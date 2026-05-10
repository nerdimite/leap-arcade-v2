import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from leap.dao.models import Base  # noqa: F401 — models __init__ registers ORM tables on metadata

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    """Get database URL from environment, falling back to alembic.ini value."""
    return os.environ.get(
        "POSTGRES_CONNECTION_STRING",
        config.get_main_option("sqlalchemy.url"),
    )


def run_migrations_offline() -> None:
    """Run migrations in offline mode (generate SQL without a live connection)."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations against a live database connection."""
    connectable = create_async_engine(get_url())

    async with connectable.connect() as connection:
        await connection.run_sync(
            lambda sync_conn: context.configure(
                connection=sync_conn,
                target_metadata=target_metadata,
            )
        )
        await connection.run_sync(
            lambda sync_conn: context.run_migrations()
        )

    await connectable.dispose()


def run() -> None:
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        asyncio.run(run_migrations_online())


run()
