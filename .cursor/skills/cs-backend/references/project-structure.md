# Project Structure

## Directory Layout

```
project_root/
├── pyproject.toml                 # Dependencies, scripts, tool config
├── alembic.ini                    # Migration configuration
├── alembic/                       # Database migrations
│   ├── env.py                     # Alembic env (async engine setup)
│   └── versions/                  # Migration scripts
├── .env.example                   # Env template (committed)
├── .env                           # Env values (gitignored)
├── app/                           # Main package
│   ├── main.py                    # FastAPI app, lifespan, middleware, exception handlers
│   ├── config/
│   │   ├── settings.py            # pydantic-settings BaseSettings
│   │   ├── constants.py           # Domain constants, URIs, magic strings
│   │   ├── errors.py              # ErrorCodes, ErrorHttpStatus, ErrorMessages
│   │   └── policies.json          # ABAC policy definitions
│   ├── core/                      # Infrastructure & cross-cutting concerns
│   │   ├── abac/                  # Access control engine
│   │   │   ├── types.py           # UserContext, ABACAction, policy models
│   │   │   ├── guard.py           # AccessControlGuard (entry point)
│   │   │   ├── compiler.py        # JSON rules → SQLAlchemy WHERE clauses
│   │   │   ├── evaluator.py       # JSON rules → in-memory evaluation
│   │   │   └── providers.py       # JSONPolicyProvider (loads policies.json)
│   │   ├── auth/                  # Auth provider client (e.g., Clerk)
│   │   ├── common/                # Shared utilities
│   │   │   ├── logger.py          # structlog JSON logging
│   │   │   ├── pagination.py      # Page validation, offset calc
│   │   │   ├── sanitize.py        # Input sanitization
│   │   │   ├── timezone.py        # UTC/local time helpers
│   │   │   └── id/                # ID generation (snowflake, short, domain-specific)
│   │   ├── context/               # Application lifecycle
│   │   │   ├── app_context.py     # Global singleton (settings, logger, state)
│   │   │   └── context_manager.py # Infrastructure providers (DB, cache, storage)
│   │   └── database/              # Database connection provider
│   │       ├── base_database.py   # Abstract provider interface
│   │       └── postgres_provider.py # Async SQLAlchemy engine + session factory
│   ├── api/
│   │   ├── dependencies/          # FastAPI dependency injection
│   │   │   ├── auth.py            # JWT verification → UserContext
│   │   │   └── service_container.py # Lazy service container
│   │   ├── routes/                # Domain routers
│   │   │   ├── __init__.py        # Aggregates all routers into api_router
│   │   │   └── <domain>_router.py # One router per domain
│   │   └── schema/                # API request/response models
│   │       └── <domain>/
│   │           ├── request.py     # Request bodies
│   │           └── response.py    # Response type aliases
│   ├── dao/
│   │   ├── base_pg_dao.py         # Generic async DAO with ABAC
│   │   ├── models/                # SQLAlchemy ORM models
│   │   │   ├── __init__.py        # CRITICAL: imports all models (Alembic detection)
│   │   │   ├── base.py            # Base, AuditBase, OrgBase
│   │   │   └── <domain>.py        # Domain model
│   │   └── pg/                    # Concrete Postgres DAOs
│   │       └── <domain>_dao.py    # Extends BasePgDAO[Model]
│   ├── service/
│   │   ├── base_service.py        # Abstract base with ABAC guard
│   │   ├── exceptions.py          # BaseServiceException hierarchy
│   │   └── <domain>/
│   │       ├── __init__.py
│   │       ├── <domain>_service.py
│   │       └── <domain>_exceptions.py
│   ├── types/                     # Internal Pydantic DTOs
│   │   ├── __init__.py            # BaseModelWithDefaultConfig, mixins
│   │   ├── auth/                  # JWT claim models
│   │   └── <domain>/              # Base, Create, Update, Internal, Filter
│   └── tasks/                     # Background schedulers
└── tests/
    ├── unit/                      # Isolated unit tests
    └── e2e/                       # End-to-end against live server
        ├── conftest.py            # Session fixtures (setup, tokens, clients)
        ├── auth.py                # JWT generation for test personas
        ├── setup.py               # Idempotent env provisioning
        ├── teardown.py            # Cleanup script
        ├── state.py               # Persistent test state models
        ├── clients/
        │   └── api_client.py      # httpx-based test client
        └── scenarios/
            └── test_<domain>.py   # Test classes: Happy, Failure, ABAC
```

## Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Package/Module | snake_case | `booking_service.py` |
| Class | PascalCase | `BookingService` |
| Router file | `<domain>_router.py` | `appointment_router.py` |
| DAO file | `<domain>_dao.py` | `slot_dao.py` |
| Exception file | `<domain>_exceptions.py` | `scheduling_exceptions.py` |
| Model file | `<domain>.py` | `slot.py` |
| Type file | `<domain>.py` | `schedule.py` |
| Schema dir | `<domain>/` | `appointment/request.py` |
| Test file | `test_<domain>.py` | `test_organization.py` |

## Key Rules

1. **Imports at top** — No inline imports unless avoiding circular dependencies. If needed, document why in a comment.
2. **Constants centralized** — All magic strings, paths, URIs go in `config/constants.py`.
3. **Logger usage** — Always `from app.core.common.logger import get_logger`.
4. **Model registry** — Every new SQLAlchemy model MUST be imported in `dao/models/__init__.py` for Alembic to detect it.
5. **Pydantic defaults** — Optional fields always use `default=None` explicitly.
6. **PATCH not PUT** — Update endpoints use PATCH (partial update), not PUT.
