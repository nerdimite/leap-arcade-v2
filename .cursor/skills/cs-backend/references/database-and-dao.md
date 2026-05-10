# Database & DAO Patterns

## Database Provider

Abstract base with async interface:

```python
class BaseDatabaseProvider(ABC):
    @abstractmethod
    async def get_session(self) -> AsyncSession: ...
    @abstractmethod
    async def health_check(self) -> bool: ...
    @abstractmethod
    async def close(self) -> None: ...
```

Concrete `PostgresProvider` uses `create_async_engine` + `async_sessionmaker`:

```python
class PostgresProvider(BaseDatabaseProvider):
    def __init__(self, connection_string: str, **pool_kwargs):
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker] = None
        self._connection_string = connection_string
        self._pool_kwargs = pool_kwargs

    async def _ensure_engine(self):
        if self._engine is None:
            self._engine = create_async_engine(
                self._connection_string,
                pool_size=self._pool_kwargs.get("pool_size", 5),
                max_overflow=self._pool_kwargs.get("max_overflow", 10),
            )
            self._session_factory = async_sessionmaker(
                self._engine, class_=AsyncSession, expire_on_commit=False
            )

    async def get_session(self) -> AsyncSession:
        await self._ensure_engine()
        return self._session_factory()
```

## Session Management

`ContextManager.session()` provides auto-commit/rollback:

```python
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

DAOs use it: `async with self.context_manager.session(self.context) as session:`

## Model Hierarchy

Three-tier SQLAlchemy model base:

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class AuditBase(Base):
    __abstract__ = True
    created_by: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=func.now())
    modified_by: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    modified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

class OrgBase(AuditBase):
    __abstract__ = True
    org_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
```

**Choose your base:**
- `Base` — no audit, no org scoping
- `AuditBase` — audit fields + soft delete, no org scoping
- `OrgBase` — audit + soft delete + org isolation (multi-tenant)

## Model Patterns

```python
class Slot(OrgBase):
    __tablename__ = "slots"
    __table_args__ = (
        Index("ix_slots_schedule_date", "schedule_id", "date"),
        Index("ix_slots_practitioner_status", "practitioner_fhir_id", "status"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True)
    schedule_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    status: Mapped[str] = mapped_column(slot_status_enum, default="free")
    version: Mapped[int] = mapped_column(Integer, default=1)  # Optimistic locking
```

Key patterns:
- Composite indexes in `__table_args__`
- Enums via `sqlalchemy.Enum` with explicit values
- JSONB columns for flexible data
- Optimistic locking via `version` field
- Always use `Mapped[T]` with `mapped_column()` (SQLAlchemy 2.0 style)

## Model Registry

**Critical:** Every model must be imported in `dao/models/__init__.py`:

```python
from .base import AuditBase, Base, OrgBase
from .slot import Slot
from .schedule import PractitionerSchedule
```

Without this, Alembic `--autogenerate` won't detect the model.

## Base DAO (BasePgDAO)

Generic DAO parameterized on model type:

```python
class BasePgDAO(Generic[T]):
    def __init__(self, context, context_manager, model_class: Type[T], guard=None):
        self.context = context
        self.context_manager = context_manager
        self.model_class = model_class
        self._guard = guard
```

### Provided CRUD Methods (all protected)

| Method | Purpose |
|--------|---------|
| `_create(data)` | Insert row, set audit fields |
| `_get_by_id(id)` | Get by PK with ABAC filter |
| `_update(id, data)` | Partial update, set modified_by/at |
| `_delete_by_id(id)` | Hard delete |
| `_soft_delete_by_id(id)` | Set is_deleted=True |
| `_restore_by_id(id)` | Set is_deleted=False |
| `_get_all(filters, page, page_size, order_by)` | List with ABAC, pagination, ordering |
| `_count(filters)` | Count with ABAC filter |
| `_exists(filters)` | Check existence |

### ABAC Integration

Every query passes through `_apply_abac_filters()`:

```python
async def _apply_abac_filters(self, query, action="read"):
    if self._guard is None:
        return query
    conditions = self._guard.get_authorized_filters(self.model_class, action)
    if conditions is None:
        raise PermissionError("Access denied")
    if conditions:
        query = query.where(or_(*conditions))
    return query
```

### Abstract Method

Subclasses must implement:

```python
@abstractmethod
def _apply_filters(self, query, filters) -> Select:
    """Apply domain-specific filters to the query."""
```

## Concrete DAO Pattern

```python
class SlotDAO(BasePgDAO[Slot]):
    def __init__(self, context, context_manager, guard=None):
        super().__init__(context, context_manager, Slot, guard)

    def _apply_filters(self, query, filters: SlotFilter):
        if filters.schedule_id:
            query = query.where(Slot.schedule_id == filters.schedule_id)
        if filters.status:
            query = query.where(Slot.status == filters.status)
        return query

    async def create_slot(self, slot: SlotCreate) -> SlotInternal:
        async with self.context_manager.session(self.context) as session:
            data = slot.model_dump()
            data["id"] = generate_id("slot")
            row = await self._create(session, data)
            return SlotInternal.model_validate(row)
```

**Key pattern:** Public methods handle Pydantic ↔ ORM conversion. Protected `_create`/`_get_by_id` work with raw dicts and ORM objects.

## Alembic Migrations

```bash
# Generate migration
uv run alembic revision --autogenerate -m "add_slots_table"

# Apply migrations
uv run alembic upgrade head

# Rollback one step
uv run alembic downgrade -1
```

`alembic/env.py` must:
1. Import all models: `from app.dao.models import *`
2. Set `target_metadata = Base.metadata`
3. Use async engine for online migrations
