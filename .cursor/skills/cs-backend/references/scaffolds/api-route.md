# API Router Scaffold

## app/api/routes/item_router.py

```python
from fastapi import APIRouter, Depends, Query

from app.api.dependencies.service_container import ServiceContainer, get_service_container
from app.api.schema import PaginatedSuccessResponse, PaginationInfo, SuccessResponse
from app.api.schema.item.request import CreateItemRequest, UpdateItemRequest
from app.types.item import ItemFilter, ItemInternal

router = APIRouter(prefix="/items", tags=["Items"])


@router.post("", response_model=SuccessResponse[ItemInternal], status_code=201)
async def create_item(
    body: CreateItemRequest,
    services: ServiceContainer = Depends(get_service_container),
):
    result = await services.item.create(
        name=body.name,
        category=body.category,
        description=body.description,
        quantity=body.quantity,
    )
    return SuccessResponse(message="Item created", data=result)


@router.get("/{item_id}", response_model=SuccessResponse[ItemInternal])
async def get_item(
    item_id: str,
    services: ServiceContainer = Depends(get_service_container),
):
    result = await services.item.get_by_id(item_id)
    return SuccessResponse(message="Item retrieved", data=result)


@router.get("", response_model=PaginatedSuccessResponse[list[ItemInternal]])
async def list_items(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    category: str | None = Query(default=None),
    search: str | None = Query(default=None),
    services: ServiceContainer = Depends(get_service_container),
):
    filters = ItemFilter(category=category, search=search)
    items, pagination = await services.item.list(
        filters=filters, page=page, page_size=page_size
    )
    return PaginatedSuccessResponse(
        message="Items retrieved", data=items, pagination=pagination
    )


@router.patch("/{item_id}", response_model=SuccessResponse[ItemInternal])
async def update_item(
    item_id: str,
    body: UpdateItemRequest,
    services: ServiceContainer = Depends(get_service_container),
):
    result = await services.item.update(item_id, body)
    return SuccessResponse(message="Item updated", data=result)


@router.delete("/{item_id}", response_model=SuccessResponse[None])
async def delete_item(
    item_id: str,
    services: ServiceContainer = Depends(get_service_container),
):
    await services.item.delete(item_id)
    return SuccessResponse(message="Item deleted", data=None)
```

## app/api/routes/__init__.py

```python
from fastapi import APIRouter

from .item_router import router as item_router

api_router = APIRouter()
api_router.include_router(item_router)

# Add new routers:
# from .order_router import router as order_router
# api_router.include_router(order_router)
```

## Route Design Rules

- **PATCH not PUT** for updates (partial update semantics)
- **Plural nouns** for paths: `/items`, `/orders`
- **201 status** for creation endpoints
- **Query params** for filtering and pagination on list endpoints
- **Path params** for resource identifiers
- Inject `ServiceContainer` via `Depends(get_service_container)`
- Wrap results in `SuccessResponse[T]` or `PaginatedSuccessResponse[T]`
