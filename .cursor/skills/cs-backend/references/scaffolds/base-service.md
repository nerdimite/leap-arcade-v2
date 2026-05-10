# Base Service Scaffold

## app/service/base_service.py

```python
from abc import ABC
from typing import Optional

from app.core.context.app_context import get_app_context
from app.core.context.context_manager import ContextManager


class BaseService(ABC):
    """Base service with ABAC guard integration."""

    def __init__(self, context, context_manager: ContextManager):
        self.context = context
        self.context_manager = context_manager
        self.logger = get_app_context().logger
        self._guard = None

    @property
    def guard(self):
        if self._guard is None:
            from app.core.abac import AccessControlGuard
            policy_provider = self.context_manager.get_policy_provider()
            self._guard = AccessControlGuard(self.context, policy_provider)
        return self._guard

    @property
    def user_id(self) -> str:
        return self.context.id

    @property
    def org_id(self) -> str:
        return self.context.org.id

    @property
    def user_email(self) -> Optional[str]:
        return self.context.user.email

    @property
    def current_org_roles(self) -> list[str]:
        return self.context.roles
```

## Example Domain Service

```python
# app/service/item/item_service.py
from typing import Optional

from app.api.schema import PaginationInfo
from app.core.common.pagination import calculate_total_pages, validate_page_number
from app.core.context.context_manager import ContextManager
from app.dao.pg.item_dao import ItemDAO
from app.service.base_service import BaseService
from app.service.item.item_exceptions import ItemNotFoundException
from app.types.item import ItemCreate, ItemFilter, ItemInternal, ItemUpdate


class ItemService(BaseService):
    def __init__(self, context, context_manager: ContextManager):
        super().__init__(context, context_manager)
        self.item_dao = ItemDAO(context, context_manager, guard=self.guard)

    async def create(self, name: str, category: str, **kwargs) -> ItemInternal:
        self.guard.authorize_create("items", {"org_id": self.org_id})

        item_data = ItemCreate(
            org_id=self.org_id,
            name=name,
            category=category,
            **kwargs,
        )
        item = await self.item_dao.create_item(item_data)
        self.logger.info("item_created", item_id=item.id)
        return item

    async def get_by_id(self, item_id: str) -> ItemInternal:
        item = await self.item_dao.get_item(item_id)
        if item is None:
            raise ItemNotFoundException(item_id)
        return item

    async def update(self, item_id: str, update: ItemUpdate) -> ItemInternal:
        item = await self.item_dao.update_item(item_id, update)
        if item is None:
            raise ItemNotFoundException(item_id)
        self.logger.info("item_updated", item_id=item.id)
        return item

    async def delete(self, item_id: str) -> None:
        deleted = await self.item_dao.delete_item(item_id)
        if not deleted:
            raise ItemNotFoundException(item_id)
        self.logger.info("item_deleted", item_id=item_id)

    async def list(
        self,
        filters: Optional[ItemFilter] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ItemInternal], PaginationInfo]:
        if filters is None:
            filters = ItemFilter()

        items, total = await self.item_dao.list_items(filters, page, page_size)
        validate_page_number(page, page_size, total)

        pagination = PaginationInfo(
            total=total,
            count=len(items),
            page=page,
            page_size=page_size,
            total_pages=calculate_total_pages(total, page_size),
        )
        return items, pagination
```
