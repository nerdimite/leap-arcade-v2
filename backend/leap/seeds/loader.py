"""Seed loader: reads JSON data files and upserts into content tables at startup.

Called from the FastAPI lifespan when SEED_ON_STARTUP=true.
"""
import json
import logging
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent / "data"


async def seed_all(session: AsyncSession) -> None:
    """Upsert all game content from JSON seed files into the database."""
    logger.info("Starting seed data load")
    # TODO: implement per-game upsert logic once content DAOs are in place
    # For now, just log that we would seed each game
    for game in ["wiki", "picture", "rapid_fire", "four_pics", "crossword"]:
        path = DATA_DIR / f"{game}.json"
        if path.exists():
            data = json.loads(path.read_text())
            logger.info("Would seed %d records for game=%s", len(data), game)
        else:
            logger.warning("No seed file found for game=%s at %s", game, path)
    logger.info("Seed data load complete (stub — no actual DB writes yet)")
