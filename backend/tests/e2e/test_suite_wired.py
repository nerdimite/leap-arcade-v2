"""Smoke tests proving e2e infrastructure (PG + ASGI transport). Journey tests arrive in later slices."""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from tests.e2e.conftest import E2E_POSTGRES_URL, truncate_transaction_tables


async def test_health_via_async_client(client) -> None:
    r = await client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body.get("status") == "ok"
    assert body.get("db") == "ok"


async def test_suite_seeds_question_pool(db_setup: None) -> None:
    engine = create_async_engine(E2E_POSTGRES_URL)
    try:
        async with engine.connect() as conn:
            n = (await conn.execute(text("SELECT COUNT(*) FROM rapid_fire_questions"))).scalar_one()
            assert isinstance(n, int)
            assert n > 0
    finally:
        await engine.dispose()


async def test_truncate_preserves_rapid_fire_content(db_setup: None) -> None:
    engine = create_async_engine(E2E_POSTGRES_URL)
    try:
        async with engine.connect() as conn:
            before = (
                await conn.execute(text("SELECT COUNT(*) FROM rapid_fire_questions"))
            ).scalar_one()
        async with engine.begin() as conn:
            await conn.execute(
                text(
                    "INSERT INTO players (id, display_name) VALUES ('e2e-truncate-marker', 'Infra')"
                )
            )
        await truncate_transaction_tables(engine)
        async with engine.connect() as conn:
            players = (await conn.execute(text("SELECT COUNT(*) FROM players"))).scalar_one()
            after_questions = (
                await conn.execute(text("SELECT COUNT(*) FROM rapid_fire_questions"))
            ).scalar_one()
        assert players == 0
        assert after_questions == before
        assert after_questions > 0
    finally:
        await engine.dispose()
