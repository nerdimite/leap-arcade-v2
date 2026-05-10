# API Layer

## Router Pattern

Each domain has one router file:

```python
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/items", tags=["Items"])

@router.post("", response_model=SuccessResponse[ItemInternal], status_code=201)
async def create_item(
    body: CreateItemRequest,
    services: ServiceContainer = Depends(get_service_container),
):
    result = await services.item.create(body)
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
    services: ServiceContainer = Depends(get_service_container),
):
    items, pagination = await services.item.list(page=page, page_size=page_size)
    return PaginatedSuccessResponse(
        message="Items retrieved",
        data=items,
        pagination=pagination,
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

## Router Registration

All routers aggregate in `api/routes/__init__.py`:

```python
from fastapi import APIRouter
from .item_router import router as item_router
from .order_router import router as order_router

api_router = APIRouter()
api_router.include_router(item_router)
api_router.include_router(order_router)
```

Then mounted in `main.py`:
```python
app.include_router(api_router, prefix=settings.API_VERSION_PREFIX)
```

## Response Envelope

All responses use a standard envelope:

### Success
```json
{
  "success": true,
  "message": "Item created",
  "data": { ... }
}
```

### Paginated
```json
{
  "success": true,
  "message": "Items retrieved",
  "data": [...],
  "pagination": {
    "total": 50,
    "count": 20,
    "page": 1,
    "pageSize": 20,
    "totalPages": 3
  }
}
```

### Error
```json
{
  "success": false,
  "message": "Item not found",
  "code": 4100,
  "httpStatus": 404,
  "error": { "item_id": "item_123" }
}
```

## Request Schemas

```python
class CreateItemRequest(BaseModelWithDefaultConfig):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None)
    quantity: int = Field(..., ge=0)

class UpdateItemRequest(BaseModelWithDefaultConfig):
    name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    quantity: Optional[int] = Field(default=None, ge=0)
```

**Rules:**
- Request schemas have NO `id` or `org_id` — those come from auth/path params
- `Create` uses `Field(...)` for required fields
- `Update` makes everything `Optional` with `default=None`
- Always use PATCH for updates, not PUT

## Response Schemas

```python
# Type aliases for route response_model
CreateItemResponse = SuccessResponse[ItemInternal]
GetItemResponse = SuccessResponse[ItemInternal]
ListItemsResponse = PaginatedSuccessResponse[list[ItemInternal]]
```

## Global Exception Handlers

Registered in `main.py`, they catch:

| Exception | Status | Handler |
|-----------|--------|---------|
| `RequestValidationError` | 422 | Sanitizes Pydantic errors |
| `BaseServiceException` | varies | Calls `exc.to_dict()` |
| `PermissionError` | 403 | ABAC denial |
| `HTTPException` | varies | Standard HTTP errors |
| `Exception` | 500 | Catch-all with stack trace logging |

## Route Design Rules

1. **PATCH not PUT** for updates
2. **Plural nouns** for resource paths: `/items`, `/orders`
3. **Nested resources** via path: `/orders/{order_id}/items`
4. **Query params** for filtering/pagination on list endpoints
5. **Status code 201** for creation endpoints
6. **No auth** endpoints: don't use `get_service_container` dependency
