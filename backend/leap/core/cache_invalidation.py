"""Cross-worker game-cache invalidation via Postgres LISTEN/NOTIFY.

Each gunicorn worker holds its own in-memory game content caches (warmed by
``ServiceContainer.warm_caches``). When one worker mutates content — e.g. the admin
reset endpoint truncates and re-seeds — the others keep stale caches. We coordinate
through Postgres (the only shared runtime dependency; no Redis) instead of restarting:

- Every worker runs a :class:`CacheInvalidationListener` on a dedicated asyncpg
  connection, subscribed to ``leap_cache_invalidate``.
- A mutating worker calls :func:`emit_cache_invalidation`, which fires ``pg_notify``.
- Each listener re-runs ``warm_caches`` on receipt, refreshing without a restart.

The listener owns a connection separate from the SQLAlchemy pool because a ``LISTEN``
connection must stay open indefinitely, which a pooled session cannot do.
"""

import asyncio
from typing import Optional, Set

import asyncpg
from sqlalchemy import text

from leap.core.common.logger import get_logger
from leap.core.context_manager import ContextManager
from leap.service.container import ServiceContainer

CACHE_INVALIDATION_CHANNEL = "leap_cache_invalidate"

logger = get_logger(__name__)


def _to_asyncpg_dsn(connection_string: str) -> str:
    """Convert a SQLAlchemy ``postgresql+asyncpg://`` URL to a libpq DSN for asyncpg."""
    return connection_string.replace("+asyncpg", "", 1)


async def emit_cache_invalidation(context_manager: ContextManager) -> None:
    """Broadcast a cache-invalidation signal to every worker via Postgres NOTIFY.

    Delivered when the session commits (on clean exit of ``session()``).
    """
    async with context_manager.session() as session:
        await session.execute(
            text("SELECT pg_notify(:channel, '')"),
            {"channel": CACHE_INVALIDATION_CHANNEL},
        )


class CacheInvalidationListener:
    """Per-worker background listener that refreshes game caches on NOTIFY.

    Reconnects automatically if the dedicated connection drops, so a transient DB
    blip during the event doesn't permanently silence a worker.
    """

    def __init__(
        self,
        context_manager: ContextManager,
        container: ServiceContainer,
        connection_string: str,
        reconnect_delay: float = 5.0,
    ) -> None:
        self._context_manager = context_manager
        self._container = container
        self._dsn = _to_asyncpg_dsn(connection_string)
        self._reconnect_delay = reconnect_delay
        self._stopped = False
        self._task: Optional[asyncio.Task] = None
        self._conn: Optional[asyncpg.Connection] = None
        self._refresh_lock = asyncio.Lock()
        self._refresh_tasks: Set[asyncio.Task] = set()

    async def start(self) -> None:
        """Launch the listener supervisor task. Call once during lifespan startup."""
        self._stopped = False
        self._task = asyncio.create_task(self._run(), name="cache-invalidation-listener")

    async def stop(self) -> None:
        """Cancel the listener and close its connection. Call during lifespan shutdown."""
        self._stopped = True
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    def _on_notify(self, connection: object, pid: int, channel: str, payload: str) -> None:
        """asyncpg callback (sync): schedule an async refresh on the running loop."""
        task = asyncio.create_task(self._refresh())
        self._refresh_tasks.add(task)
        task.add_done_callback(self._refresh_tasks.discard)

    async def _refresh(self) -> None:
        """Re-warm every game cache. Serialized so overlapping NOTIFYs coalesce."""
        async with self._refresh_lock:
            try:
                async with self._context_manager.session() as session:
                    await self._container.warm_caches(session)
                logger.info("Game caches refreshed from cache-invalidation NOTIFY")
            except Exception as exc:
                logger.error("Cache refresh failed", error=str(exc))

    async def _run(self) -> None:
        while not self._stopped:
            conn: Optional[asyncpg.Connection] = None
            try:
                conn = await asyncpg.connect(self._dsn)
                self._conn = conn
                await conn.add_listener(CACHE_INVALIDATION_CHANNEL, self._on_notify)
                logger.info(
                    "Cache-invalidation listener connected",
                    channel=CACHE_INVALIDATION_CHANNEL,
                )
                while not self._stopped and not conn.is_closed():
                    await asyncio.sleep(5)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.warning(
                    "Cache-invalidation listener error; will reconnect",
                    error=str(exc),
                )
            finally:
                self._conn = None
                if conn is not None and not conn.is_closed():
                    try:
                        await conn.remove_listener(CACHE_INVALIDATION_CHANNEL, self._on_notify)
                    except Exception:
                        pass
                    try:
                        await conn.close()
                    except Exception:
                        pass

            if not self._stopped:
                await asyncio.sleep(self._reconnect_delay)
