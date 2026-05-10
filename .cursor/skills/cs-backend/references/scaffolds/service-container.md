# Service Container Scaffold

## app/api/dependencies/service_container.py

```python
from typing import Optional

from fastapi import Depends

from app.api.dependencies.auth import get_auth_user
from app.core.abac.types import UserContext
from app.core.context.app_context import get_context_manager
from app.core.context.context_manager import ContextManager


class ServiceContainer:
    """Lazy-loading DI container. One instance per request, scoped to the authenticated user."""

    def __init__(self, context: UserContext, context_manager: ContextManager):
        self.context = context
        self.context_manager = context_manager

        # Register service slots (add new services here)
        self._item_service = None
        # self._order_service = None

    @property
    def item(self):
        if self._item_service is None:
            from app.service.item.item_service import ItemService
            self._item_service = ItemService(self.context, self.context_manager)
        return self._item_service

    # @property
    # def order(self):
    #     if self._order_service is None:
    #         from app.service.order.order_service import OrderService
    #         self._order_service = OrderService(self.context, self.context_manager)
    #     return self._order_service


async def get_service_container(
    actor: UserContext = Depends(get_auth_user),
    context_manager: ContextManager = Depends(get_context_manager),
) -> ServiceContainer:
    """FastAPI dependency — creates a request-scoped ServiceContainer."""
    return ServiceContainer(actor, context_manager)
```

## Adding a New Service

1. Add a private slot: `self._order_service = None`
2. Add a property:
   ```python
   @property
   def order(self):
       if self._order_service is None:
           from app.service.order.order_service import OrderService
           self._order_service = OrderService(self.context, self.context_manager)
       return self._order_service
   ```
3. Use in routes: `services.order.create(...)`
