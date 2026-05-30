"""Seed loader: reads JSON data files and upserts into the database at startup.

Called from the FastAPI lifespan when SEED_ON_STARTUP=true.
"""

import json
import structlog
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from leap.games.crossword.grid import validate_grid_consistency, validate_seeded_entry
from leap.games.word_hunt.grid import validate_seeded_word

logger = structlog.get_logger(__name__)

DATA_DIR = Path(__file__).parent / "data"


async def seed_all(session: AsyncSession) -> None:
    """Upsert players, game seeds, and content tables from JSON."""
    await _seed_players(session)
    await _seed_rapid_fire(session)
    await _seed_wiki(session)
    await _seed_picture(session)
    await _seed_four_pics(session)
    await _seed_pinpoint(session)
    await _seed_word_hunt(session)
    await _seed_crossword(session)


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
                ON CONFLICT (id) DO UPDATE SET
                    question = EXCLUDED.question,
                    options = EXCLUDED.options,
                    correct_option_index = EXCLUDED.correct_option_index,
                    category = EXCLUDED.category,
                    time_limit_ms = EXCLUDED.time_limit_ms
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


async def _seed_pinpoint(session: AsyncSession) -> None:
    path = DATA_DIR / "pinpoint.json"
    if not path.exists():
        logger.warning("seed.pinpoint.missing", path=str(path))
        return

    puzzles = json.loads(path.read_text())
    for p in puzzles:
        await session.execute(
            text(
                """
                INSERT INTO pinpoint_puzzles (
                    answer,
                    answer_aliases,
                    clue1,
                    clue2,
                    clue3,
                    clue4,
                    clue5
                )
                VALUES (
                    :answer,
                    CAST(:answer_aliases AS jsonb),
                    :clue1,
                    :clue2,
                    :clue3,
                    :clue4,
                    :clue5
                )
                ON CONFLICT (answer) DO UPDATE SET
                    answer_aliases = EXCLUDED.answer_aliases,
                    clue1 = EXCLUDED.clue1,
                    clue2 = EXCLUDED.clue2,
                    clue3 = EXCLUDED.clue3,
                    clue4 = EXCLUDED.clue4,
                    clue5 = EXCLUDED.clue5
                """
            ),
            {
                "answer": p["answer"],
                "answer_aliases": json.dumps(p["answer_aliases"]),
                "clue1": p["clue1"],
                "clue2": p["clue2"],
                "clue3": p["clue3"],
                "clue4": p["clue4"],
                "clue5": p["clue5"],
            },
        )
    await session.commit()
    logger.info("seed.pinpoint.done", count=len(puzzles))


async def _seed_word_hunt(session: AsyncSession) -> None:
    path = DATA_DIR / "word_hunt.json"
    if not path.exists():
        logger.warning("seed.word_hunt.missing", path=str(path))
        return

    payload = json.loads(path.read_text())
    puzzle = payload["puzzle"]
    words = payload["words"]
    grid = puzzle["grid"]

    for word_entry in words:
        if not validate_seeded_word(
            grid,
            word_entry["word"],
            word_entry["start_row"],
            word_entry["start_col"],
            word_entry["end_row"],
            word_entry["end_col"],
        ):
            raise ValueError(
                f"word_hunt seed validation failed for word {word_entry['word']!r}"
            )

    puzzle_id = puzzle.get("id", "11111111-1111-1111-1111-111111111111")
    await session.execute(
        text(
            """
            INSERT INTO word_hunt_puzzles (id, rows, cols, grid)
            VALUES (:id, :rows, :cols, CAST(:grid AS jsonb))
            ON CONFLICT (id) DO UPDATE SET
                rows = EXCLUDED.rows,
                cols = EXCLUDED.cols,
                grid = EXCLUDED.grid
            """
        ),
        {
            "id": puzzle_id,
            "rows": puzzle["rows"],
            "cols": puzzle["cols"],
            "grid": json.dumps(grid),
        },
    )

    for word_entry in words:
        await session.execute(
            text(
                """
                INSERT INTO word_hunt_words (
                    puzzle_id,
                    word,
                    clue,
                    start_row,
                    start_col,
                    end_row,
                    end_col
                )
                VALUES (
                    :puzzle_id,
                    :word,
                    :clue,
                    :start_row,
                    :start_col,
                    :end_row,
                    :end_col
                )
                ON CONFLICT (puzzle_id, word) DO UPDATE SET
                    clue = EXCLUDED.clue,
                    start_row = EXCLUDED.start_row,
                    start_col = EXCLUDED.start_col,
                    end_row = EXCLUDED.end_row,
                    end_col = EXCLUDED.end_col
                """
            ),
            {
                "puzzle_id": puzzle_id,
                "word": word_entry["word"],
                "clue": word_entry["clue"],
                "start_row": word_entry["start_row"],
                "start_col": word_entry["start_col"],
                "end_row": word_entry["end_row"],
                "end_col": word_entry["end_col"],
            },
        )

    await session.commit()
    logger.info("seed.word_hunt.done", puzzle_id=puzzle_id, word_count=len(words))


async def _seed_crossword(session: AsyncSession) -> None:
    path = DATA_DIR / "crossword.json"
    if not path.exists():
        logger.warning("seed.crossword.missing", path=str(path))
        return

    payload = json.loads(path.read_text())
    puzzle = payload["puzzle"]
    entries = payload["entries"]
    grid = puzzle["grid"]

    for entry in entries:
        if not validate_seeded_entry(
            grid,
            entry["answer"],
            entry["start_row"],
            entry["start_col"],
            entry["direction"],
        ):
            raise ValueError(
                f"crossword seed validation failed for entry {entry['answer']!r}"
            )

    validate_grid_consistency(grid, entries)

    puzzle_id = puzzle.get("id", "22222222-2222-2222-2222-222222222222")
    await session.execute(
        text(
            """
            INSERT INTO crossword_puzzles (id, rows, cols, grid)
            VALUES (:id, :rows, :cols, CAST(:grid AS jsonb))
            ON CONFLICT (id) DO UPDATE SET
                rows = EXCLUDED.rows,
                cols = EXCLUDED.cols,
                grid = EXCLUDED.grid
            """
        ),
        {
            "id": puzzle_id,
            "rows": puzzle["rows"],
            "cols": puzzle["cols"],
            "grid": json.dumps(grid),
        },
    )

    for entry in entries:
        await session.execute(
            text(
                """
                INSERT INTO crossword_entries (
                    puzzle_id,
                    number,
                    direction,
                    start_row,
                    start_col,
                    answer,
                    clue
                )
                VALUES (
                    :puzzle_id,
                    :number,
                    :direction,
                    :start_row,
                    :start_col,
                    :answer,
                    :clue
                )
                ON CONFLICT (puzzle_id, number, direction) DO UPDATE SET
                    start_row = EXCLUDED.start_row,
                    start_col = EXCLUDED.start_col,
                    answer = EXCLUDED.answer,
                    clue = EXCLUDED.clue
                """
            ),
            {
                "puzzle_id": puzzle_id,
                "number": entry["number"],
                "direction": entry["direction"],
                "start_row": entry["start_row"],
                "start_col": entry["start_col"],
                "answer": entry["answer"],
                "clue": entry["clue"],
            },
        )

    await session.commit()
    logger.info("seed.crossword.done", puzzle_id=puzzle_id, entry_count=len(entries))

