# Dependency Injection

## Overview

The DI system has two tiers:
1. **FastAPI `Depends()` chain** — resolves auth user and infrastructure context
2. **`ServiceContainer`** — lazy-initializing container that holds all domain services

## Request Lifecycle

```
HTTP Request
  → get_auth_user(token) → UserContext
  → get_context_manager() → ContextManager (singleton)
  → get_service_container(user, ctx_mgr) → ServiceContainer
  → route handler accesses services.domain.method()
```

## ServiceContainer Pattern

The container is created **per-request**, scoped to the authenticated user. Services are lazily instantiated on first property access:

```python
class ServiceContainer:
    def __init__(self, context: UserContext, context_manager: ContextManager):
        self.context = context
        self.context_manager = context_manager
        self._item_service: Optional[ItemService] = None

    @property
    def item(self) -> ItemService:
        if self._item_service is None:
            self._item_service = ItemService(self.context, self.context_manager)
        return self._item_service
```

**Why lazy?** A request to `/items` should not instantiate `OrderService`, `InvoiceService`, etc. Only the accessed service is created.

## Dependency Chain

```python
async def get_service_container(
    actor: UserContext = Depends(get_auth_user),
    context_manager: ContextManager = Depends(get_context_manager),
) -> ServiceContainer:
    return ServiceContainer(actor, context_manager)
```

- `get_auth_user` — decodes JWT, builds `UserContext` (or `None` for public endpoints)
- `get_context_manager` — retrieves the singleton from `AppContext`
- `get_service_container` — creates a fresh container scoped to this user

## Route Usage

```python
@router.post("/items", response_model=SuccessResponse[ItemInternal])
async def create_item(
    body: CreateItemRequest,
    services: ServiceContainer = Depends(get_service_container),
):
    result = await services.item.create(body)
    return SuccessResponse(message="Item created", data=result)
```

## Adding a New Service

1. Create the service class extending `BaseService`
2. Add a private attribute and property to `ServiceContainer`:
   ```python
   self._order_service: Optional[OrderService] = None

   @property
   def order(self) -> OrderService:
       if self._order_service is None:
           self._order_service = OrderService(self.context, self.context_manager)
       return self._order_service
   ```
3. Use in routes: `services.order.create(...)`

## ContextManager

The `ContextManager` is the infrastructure provider factory. It lazily initializes and holds:
- **PostgresProvider** — async SQLAlchemy engine + session factory
- **PolicyProvider** — ABAC policy loader
- Additional providers (S3, cache, external APIs) as needed

```python
class ContextManager:
    async def get_postgres_provider(self) -> PostgresProvider: ...

    @asynccontextmanager
    async def session(self, context: UserContext):
        provider = await self.get_postgres_provider()
        async with await provider.get_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
```

The `session()` context manager auto-commits on success and rolls back on exception. DAOs use it via `self.context_manager.session(self.context)`.
