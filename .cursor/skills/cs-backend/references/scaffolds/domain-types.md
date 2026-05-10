# Domain Types (DTO) Scaffold

## app/types/__init__.py

```python
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


def use_default_config(**kwargs) -> ConfigDict:
    base_config = {
        "populate_by_name": True,
        "alias_generator": to_camel,
        "extra": "ignore",
        "use_enum_values": True,
    }
    base_config.update(kwargs)
    return ConfigDict(**base_config)


class BaseModelWithDefaultConfig(BaseModel):
    model_config = use_default_config()


class OrgMixin(BaseModelWithDefaultConfig):
    org_id: Optional[str] = Field(default=None)


class AuditMixin(BaseModelWithDefaultConfig):
    created_by: Optional[str] = Field(default=None)
    created_at: Optional[str] = Field(default=None)
    modified_by: Optional[str] = Field(default=None)
    modified_at: Optional[str] = Field(default=None)
    is_deleted: Optional[bool] = Field(default=None)
```

## Example Domain Types

```python
# app/types/item.py
from enum import Enum
from typing import Optional

from pydantic import Field

from app.types import BaseModelWithDefaultConfig


class ItemCategory(str, Enum):
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    FOOD = "food"
    OTHER = "other"


class ItemBase(BaseModelWithDefaultConfig):
    """Shared fields."""
    name: str = Field(...)
    description: Optional[str] = Field(default=None)
    category: ItemCategory = Field(...)
    quantity: int = Field(..., ge=0)


class ItemCreate(ItemBase):
    """Service → DAO: adds org scoping."""
    org_id: str = Field(...)


class ItemUpdate(BaseModelWithDefaultConfig):
    """Partial update — all fields optional."""
    name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    category: Optional[ItemCategory] = Field(default=None)
    quantity: Optional[int] = Field(default=None, ge=0)


class ItemInternal(ItemBase):
    """Full record from database."""
    id: str = Field(...)
    org_id: str = Field(...)


class ItemFilter(BaseModelWithDefaultConfig):
    """Query filters for list operations."""
    category: Optional[ItemCategory] = Field(default=None)
    status: Optional[str] = Field(default=None)
    search: Optional[str] = Field(default=None)
```

## Pattern Summary

| Class | Inherits | Fields | Used By |
|-------|----------|--------|---------|
| `Base` | `BaseModelWithDefaultConfig` | Common domain fields | Parent of Create/Internal |
| `Create` | `Base` | Base + `org_id` | Service passes to DAO |
| `Update` | `BaseModelWithDefaultConfig` | All optional | Service passes to DAO |
| `Internal` | `Base` | Base + `id` + `org_id` | DAO returns, route responds |
| `Filter` | `BaseModelWithDefaultConfig` | Optional query criteria | Route → Service → DAO |
