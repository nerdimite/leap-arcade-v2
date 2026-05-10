"""
Base database provider for org-aware operations.
"""

from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession


class BaseDatabaseProvider(ABC):
    """Abstract base class for database providers."""

    @abstractmethod
    async def get_session(self) -> AsyncSession:
        """Get database session."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check database health."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close database connection."""
        pass
