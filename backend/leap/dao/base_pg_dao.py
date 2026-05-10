from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import DeclarativeBase

from leap.core.common.time import utc_now
from leap.core.context_manager import ContextManager

T = TypeVar("T", bound=DeclarativeBase)


class BasePgDAO(ABC, Generic[T]):
    """Base DAO for PostgreSQL operations using SQLAlchemy async sessions.

    Subclasses must implement _to_orm, _to_dto, and _apply_filters.
    All public methods return plain dicts or lists of dicts — never ORM instances.
    All database access goes through context_manager.session().
    """

    def __init__(self, context_manager: ContextManager, model_class: type[T]) -> None:
        self.context_manager = context_manager
        self.model_class = model_class

    @abstractmethod
    def _to_orm(self, data: dict) -> T:
        """Build an ORM instance from a plain dict."""
        ...

    @abstractmethod
    def _to_dto(self, orm: T) -> dict:
        """Convert an ORM instance to a plain dict."""
        ...

    @abstractmethod
    def _apply_filters(self, query: Any, filters: dict) -> Any:
        """Apply domain-specific filters to a query. Always return the query."""
        ...

    async def _create(self, item: T) -> T:
        """Insert a new row. Sets updated_at if present. Returns the refreshed ORM instance."""
        async with self.context_manager.session() as session:
            if hasattr(item, "updated_at"):
                setattr(item, "updated_at", utc_now())
            session.add(item)
            await session.flush()
            await session.refresh(item)
            return item

    async def _get_by_id(self, item_id: str) -> Optional[T]:
        """Return an ORM instance by primary key, or None if not found."""
        async with self.context_manager.session() as session:
            query = select(self.model_class).where(
                getattr(self.model_class, "id") == item_id
            )
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def _get_all(
        self,
        filters: Optional[dict] = None,
        limit: int = 100,
        offset: int = 0,
        order_by: Optional[Any] = None,
    ) -> List[T]:
        """Return a list of ORM instances with optional filtering and pagination."""
        async with self.context_manager.session() as session:
            query = select(self.model_class)
            if filters:
                query = self._apply_filters(query, filters)
            if order_by is not None:
                query = query.order_by(order_by)
            query = query.limit(limit).offset(offset)
            result = await session.execute(query)
            return list(result.scalars().all())

    async def _count(self, filters: Optional[dict] = None) -> int:
        """Return the count of rows matching optional filters."""
        async with self.context_manager.session() as session:
            query = select(func.count()).select_from(self.model_class)
            if filters:
                query = self._apply_filters(query, filters)
            result = await session.execute(query)
            return result.scalar() or 0

    async def _update(self, item: T) -> T:
        """Merge and flush an ORM instance. Sets updated_at if present."""
        async with self.context_manager.session() as session:
            if hasattr(item, "updated_at"):
                setattr(item, "updated_at", utc_now())
            merged = await session.merge(item)
            await session.flush()
            await session.refresh(merged)
            return merged

    async def _delete_by_id(self, item_id: str) -> bool:
        """Hard delete a row by primary key. Returns True if a row was deleted."""
        async with self.context_manager.session() as session:
            item = await session.get(self.model_class, item_id)
            if item is None:
                return False
            await session.delete(item)
            await session.flush()
            return True
