# API Schema Scaffold

## app/api/schema/__init__.py

```python
from typing import Any, Generic, Optional, TypeVar

from pydantic import Field

from app.types import BaseModelWithDefaultConfig

T = TypeVar("T")


class PaginationInfo(BaseModelWithDefaultConfig):
    total: int = Field(...)
    count: int = Field(...)
    page: Optional[int] = Field(default=None)
    page_size: Optional[int] = Field(default=None)
    total_pages: Optional[int] = Field(default=None)


class SuccessResponse(BaseModelWithDefaultConfig, Generic[T]):
    success: bool = True
    message: str = Field(...)
    data: Optional[T] = Field(default=None)


class PaginatedSuccessResponse(BaseModelWithDefaultConfig, Generic[T]):
    success: bool = True
    message: str = Field(...)
    data: T
    pagination: PaginationInfo


class ErrorResponse(BaseModelWithDefaultConfig):
    success: bool = False
    message: str = Field(...)
    code: int = Field(...)
    http_status: int = Field(...)
    error: dict[str, Any] = Field(default_factory=dict)
```

## Example Request Schema

```python
# app/api/schema/item/request.py
from typing import Optional

from pydantic import Field

from app.types import BaseModelWithDefaultConfig


class CreateItemRequest(BaseModelWithDefaultConfig):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    category: str = Field(...)
    quantity: int = Field(..., ge=0)


class UpdateItemRequest(BaseModelWithDefaultConfig):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None)
    category: Optional[str] = Field(default=None)
    quantity: Optional[int] = Field(default=None, ge=0)
```

## Example Response Schema

```python
# app/api/schema/item/response.py
from app.api.schema import PaginatedSuccessResponse, SuccessResponse
from app.types.item import ItemInternal

CreateItemResponse = SuccessResponse[ItemInternal]
GetItemResponse = SuccessResponse[ItemInternal]
ListItemsResponse = PaginatedSuccessResponse[list[ItemInternal]]
UpdateItemResponse = SuccessResponse[ItemInternal]
DeleteItemResponse = SuccessResponse[None]
```

## Schema Rules

- Request schemas: NO `id` or `org_id` fields (those come from auth/path)
- Create requests: required fields use `Field(...)`, optional use `Field(default=None)`
- Update requests: ALL fields are `Optional` with `default=None`
- Response schemas: type aliases over `SuccessResponse[DomainType]`
- All schemas extend `BaseModelWithDefaultConfig` (camelCase, extra ignore)
