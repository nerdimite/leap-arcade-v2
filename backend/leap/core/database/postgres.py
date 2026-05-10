from typing import Any, Dict, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from leap.core.database.base_database import BaseDatabaseProvider


class PostgresProvider(BaseDatabaseProvider):
    """Manages the SQLAlchemy async engine and session factory for PostgreSQL."""

    def __init__(self, connection_string: str, connection_settings: Dict[str, Any]) -> None:
        self.connection_string = connection_string
        self.connection_settings = connection_settings
        self._engine: Optional[AsyncEngine] = None
        self._sessionmaker: Optional[async_sessionmaker] = None

    async def _ensure_engine(self) -> None:
        """Lazily create the engine and sessionmaker on first use."""
        if self._engine is None:
            self._engine = create_async_engine(
                self.connection_string,
                **self.connection_settings,
            )
            self._sessionmaker = async_sessionmaker(
                bind=self._engine,
                expire_on_commit=False,
                class_=AsyncSession,
            )

    async def get_session(self) -> AsyncSession:
        """Return a new async database session."""
        await self._ensure_engine()
        if self._sessionmaker is None:
            raise RuntimeError("Sessionmaker not initialized.")
        return self._sessionmaker()

    async def health_check(self) -> bool:
        """Check database connectivity by running SELECT 1."""
        try:
            async with await self.get_session() as session:
                await session.execute(text("SELECT 1"))
                return True
        except Exception:
            return False

    async def close(self) -> None:
        """Dispose the engine and reset state."""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._sessionmaker = None
