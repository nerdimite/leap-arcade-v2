"""Seed loader: reads JSON data files and upserts into the database at startup.

Called from the FastAPI lifespan when SEED_ON_STARTUP=true.
"""

import json
import structlog
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger(__name__)

DATA_DIR = Path(__file__).parent / "data"


async def seed_all(session: AsyncSession) -> None:
    """Upsert players and rapid fire questions from JSON seed files."""
    await _seed_players(session)
    await _seed_rapid_fire(session)


async def _seed_players(session: AsyncSession) -> None:
    path = DATA_DIR / "players.json"
    if not path.exists():
        logger.warning("seed.players.missing", path=str(path))
        return

    players = json.loads(path.read_text())
    for p in players:
        await session.execute(
            text(
                """
                INSERT INTO players (id, display_name)
                VALUES (:id, :display_name)
                ON CONFLICT (id) DO UPDATE SET display_name = EXCLUDED.display_name
                """
            ),
            {"id": p["id"], "display_name": p["display_name"]},
        )
    await session.commit()
    logger.info("seed.players.done", count=len(players))


async def _seed_rapid_fire(session: AsyncSession) -> None:
    path = DATA_DIR / "rapid_fire.json"
    if not path.exists():
        logger.warning("seed.rapid_fire.missing", path=str(path))
        return

    questions = json.loads(path.read_text())
    for q in questions:
        await session.execute(
            text(
                """
                INSERT INTO rapid_fire_questions
                    (question, options, correct_option_index, category, time_limit_ms)
                VALUES
                    (:question, :options, :correct_option_index, :category, :time_limit_ms)
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "question": q["question"],
                "options": q["options"],
                "correct_option_index": q["correct_option_index"],
                "category": q.get("category"),
                "time_limit_ms": q.get("time_limit_ms", 15000),
            },
        )
    await session.commit()
    logger.info("seed.rapid_fire.done", count=len(questions))
