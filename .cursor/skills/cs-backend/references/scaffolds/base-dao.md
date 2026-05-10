# Base DAO Scaffold

## app/dao/base_pg_dao.py

```python
from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, Type, TypeVar

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common import utc_now

T = TypeVar("T")


class BasePgDAO(ABC, Generic[T]):
    """Generic async DAO for Postgres with ABAC integration."""

    def __init__(
        self,
        context,
        context_manager,
        model_class: Type[T],
        guard=None,
    ):
        self.context = context
        self.context_manager = context_manager
        self.model_class = model_class
        self._guard = guard

    # -- ABAC --

    async def _apply_abac_filters(self, query: Select, action: str = "read") -> Select:
        if self._guard is None:
            return query
        conditions = self._guard.get_authorized_filters(self.model_class, action)
        if conditions is None:
            raise PermissionError(f"Access denied: {action} on {self.model_class.__tablename__}")
        if conditions:
            query = query.where(or_(*conditions))
        return query

    # -- Audit --

    def _set_audit_fields(self, data: dict, is_create: bool = True) -> dict:
        now = utc_now()
        user_id = getattr(self.context, "id", None)
        if is_create:
            data.setdefault("created_by", user_id)
            data.setdefault("created_at", now)
        data["modified_by"] = user_id
        data["modified_at"] = now
        return data

    # -- CRUD --

    async def _create(self, session: AsyncSession, data: dict) -> T:
        data = self._set_audit_fields(data, is_create=True)
        instance = self.model_class(**data)
        session.add(instance)
        await session.flush()
        await session.refresh(instance)
        return instance

    async def _get_by_id(self, session: AsyncSession, id_value: Any) -> Optional[T]:
        query = select(self.model_class).where(
            self.model_class.id == id_value,
            self.model_class.is_deleted == False,
        )
        query = await self._apply_abac_filters(query)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def _update(self, session: AsyncSession, instance: T, data: dict) -> T:
        data = self._set_audit_fields(data, is_create=False)
        for key, value in data.items():
            if value is not None and hasattr(instance, key):
                setattr(instance, key, value)
        await session.flush()
        await session.refresh(instance)
        return instance

    async def _delete_by_id(self, session: AsyncSession, id_value: Any) -> bool:
        instance = await self._get_by_id(session, id_value)
        if instance is None:
            return False
        await session.delete(instance)
        await session.flush()
        return True

    async def _soft_delete_by_id(self, session: AsyncSession, id_value: Any) -> bool:
        instance = await self._get_by_id(session, id_value)
        if instance is None:
            return False
        instance.is_deleted = True
        instance.modified_by = getattr(self.context, "id", None)
        instance.modified_at = utc_now()
        await session.flush()
        return True

    async def _get_all(
        self,
        session: AsyncSession,
        filters=None,
        page: int = 1,
        page_size: int = 20,
        order_by=None,
    ) -> tuple[list[T], int]:
        query = select(self.model_class).where(self.model_class.is_deleted == False)
        query = await self._apply_abac_filters(query, action="list")

        if filters:
            query = self._apply_filters(query, filters)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total = (await session.execute(count_query)).scalar() or 0

        # Ordering
        if order_by is not None:
            query = query.order_by(order_by)

        # Pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await session.execute(query)
        return list(result.scalars().all()), total

    async def _count(self, session: AsyncSession, filters=None) -> int:
        query = select(func.count()).select_from(self.model_class).where(
            self.model_class.is_deleted == False
        )
        query = await self._apply_abac_filters(query, action="list")
        if filters:
            query = self._apply_filters(query, filters)
        result = await session.execute(query)
        return result.scalar() or 0

    @abstractmethod
    def _apply_filters(self, query: Select, filters) -> Select:
        """Apply domain-specific filters. Must be implemented by subclasses."""
        ...
```

## Example Concrete DAO

```python
# app/dao/pg/item_dao.py
from typing import Optional

from app.core.common.id import generate_id
from app.dao.base_pg_dao import BasePgDAO
from app.dao.models.item import Item
from app.types.item import ItemCreate, ItemFilter, ItemInternal, ItemUpdate


class ItemDAO(BasePgDAO[Item]):
    def __init__(self, context, context_manager, guard=None):
        super().__init__(context, context_manager, Item, guard)

    def _apply_filters(self, query, filters: ItemFilter):
        if filters.category:
            query = query.where(Item.category == filters.category)
        if filters.status:
            query = query.where(Item.status == filters.status)
        if filters.search:
            query = query.where(Item.name.ilike(f"%{filters.search}%"))
        return query

    async def create_item(self, item: ItemCreate) -> ItemInternal:
        async with self.context_manager.session(self.context) as session:
            data = item.model_dump()
            data["id"] = generate_id("item")
            row = await self._create(session, data)
            return ItemInternal.model_validate(row)

    async def get_item(self, item_id: str) -> Optional[ItemInternal]:
        async with self.context_manager.session(self.context) as session:
            row = await self._get_by_id(session, item_id)
            return ItemInternal.model_validate(row) if row else None

    async def update_item(self, item_id: str, update: ItemUpdate) -> Optional[ItemInternal]:
        async with self.context_manager.session(self.context) as session:
            row = await self._get_by_id(session, item_id)
            if row is None:
                return None
            data = update.model_dump(exclude_none=True)
            updated = await self._update(session, row, data)
            return ItemInternal.model_validate(updated)

    async def delete_item(self, item_id: str) -> bool:
        async with self.context_manager.session(self.context) as session:
            return await self._soft_delete_by_id(session, item_id)

    async def list_items(
        self, filters: ItemFilter, page: int = 1, page_size: int = 20
    ) -> tuple[list[ItemInternal], int]:
        async with self.context_manager.session(self.context) as session:
            rows, total = await self._get_all(session, filters, page, page_size)
            items = [ItemInternal.model_validate(row) for row in rows]
            return items, total
```
