from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from leap.config.settings import Settings
from leap.core.database.postgres import PostgresProvider


class ContextManager:
    """Owns the database connection lifecycle for the application.

    Created once at startup and stored on app.state.
    Pass into services and DAOs via dependency injection.
    Call initialize() before use and close() on shutdown.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._postgres: PostgresProvider | None = None

    async def initialize(self) -> None:
        """Create the database engine and session factory. Call once at startup."""
        self._postgres = PostgresProvider(
            connection_string=self._settings.POSTGRES_CONNECTION_STRING,
            connection_settings={
                "pool_size": 5,
                "max_overflow": 10,
                "pool_timeout": 30,
                "pool_recycle": 1800,
                "pool_pre_ping": True,
                "echo": self._settings.ENVIRONMENT == "development",
            },
        )

    async def close(self) -> None:
        """Dispose the database engine. Call on shutdown."""
        if self._postgres:
            await self._postgres.close()
            self._postgres = None

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Yield a database session. Commits on clean exit, rolls back on exception."""
        if self._postgres is None:
            raise RuntimeError("ContextManager not initialized. Call initialize() first.")
        async with await self._postgres.get_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def health_check(self) -> bool:
        """Check live database connectivity. Used by GET /health."""
        if self._postgres is None:
            return False
        return await self._postgres.health_check()
