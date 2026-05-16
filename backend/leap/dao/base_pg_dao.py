from abc import ABC, abstractmethod
from typing import Any, Generic, List, Optional, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from leap.core.common.time import utc_now

T = TypeVar("T", bound=DeclarativeBase)


class BasePgDAO(ABC, Generic[T]):
    """Shared PostgreSQL DAO state and DTO conversion."""

    def __init__(self, model_class: type[T]) -> None:
        self.model_class = model_class

    @abstractmethod
    def _to_dto(self, orm: T) -> Any:
        """Convert an ORM instance to a domain DTO."""
        ...


class BaseReadPgDAO(BasePgDAO[T], ABC):
    """Read helpers shared by DAOs that project ORM rows into DTOs."""

    def _apply_filters(self, query: Any, filters: dict) -> Any:
        """Apply domain-specific filters to a query. Override when needed."""
        return query

    async def _get_by_id(self, session: AsyncSession, item_id: str) -> Optional[T]:
        """Return an ORM instance by primary key, or None if not found."""
        query = select(self.model_class).where(getattr(self.model_class, "id") == item_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def _get_all(
        self,
        session: AsyncSession,
        filters: Optional[dict] = None,
        limit: int = 100,
        offset: int = 0,
        order_by: Optional[Any] = None,
    ) -> List[T]:
        """Return a list of ORM instances with optional filtering and pagination."""
        query = select(self.model_class)
        if filters:
            query = self._apply_filters(query, filters)
        if order_by is not None:
            query = query.order_by(order_by)
        query = query.limit(limit).offset(offset)
        result = await session.execute(query)
        return list(result.scalars().all())

    async def _count(self, session: AsyncSession, filters: Optional[dict] = None) -> int:
        """Return the count of rows matching optional filters."""
        query = select(func.count()).select_from(self.model_class)
        if filters:
            query = self._apply_filters(query, filters)
        result = await session.execute(query)
        return result.scalar() or 0


class BaseWritePgDAO(BasePgDAO[T], ABC):
    """Write helpers shared by DAOs that manage ORM lifecycle."""

    async def _create(self, session: AsyncSession, item: T) -> T:
        """Insert a new row. Sets updated_at if present. Returns the refreshed ORM instance."""
        if hasattr(item, "updated_at"):
            setattr(item, "updated_at", utc_now())
        session.add(item)
        await session.flush()
        await session.refresh(item)
        return item

    async def _update(self, session: AsyncSession, item: T) -> T:
        """Merge and flush an ORM instance. Sets updated_at if present."""
        if hasattr(item, "updated_at"):
            setattr(item, "updated_at", utc_now())
        merged = await session.merge(item)
        await session.flush()
        await session.refresh(merged)
        return merged

    async def _delete_by_id(self, session: AsyncSession, item_id: str) -> bool:
        """Hard delete a row by primary key. Returns True if a row was deleted."""
        item = await session.get(self.model_class, item_id)
        if item is None:
            return False
        await session.delete(item)
        await session.flush()
        return True
