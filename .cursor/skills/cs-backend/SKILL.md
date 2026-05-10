---
name: cs-backend
description: Scaffold and build production-grade FastAPI backend APIs with structured patterns for dependency injection, Clerk JWT auth, ABAC/RBAC policies, async Postgres DAOs, Pydantic DTOs, service layer, and uv package management. Use when setting up a new FastAPI backend project, adding a new service/feature to an existing one, or asking about backend architecture patterns.
---

# FastAPI Backend System

Comprehensive system for building production-grade FastAPI backend APIs. Covers project setup, architecture patterns, and scaffolded code.

## Quick Start

**New project?** Run the interactive setup:
> Follow the [Setup Guide](references/setup.md) — it asks about your DB, auth, multi-tenancy, and ABAC needs, then scaffolds the project.

**Adding a feature to an existing project?** Follow the [New Feature Checklist](#new-feature-checklist).

## Architecture Overview

```
project_root/
├── pyproject.toml              # uv-managed deps & scripts
├── alembic.ini                 # Migration config
├── alembic/                    # DB migrations
├── app/                        # Main package (rename per project)
│   ├── main.py                 # FastAPI app, lifespan, exception handlers
│   ├── config/
│   │   ├── settings.py         # pydantic-settings env config
│   │   ├── constants.py        # Domain constants
│   │   ├── errors.py           # Error codes, HTTP statuses, messages
│   │   └── policies.json       # ABAC policy definitions
│   ├── core/
│   │   ├── abac/               # Access control (guard, compiler, evaluator)
│   │   ├── auth/               # Auth client (Clerk, etc.)
│   │   ├── common/             # Logger, pagination, ID gen, sanitize, timezone
│   │   ├── context/            # AppContext singleton, ContextManager (infra)
│   │   └── database/           # Async Postgres provider
│   ├── api/
│   │   ├── dependencies/       # Auth dep, ServiceContainer DI
│   │   ├── routes/             # Domain routers
│   │   └── schema/             # Request/Response schemas per domain
│   ├── dao/
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── pg/                 # Postgres DAOs
│   │   └── base_pg_dao.py      # Generic base DAO
│   ├── service/
│   │   ├── base_service.py     # Abstract base with ABAC guard
│   │   ├── exceptions.py       # Base exception hierarchy
│   │   └── <domain>/           # Domain services + exceptions
│   ├── types/                  # Pydantic internal DTOs (Base/Create/Update/Internal)
│   └── tasks/                  # Background tasks / scheduler
└── tests/
    ├── unit/
    └── e2e/                    # Persona-based E2E tests
```

See [Project Structure](references/project-structure.md) for full conventions.

## Core Patterns

### 1. Dependency Injection

Two-tier DI: FastAPI `Depends()` chain → lazy `ServiceContainer`.

```python
# Route injects the container
async def create_item(
    body: CreateItemRequest,
    services: ServiceContainer = Depends(get_service_container),
):
    result = await services.item.create(body)
    return SuccessResponse(message="Created", data=result)
```

`get_service_container` depends on `get_auth_user` (auth) + `get_context_manager` (infra). Each service is lazily instantiated on first property access.

See [Dependency Injection](references/dependency-injection.md) | [Scaffold](references/scaffolds/service-container.md)

### 2. Authentication

Clerk JWT verification via JWKS. Extracts `UserContext` with `id`, `roles`, `org`, `user` claims.

```python
CurrentUser = Annotated[UserContext, Depends(get_auth_user)]
```

See [Auth Patterns](references/auth-patterns.md) | [Scaffold](references/scaffolds/auth-dependency.md)

### 3. ABAC / RBAC

JSON policy file: `role → resource → action → [rules]`. Rules use operators (`$eq`, `$in`, `$or`) with context variables (`$org.id`, `$user.id`).

- **CREATE**: `ABACEvaluator` checks payload against rules in-memory
- **READ/LIST**: `ABACCompiler` converts rules to SQLAlchemy WHERE clauses injected into every query
- **Guard**: `AccessControlGuard` orchestrates both, attached to every service/DAO

See [ABAC](references/abac.md) | [Scaffold](references/scaffolds/abac-system.md)

### 4. Database & DAO Layer

Async SQLAlchemy + Neon Postgres. Three-tier model hierarchy:

- `Base` — plain DeclarativeBase
- `AuditBase` — `created_by`, `created_at`, `modified_by`, `modified_at`, `is_deleted`
- `OrgBase` — extends AuditBase + `org_id` for multi-tenant isolation

Generic `BasePgDAO[T]` provides CRUD with automatic ABAC filtering, soft delete, audit stamping, and pagination.

See [Database & DAO](references/database-and-dao.md) | Scaffolds: [Models](references/scaffolds/base-models.md), [DAO](references/scaffolds/base-dao.md)

### 5. Service Layer

Every service extends `BaseService(context, context_manager)`:
- Lazy ABAC guard via `self.guard`
- Convenience: `self.user_id`, `self.org_id`, `self.user_email`
- Creates domain-specific DAOs in `__init__`, passing guard for row-level security

See [Service Layer](references/service-layer.md) | Scaffolds: [Service](references/scaffolds/base-service.md), [Exceptions](references/scaffolds/base-exceptions.md)

### 6. API Layer

Standard patterns: domain router → schema validation → service call → typed response.

Response envelope: `{ success, message, data }` via `SuccessResponse[T]`.
Pagination: `PaginatedSuccessResponse[T]` with `PaginationInfo`.
Errors: `{ success: false, message, code, http_status, error }`.

See [API Layer](references/api-layer.md) | Scaffolds: [Route](references/scaffolds/api-route.md), [Schema](references/scaffolds/api-schema.md)

### 7. Pydantic Types (DTOs)

Four-class pattern per entity: `Base` → `Create` → `Update` → `Internal`.

All extend `BaseModelWithDefaultConfig` which enables camelCase aliasing, enum values, and extra ignore.

See [Pydantic Types](references/pydantic-types.md) | [Scaffold](references/scaffolds/domain-types.md)

### 8. Error Handling

Three-tier: `ErrorCodes` (numeric) + `ErrorHttpStatus` (HTTP mapping) + `ErrorMessages` (strings).

All service exceptions extend `BaseServiceException` → caught by global handler → standard JSON response.

See [Error Handling](references/error-handling.md) | [Scaffold](references/scaffolds/base-exceptions.md)

### 9. Config & Settings

`pydantic-settings` for env-driven config. Singleton `get_settings()`. Groups: database, auth, CORS, providers.

See [Config & Settings](references/config-and-settings.md) | [Scaffold](references/scaffolds/settings-config.md)

### 10. uv & Scripts

`uv` for dependency management and custom scripts defined in `[project.scripts]`.

See [uv & Scripts](references/uv-scripts.md) | [Scaffold](references/scaffolds/pyproject-toml.md)

## New Feature Checklist

When adding a new domain feature (e.g., "orders", "invoices"), follow this order:

1. **Data Model** — Define SQLAlchemy model in `dao/models/`. Import in `dao/models/__init__.py`. Generate migration.
2. **DAO** — Create DAO in `dao/pg/` extending `BasePgDAO`. Implement `_apply_filters()`.
3. **Types** — Create Pydantic DTOs in `types/<domain>/` (Base, Create, Update, Internal, Filter).
4. **Errors** — Add error codes to `config/errors.py`. Create `<domain>_exceptions.py`.
5. **Service** — Create service in `service/<domain>/` extending `BaseService`. Add ABAC guards.
6. **ABAC** — Add policies to `policies.json` for each role.
7. **DI** — Register service in `ServiceContainer`.
8. **Schemas** — Create request/response in `api/schema/<domain>/`.
9. **Routes** — Create router in `api/routes/`. Register in `api/routes/__init__.py`.

## Reference Index

| Topic | Reference | Scaffold |
|-------|-----------|----------|
| Project setup | [setup.md](references/setup.md) | — |
| Directory layout | [project-structure.md](references/project-structure.md) | [gitignore.md](references/scaffolds/gitignore.md) |
| FastAPI app | — | [main-app.md](references/scaffolds/main-app.md) |
| pyproject.toml | [uv-scripts.md](references/uv-scripts.md) | [pyproject-toml.md](references/scaffolds/pyproject-toml.md) |
| Settings | [config-and-settings.md](references/config-and-settings.md) | [settings-config.md](references/scaffolds/settings-config.md) |
| Logging | [config-and-settings.md](references/config-and-settings.md) | [logger.md](references/scaffolds/logger.md) |
| Common utilities | — | [common-utilities.md](references/scaffolds/common-utilities.md) |
| Auth | [auth-patterns.md](references/auth-patterns.md) | [auth-dependency.md](references/scaffolds/auth-dependency.md) |
| DI | [dependency-injection.md](references/dependency-injection.md) | [service-container.md](references/scaffolds/service-container.md) |
| Database & DAO | [database-and-dao.md](references/database-and-dao.md) | [base-models.md](references/scaffolds/base-models.md), [base-dao.md](references/scaffolds/base-dao.md) |
| Alembic migrations | [database-and-dao.md](references/database-and-dao.md) | [alembic-env.md](references/scaffolds/alembic-env.md) |
| Service layer | [service-layer.md](references/service-layer.md) | [base-service.md](references/scaffolds/base-service.md) |
| ABAC | [abac.md](references/abac.md) | [abac-system.md](references/scaffolds/abac-system.md) |
| API routes & schemas | [api-layer.md](references/api-layer.md) | [api-route.md](references/scaffolds/api-route.md), [api-schema.md](references/scaffolds/api-schema.md) |
| Pydantic types | [pydantic-types.md](references/pydantic-types.md) | [domain-types.md](references/scaffolds/domain-types.md) |
| Error handling | [error-handling.md](references/error-handling.md) | [base-exceptions.md](references/scaffolds/base-exceptions.md) |
| Dockerfile | — | [dockerfile.md](references/scaffolds/dockerfile.md) |
| Testing | Defer to `e2e-tester` / `generic-e2e-tester` skill if available | — |
