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
    """Upsert players, game seeds, and content tables from JSON."""
    await _seed_players(session)
    await _seed_rapid_fire(session)
    await _seed_wiki(session)
    await _seed_picture(session)
    await _seed_four_pics(session)


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
                    (id, question, options, correct_option_index, category, time_limit_ms)
                VALUES
                    (:id, :question, :options, :correct_option_index, :category, :time_limit_ms)
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {
                "id": q["id"],
                "question": q["question"],
                "options": q["options"],
                "correct_option_index": q["correct_option_index"],
                "category": q.get("category"),
                "time_limit_ms": q.get("time_limit_ms", 15000),
            },
        )
    await session.commit()
    logger.info("seed.rapid_fire.done", count=len(questions))


async def _seed_wiki(session: AsyncSession) -> None:
    path = DATA_DIR / "wiki.json"
    if not path.exists():
        logger.warning("seed.wiki.missing", path=str(path))
        return

    rounds = json.loads(path.read_text())
    for r in rounds:
        await session.execute(
            text(
                """
                INSERT INTO wiki_rounds (
                    id,
                    sequence_index,
                    start_title,
                    start_url,
                    target_title,
                    target_url,
                    clue,
                    optimal_click_count,
                    solution_path,
                    time_limit_ms
                )
                VALUES (
                    :id,
                    :sequence_index,
                    :start_title,
                    :start_url,
                    :target_title,
                    :target_url,
                    :clue,
                    :optimal_click_count,
                    :solution_path,
                    :time_limit_ms
                )
                ON CONFLICT (sequence_index) DO UPDATE SET
                    start_title = EXCLUDED.start_title,
                    start_url = EXCLUDED.start_url,
                    target_title = EXCLUDED.target_title,
                    target_url = EXCLUDED.target_url,
                    clue = EXCLUDED.clue,
                    optimal_click_count = EXCLUDED.optimal_click_count,
                    solution_path = EXCLUDED.solution_path,
                    time_limit_ms = EXCLUDED.time_limit_ms
                """
            ),
            {
                "id": r["id"],
                "sequence_index": r["sequenceIndex"],
                "start_title": r["start"],
                "start_url": r["startLink"],
                "target_title": r["end"],
                "target_url": r["endLink"],
                "clue": r["clue"],
                "optimal_click_count": r["optimalClickCount"],
                "solution_path": r["solutionPath"],
                "time_limit_ms": r.get("timeLimitMs", 180000),
            },
        )
    await session.commit()
    logger.info("seed.wiki.done", count=len(rounds))


async def _seed_picture(session: AsyncSession) -> None:
    path = Path(__file__).parent / "picture.json"
    if not path.exists():
        logger.warning("seed.picture.missing", path=str(path))
        return

    puzzles = json.loads(path.read_text())
    for p in puzzles:
        await session.execute(
            text(
                """
                INSERT INTO picture_puzzles (
                    id,
                    image_filename,
                    canonical_answer,
                    accepted_answers
                )
                VALUES (
                    :id,
                    :image_filename,
                    :canonical_answer,
                    CAST(:accepted_answers AS jsonb)
                )
                ON CONFLICT (id) DO UPDATE SET
                    image_filename = EXCLUDED.image_filename,
                    canonical_answer = EXCLUDED.canonical_answer,
                    accepted_answers = EXCLUDED.accepted_answers
                """
            ),
            {
                "id": p["id"],
                "image_filename": p["image_filename"],
                "canonical_answer": p["canonical_answer"],
                "accepted_answers": json.dumps(p["accepted_answers"]),
            },
        )
    await session.commit()
    logger.info("seed.picture.done", count=len(puzzles))


async def _seed_four_pics(session: AsyncSession) -> None:
    path = DATA_DIR / "four_pics.json"
    if not path.exists():
        logger.warning("seed.four_pics.missing", path=str(path))
        return

    questions = json.loads(path.read_text())
    for q in questions:
        await session.execute(
            text(
                """
                INSERT INTO four_pics_questions (
                    id,
                    image_paths,
                    odd_one_out_index
                )
                VALUES (
                    :id,
                    CAST(:image_paths AS jsonb),
                    :odd_one_out_index
                )
                ON CONFLICT (id) DO UPDATE SET
                    image_paths = EXCLUDED.image_paths,
                    odd_one_out_index = EXCLUDED.odd_one_out_index
                """
            ),
            {
                "id": q["id"],
                "image_paths": json.dumps(q["image_paths"]),
                "odd_one_out_index": q["odd_one_out_index"],
            },
        )
    await session.commit()
    logger.info("seed.four_pics.done", count=len(questions))
