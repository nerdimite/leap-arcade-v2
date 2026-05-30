"""Shared fixtures for API e2e tests: migrations, seeds, DB cleanup, ASGI client.

Only loaded when pytest collects ``tests/e2e/``, so ``tests/unit`` runs stay isolated.
"""

from __future__ import annotations

import asyncio
import functools
import os
import subprocess
import sys
from pathlib import Path
from typing import AsyncIterator

import httpx
import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import ASGITransport
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

_BACKEND_ROOT = Path(__file__).resolve().parents[2]

# Must align with postgres_test overlay (docker-compose.test.yml).
E2E_POSTGRES_URL = "postgresql+asyncpg://leap:leap@localhost:5433/leap_test"


def _truncate_transactional_tables_sql() -> str:
    return (
        "TRUNCATE TABLE players, game_sessions, rapid_fire_answers "
        "RESTART IDENTITY CASCADE"
    )


async def truncate_transaction_tables(engine: AsyncEngine) -> None:
    stmt = text(_truncate_transactional_tables_sql())
    async with engine.begin() as conn:
        await conn.execute(stmt)


async def truncate_all_tables_for_suite(engine: AsyncEngine) -> None:
    """Full wipe including seeded question pools — used once per pytest session."""
    stmt = text(
        "TRUNCATE TABLE rapid_fire_answers, four_pics_question_attempts, "
        "crossword_solves, word_hunt_finds, game_sessions, players, "
        "rapid_fire_questions, four_pics_questions, crossword_entries, "
        "crossword_puzzles, word_hunt_words, word_hunt_puzzles "
        "RESTART IDENTITY CASCADE"
    )
    async with engine.begin() as conn:
        await conn.execute(stmt)


def _apply_e2e_settings_patch() -> None:
    import leap.config.settings as settings_mod

    settings_mod.get_settings.cache_clear()

    @functools.lru_cache(maxsize=1)
    def patched_get_settings() -> settings_mod.Settings:
        base = settings_mod.Settings()  # type: ignore[call-arg]
        return base.model_copy(
            update={
                "POSTGRES_CONNECTION_STRING": E2E_POSTGRES_URL,
                "SEED_ON_STARTUP": False,
                "ENVIRONMENT": "test",
            }
        )

    settings_mod.get_settings = patched_get_settings  # type: ignore[assignment]


# JWT / EVENT_CODE pulled from backend/.env when present; CI / bare env falls back safely.
os.environ.setdefault("JWT_SECRET_KEY", "e2e-dev-jwt-secret-key-hs256-32-characters!")
os.environ.setdefault("EVENT_CODE", "e2e-event-code")

_apply_e2e_settings_patch()

from leap.api.main import app


def _run_alembic_upgrade_head() -> None:
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=_BACKEND_ROOT,
        env={**os.environ, "POSTGRES_CONNECTION_STRING": E2E_POSTGRES_URL},
        check=True,
    )


async def _run_seed_once() -> None:
    from leap.config.settings import get_settings
    from leap.core.context_manager import ContextManager
    from leap.seeds.loader import seed_all

    context = ContextManager(get_settings())
    await context.initialize()
    try:
        async with context.session() as session:
            await seed_all(session)
    finally:
        await context.close()


async def _e2e_migrate_then_seed_fresh_pool() -> None:
    """Truncate all game tables once, then load seeds (stable Rapid Fire pool size).

    The seed loader uses ``INSERT ... ON CONFLICT DO NOTHING`` without a usable
    conflict target for PostgreSQL's UUID PK rows, so a persistent ``postgres_test``
    volume accumulates duplicate questions unless we truncate the content table once
    per pytest session before ``seed_all``.
    """
    engine = create_async_engine(E2E_POSTGRES_URL)
    try:
        await truncate_all_tables_for_suite(engine)
    finally:
        await engine.dispose()
    await _run_seed_once()


@pytest.fixture(scope="session")
def db_setup() -> None:
    """Migrate test DB, wipe all rows once per process, then load seeds."""
    _run_alembic_upgrade_head()
    asyncio.run(_e2e_migrate_then_seed_fresh_pool())


@pytest_asyncio.fixture(autouse=True)
async def clean_db(db_setup: None) -> AsyncIterator[None]:
    """Truncate transactional tables then restore seed ``players`` from JSON.

    ``rapid_fire_questions`` stays as loaded during ``db_setup``. Player rows are
    re-upserted so login-based journeys work without inserting ad-hoc players.
    """
    from leap.seeds.loader import _seed_players

    engine = create_async_engine(E2E_POSTGRES_URL)
    try:
        await truncate_transaction_tables(engine)
        factory = async_sessionmaker(engine, expire_on_commit=False)
        async with factory() as session:
            await _seed_players(session)
    finally:
        await engine.dispose()

    yield


@pytest_asyncio.fixture
async def client(clean_db: None) -> AsyncIterator[httpx.AsyncClient]:
    """ASGI-bound client depending on ``clean_db`` for deterministic setup order."""
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
