"""Admin-only operational routes.

Guarded by the ``X-Admin-API-Key`` header (see ``require_admin_api_key``), not the
player JWT. Intended for event organizers — e.g. wiping the event clean between
rehearsal and the live run, and triggering it straight from Swagger.
"""

from typing import List

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy import text

from leap.api.deps import require_admin_api_key
from leap.core.cache_invalidation import emit_cache_invalidation
from leap.core.common.logger import get_logger
from leap.seeds.loader import seed_all

router = APIRouter()

logger = get_logger(__name__)

# Every table the app owns, child tables first. ``RESTART IDENTITY CASCADE`` makes
# FK ordering moot, but the explicit list documents the full reset surface.
_ALL_TABLES: List[str] = [
    "rapid_fire_answers",
    "wiki_puzzle_attempts",
    "picture_puzzle_attempts",
    "four_pics_question_attempts",
    "pinpoint_puzzle_attempts",
    "word_hunt_finds",
    "crossword_solves",
    "game_sessions",
    "players",
    "rapid_fire_questions",
    "wiki_rounds",
    "picture_puzzles",
    "four_pics_questions",
    "pinpoint_puzzles",
    "word_hunt_words",
    "word_hunt_puzzles",
    "crossword_entries",
    "crossword_puzzles",
]


class ResetResponse(BaseModel):
    status: str
    tables_cleared: int
    message: str


@router.post(
    "/reset",
    response_model=ResetResponse,
    summary="Reset the event database",
    dependencies=[Depends(require_admin_api_key)],
)
async def reset_database(request: Request) -> ResetResponse:
    """Wipe all players, sessions, scores, and content, then re-seed from JSON.

    Steps:
    1. ``TRUNCATE`` every table (runtime + seeded content) with ``RESTART IDENTITY CASCADE``.
    2. Re-run the idempotent seed loader to restore players and game content.
    3. Re-warm this worker's in-memory content cache so the response reflects the
       fresh pools immediately.
    4. Broadcast a cache-invalidation NOTIFY so every other gunicorn worker refreshes
       its caches too (no restart required).
    """
    context_manager = request.app.state.context_manager
    container = request.app.state.container

    logger.warning("Admin database reset requested")

    truncate_sql = text(f"TRUNCATE TABLE {', '.join(_ALL_TABLES)} RESTART IDENTITY CASCADE")

    async with context_manager.session() as session:
        await session.execute(truncate_sql)
        await session.commit()
        await seed_all(session)

    async with context_manager.session() as session:
        await container.warm_caches(session)

    await emit_cache_invalidation(context_manager)

    logger.warning("Admin database reset complete", tables_cleared=len(_ALL_TABLES))

    return ResetResponse(
        status="ok",
        tables_cleared=len(_ALL_TABLES),
        message="Database cleared and re-seeded. Caches refreshed across all workers.",
    )
