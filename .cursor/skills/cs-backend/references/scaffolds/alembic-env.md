# Alembic env.py Scaffold

Setting up Alembic with async SQLAlchemy requires specific configuration. This scaffold handles both sync and async migrations.

## alembic/env.py

```python
import asyncio
from logging.config import fileConfig

from sqlalchemy import Connection, create_engine, pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from app.config.settings import get_settings

# CRITICAL: Import all models so Alembic detects them for autogenerate
from app.dao.models import *  # noqa: F401,F403
from app.dao.models.base import Base

target_metadata = Base.metadata


def get_database_url() -> str:
    """Get sync database URL from settings (strips +asyncpg if present)."""
    settings = get_settings()
    if not settings.POSTGRES_CONNECTION_STRING:
        raise ValueError("POSTGRES_CONNECTION_STRING not configured")
    conn_str = settings.POSTGRES_CONNECTION_STRING
    if conn_str.startswith("postgresql+asyncpg://"):
        conn_str = "postgresql://" + conn_str[len("postgresql+asyncpg://"):]
    return conn_str


def run_migrations_offline() -> None:
    """Run migrations without a live database connection (generates SQL)."""
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Execute migrations on an active connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations using an async engine (for asyncpg)."""
    url = get_database_url()
    config_section = config.get_section(config.config_ini_section, {})
    config_section["sqlalchemy.url"] = url

    connectable = async_engine_from_config(
        config_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in online mode (sync engine, works with alembic CLI)."""
    url = get_database_url()
    connectable = create_engine(url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        do_run_migrations(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

## Initialization

```bash
# Initialize alembic (creates alembic/ directory and alembic.ini)
uv run alembic init alembic

# Then replace alembic/env.py with the scaffold above
```

## alembic.ini tweaks

The default `alembic.ini` works as-is. The `sqlalchemy.url` setting is ignored because `env.py` overrides it from `Settings`. No changes needed.

## Running Against Different Environments

The `Settings` class uses `ENV_FILE` to determine which `.env` file to load (defaults to `.env`). Prefix any command with `ENV_FILE=<path>` to target a different database:

```bash
# Local (default — reads .env)
uv run alembic upgrade head

# Dev database
ENV_FILE=.env.dev uv run alembic upgrade head

# Staging database
ENV_FILE=.env.staging uv run alembic revision --autogenerate -m "add_items_table"
```

This works because the `Settings` class is configured with:

```python
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        case_sensitive=False,
        extra="ignore",
    )
```

The same `ENV_FILE` pattern works for any `uv run` command, not just Alembic:

```bash
# Start dev server against dev database
ENV_FILE=.env.dev uv run dev

# Run E2E tests against staging
ENV_FILE=.env.staging uv run pytest -m e2e
```

You can also override a single variable inline if you just need to swap the connection string:

```bash
POSTGRES_CONNECTION_STRING="postgresql://..." uv run alembic upgrade head
```

## Common Commands

```bash
# Generate a migration from model changes
uv run alembic revision --autogenerate -m "add_items_table"

# Apply all pending migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1

# Show migration history
uv run alembic history

# Show current revision
uv run alembic current
```

## Key Points

- `get_database_url()` strips `+asyncpg` so Alembic uses the sync `psycopg2` driver — Alembic CLI runs synchronously
- `compare_type=True` and `compare_server_default=True` ensure column type and default changes are detected
- The `from app.dao.models import *` line is **critical** — without it, Alembic won't see your models for `--autogenerate`
- Every new model must be imported in `dao/models/__init__.py` for this to work
