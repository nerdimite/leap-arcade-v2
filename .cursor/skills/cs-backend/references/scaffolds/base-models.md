# SQLAlchemy Model Scaffold

## app/dao/models/base.py

```python
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Shared base class for all ORM models."""
    pass


class AuditBase(Base):
    """Base with audit tracking and soft delete."""
    __abstract__ = True

    created_by: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    modified_by: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    modified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)


class OrgBase(AuditBase):
    """Extends AuditBase with org-scoped multi-tenancy."""
    __abstract__ = True

    org_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
```

## app/dao/models/__init__.py

```python
# CRITICAL: Import every model here for Alembic autogenerate detection.
from .base import AuditBase, Base, OrgBase

# Add new models below:
# from .item import Item
# from .order import Order
```

## Example Domain Model

```python
# app/dao/models/item.py
from datetime import datetime
from typing import Optional

from sqlalchemy import Date, Enum, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import OrgBase

item_status_enum = Enum("active", "archived", "deleted", name="item_status", create_type=True)


class Item(OrgBase):
    __tablename__ = "items"
    __table_args__ = (
        Index("ix_items_org_status", "org_id", "status"),
        Index("ix_items_category", "category"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(item_status_enum, default="active")
    version: Mapped[int] = mapped_column(Integer, default=1)
```

## Notes

- Use `Mapped[T]` with `mapped_column()` (SQLAlchemy 2.0 typed style)
- Define composite indexes in `__table_args__`
- Use `Enum(...)` for constrained string columns
- Add `version` field for optimistic locking where needed
- Always import new models in `__init__.py`
