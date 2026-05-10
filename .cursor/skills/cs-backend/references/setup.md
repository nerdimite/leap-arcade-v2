# Interactive Project Setup

This guide walks through setting up a new FastAPI backend project. Use the `AskQuestion` tool to gather requirements from the user before scaffolding.

## Phase 1: Gather Requirements

Ask the user the following questions (use `AskQuestion` when available, otherwise ask conversationally):

### Q1: Project Identity

```
- Project name? (e.g., "billing-service", "inventory-api")
- Python package name? (lowercase, underscores — e.g., "billing", "inventory")
- Description? (one-liner for pyproject.toml)
```

### Q2: Database

```
Options:
  a) Neon Postgres (async, recommended)
  b) Standard Postgres (async)
  c) SQLite (dev/prototype only)
  d) No database (stateless API)
```

If database selected, also ask:
```
- Do you need soft delete support? (is_deleted flag) [Yes/No]
- Do you need audit fields? (created_by, created_at, modified_by, modified_at) [Yes/No]
```

### Q3: Authentication

```
Options:
  a) Clerk (JWT via JWKS — recommended)
  b) Custom JWT (bring your own JWKS endpoint)
  c) API key only
  d) No auth (public API)
```

### Q4: Multi-Tenancy

```
Options:
  a) Yes — org-scoped isolation (each resource belongs to an org)
  b) No — single tenant
```

### Q5: Access Control

```
Options:
  a) ABAC (Attribute-Based) — JSON policies with org/user/role context
  b) RBAC (Role-Based) — simple role checks (admin, member, viewer)
  c) Both ABAC + RBAC
  d) No access control
```

If ABAC/RBAC selected:
```
- What roles do you need? (e.g., admin, member, viewer — comma-separated)
```

### Q6: Additional Features

```
Select all that apply:
  a) Email notifications (SendGrid / SES / console)
  b) SMS notifications (Twilio / SNS / console)
  c) S3 file storage
  d) Background task scheduler
  e) Webhook handling (Svix verification)
  f) None of the above
```

### Q7: Testing

```
Options:
  a) Yes — scaffold test directories
  b) No test scaffold
```

If yes, create the `tests/unit/` and `tests/e2e/` directories. For E2E test implementation, defer to the `e2e-tester` skill if available in the project.

---

## Phase 2: Scaffold the Project

Based on answers, create the following structure. **Always include** the core files; conditionally include optional modules.

### Step 1: Initialize with uv

```bash
# Create project directory
mkdir <project-name> && cd <project-name>

# Initialize uv project
uv init --python 3.13

# Remove default hello.py if created
rm -f hello.py
```

### Step 2: Create Directory Structure

```bash
# Core directories (always)
mkdir -p <package>/config
mkdir -p <package>/core/common/id
mkdir -p <package>/core/context
mkdir -p <package>/core/database
mkdir -p <package>/api/dependencies
mkdir -p <package>/api/routes
mkdir -p <package>/api/schema
mkdir -p <package>/dao/models
mkdir -p <package>/dao/pg
mkdir -p <package>/service
mkdir -p <package>/types

# Conditional directories
# If auth: mkdir -p <package>/core/auth
# If ABAC: mkdir -p <package>/core/abac
# If notifications: mkdir -p <package>/core/notifications
# If S3: mkdir -p <package>/core/storage
# If webhooks: mkdir -p <package>/core/webhook
# If tasks: mkdir -p <package>/tasks
# If testing: mkdir -p tests/unit tests/e2e  (use e2e-tester skill for full E2E scaffold)
```

### Step 3: Install Dependencies

```bash
# Core (always)
uv add fastapi uvicorn pydantic pydantic-settings structlog rich

# Database (if selected)
uv add sqlalchemy asyncpg alembic psycopg2-binary  # Postgres
# or: uv add sqlalchemy aiosqlite alembic           # SQLite

# Auth (if Clerk)
uv add pyjwt[crypto] httpx cachetools

# S3 (if selected)
uv add aioboto3 boto3

# Notifications (if selected)
# uv add sendgrid  # for SendGrid
# uv add twilio    # for Twilio

# Webhooks (if selected)
# uv add svix

# Server (always for production)
uv add gunicorn

# Dev dependencies
uv add --group dev pytest pytest-asyncio pyright python-dotenv
```

### Step 4: Create Files

Use the scaffolds from `references/scaffolds/` to create each file. The order matters:

1. **`pyproject.toml`** — [pyproject-toml.md](scaffolds/pyproject-toml.md)
2. **`<package>/config/settings.py`** — [settings-config.md](scaffolds/settings-config.md)
3. **`<package>/config/errors.py`** — [settings-config.md](scaffolds/settings-config.md) (error codes section)
4. **`<package>/config/constants.py`** — [settings-config.md](scaffolds/settings-config.md) (constants section)
5. **`<package>/core/common/logger.py`** — [logger.md](scaffolds/logger.md)
6. **`<package>/core/common/`** (all utilities) — [common-utilities.md](scaffolds/common-utilities.md)
7. **`<package>/core/database/`** — [common-utilities.md](scaffolds/common-utilities.md) (database provider section)
8. **`<package>/core/context/`** — [main-app.md](scaffolds/main-app.md) (AppContext + ContextManager)
9. **`<package>/dao/models/base.py`** — [base-models.md](scaffolds/base-models.md)
10. **`<package>/dao/models/__init__.py`** — import registry (critical for Alembic)
11. **`<package>/dao/base_pg_dao.py`** — [base-dao.md](scaffolds/base-dao.md)
12. **`<package>/service/exceptions.py`** — [base-exceptions.md](scaffolds/base-exceptions.md)
13. **`<package>/service/base_service.py`** — [base-service.md](scaffolds/base-service.md)
14. **`<package>/api/schema/__init__.py`** — [api-schema.md](scaffolds/api-schema.md) (base responses)
15. **`<package>/types/__init__.py`** — [domain-types.md](scaffolds/domain-types.md) (base config)
16. **`<package>/api/dependencies/auth.py`** — [auth-dependency.md](scaffolds/auth-dependency.md) (if auth)
17. **`<package>/api/dependencies/service_container.py`** — [service-container.md](scaffolds/service-container.md)
18. **`<package>/api/routes/__init__.py`** — router aggregation
19. **`<package>/main.py`** — [main-app.md](scaffolds/main-app.md)
20. **ABAC files** (if selected) — [abac-system.md](scaffolds/abac-system.md)

### Step 5: Initialize Alembic (if database)

```bash
uv run alembic init alembic
```

Then replace `alembic/env.py` with the scaffold from [alembic-env.md](scaffolds/alembic-env.md). Key points:
- Imports all models via `from <package>.dao.models import *`
- Sets `target_metadata = Base.metadata`
- Strips `+asyncpg` from connection string so Alembic uses sync `psycopg2`

### Step 6: Create .gitignore

Use the scaffold from [gitignore.md](scaffolds/gitignore.md).

### Step 7: Create .env Files

```bash
# .env.example (committed)
cat > .env.example << 'EOF'
ENVIRONMENT="local"
LOG_LEVEL=DEBUG
LOG_FORMAT=json
POSTGRES_CONNECTION_STRING=
# Add auth, provider, and feature-specific vars based on answers
EOF

# .env (gitignored, copy from example)
cp .env.example .env
```

### Step 8: Create Dockerfile (optional)

Use the scaffold from [dockerfile.md](scaffolds/dockerfile.md) for production deployment.

### Step 9: Verify Setup

```bash
# Install all dependencies
uv sync

# Start dev server
uv run dev

# Should see:
# INFO:     Uvicorn running on http://0.0.0.0:8080
# Visit http://localhost:8080/docs for Swagger UI
```

---

## Phase 3: First Domain Feature

After scaffolding, guide the user through adding their first domain feature using the [New Feature Checklist](../SKILL.md#new-feature-checklist) in SKILL.md.

Walk through each step, using the scaffolds to generate concrete code for their specific domain entity.

---

## Decision Matrix

| User Choice | Files to Scaffold | Skip |
|---|---|---|
| No database | Skip: dao/, models/, alembic, base_pg_dao | — |
| No auth | Skip: auth.py, auth_exceptions.py | Use simple `ServiceContainer` without auth dep |
| No multi-tenancy | Use `AuditBase` instead of `OrgBase` | Skip `org_id` fields |
| No ABAC | Skip: core/abac/, policies.json | Remove guard from BaseService & BasePgDAO |
| RBAC only | Use simple role decorator instead of full ABAC | Skip compiler/evaluator |
