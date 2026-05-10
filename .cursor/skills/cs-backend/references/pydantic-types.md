# Pydantic Types (DTOs)

## Base Configuration

All models extend `BaseModelWithDefaultConfig`:

```python
from pydantic import BaseModel, ConfigDict
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
```

This gives:
- **camelCase aliases** for JSON serialization/deserialization
- **Extra fields ignored** (tolerant parsing)
- **Enum values** serialized (not enum names)

## Four-Class Pattern

Every domain entity follows this pattern:

```python
# types/<domain>/item.py

class ItemBase(BaseModelWithDefaultConfig):
    """Shared fields between create and internal representations."""
    name: str = Field(...)
    description: Optional[str] = Field(default=None)
    quantity: int = Field(..., ge=0)
    category: ItemCategory = Field(...)

class ItemCreate(ItemBase):
    """For creating a new item — adds org scoping."""
    org_id: str = Field(...)

class ItemUpdate(BaseModelWithDefaultConfig):
    """For partial updates — all fields optional."""
    name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    quantity: Optional[int] = Field(default=None, ge=0)
    category: Optional[ItemCategory] = Field(default=None)

class ItemInternal(ItemBase):
    """Full representation from the database."""
    id: str = Field(...)
    org_id: str = Field(...)

class ItemFilter(BaseModelWithDefaultConfig):
    """Query filter criteria for list operations."""
    category: Optional[ItemCategory] = Field(default=None)
    min_quantity: Optional[int] = Field(default=None)
    search: Optional[str] = Field(default=None)
```

## Why Four Classes?

| Class | Used By | Contains |
|-------|---------|----------|
| `Base` | Shared | Common fields |
| `Create` | Service → DAO | Base + org_id (added by service) |
| `Update` | Service → DAO | All optional (PATCH semantics) |
| `Internal` | DAO → Service → Route | Base + id + org_id (full record) |
| `Filter` | Route → DAO | Optional filter criteria |

## Mixins

For audit and org fields, use mixins:

```python
class OrgMixin(BaseModelWithDefaultConfig):
    org_id: Optional[str] = Field(default=None)

class AuditMixin(BaseModelWithDefaultConfig):
    created_by: Optional[str] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    modified_by: Optional[str] = Field(default=None)
    modified_at: Optional[datetime] = Field(default=None)
    is_deleted: Optional[bool] = Field(default=None)
```

## Rules

1. **Optional fields always have `default=None`** — Never `Optional[str]` without default
2. **Use `Field(...)` for required fields** — Makes intent explicit
3. **Update classes are flat** — Don't inherit from Base (different optionality)
4. **Request schemas ≠ Domain types** — Requests have no `id`/`org_id`; domain types do
5. **Enums use string values** — `use_enum_values=True` serializes `"active"` not `Status.ACTIVE`

## Enum Pattern

```python
from enum import Enum

class ItemCategory(str, Enum):
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    FOOD = "food"

class SlotStatus(str, Enum):
    FREE = "free"
    BUSY = "busy"
    BLOCKED = "blocked"
```

Always extend `str, Enum` for JSON serialization compatibility.

## Conversion: ORM ↔ Pydantic

```python
# ORM → Pydantic (in DAO)
item_internal = ItemInternal.model_validate(orm_object)

# Pydantic → dict (for DAO create/update)
data = item_create.model_dump()
data["id"] = generate_id("item")
```
