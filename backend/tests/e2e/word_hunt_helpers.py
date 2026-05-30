"""Shared helpers for Word Hunt end-to-end API journeys."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from leap.api.main import app
from leap.config.settings import get_settings
from leap.games.word_hunt.scoring import compute_final_score, compute_time_bonus
from tests.e2e.conftest import E2E_POSTGRES_URL

_WORD_HUNT_JSON = Path(__file__).resolve().parents[2] / "leap" / "seeds" / "data" / "word_hunt.json"


def auth_headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def login(client: httpx.AsyncClient, corp_id: str) -> str:
    r = await client.post(
        "/auth/login",
        json={"corp_id": corp_id, "event_code": get_settings().EVENT_CODE},
    )
    assert r.status_code == 200, r.text
    return str(r.json()["access_token"])


async def insert_player(player_id: str, display_name: str) -> None:
    engine = create_async_engine(E2E_POSTGRES_URL)
    try:
        async with engine.begin() as conn:
            await conn.execute(
                text(
                    "INSERT INTO players (id, display_name) VALUES (:id, :display_name)",
                ),
                {"id": player_id, "display_name": display_name},
            )
    finally:
        await engine.dispose()


async def fetch_seeded_words() -> List[dict]:
    """Return seeded words ordered by start position (stable play order)."""
    engine = create_async_engine(E2E_POSTGRES_URL)
    try:
        async with engine.connect() as conn:
            rows = (
                await conn.execute(
                    text(
                        """
                        SELECT id, word, clue, start_row, start_col, end_row, end_col
                        FROM word_hunt_words
                        ORDER BY start_row, start_col, word
                        """,
                    ),
                )
            ).all()
            return [
                {
                    "word_id": str(row[0]),
                    "word": str(row[1]),
                    "clue": str(row[2]),
                    "start_row": int(row[3]),
                    "start_col": int(row[4]),
                    "end_row": int(row[5]),
                    "end_col": int(row[6]),
                }
                for row in rows
            ]
    finally:
        await engine.dispose()


async def fetch_puzzle_dims() -> Tuple[int, int]:
    engine = create_async_engine(E2E_POSTGRES_URL)
    try:
        async with engine.connect() as conn:
            row = (
                await conn.execute(text("SELECT rows, cols FROM word_hunt_puzzles LIMIT 1"))
            ).one()
            return int(row[0]), int(row[1])
    finally:
        await engine.dispose()


async def count_finds_for_player(player_id: str) -> int:
    engine = create_async_engine(E2E_POSTGRES_URL)
    try:
        async with engine.connect() as conn:
            return int(
                (
                    await conn.execute(
                        text(
                            """
                            SELECT COUNT(*)
                            FROM word_hunt_finds f
                            JOIN game_sessions gs ON gs.id = f.session_id
                            WHERE gs.player_id = :player_id
                              AND gs.game_id = 'word_hunt'
                            """,
                        ),
                        {"player_id": player_id},
                    )
                ).scalar_one(),
            )
    finally:
        await engine.dispose()


async def fetch_persisted_session_score(player_id: str) -> Optional[int]:
    engine = create_async_engine(E2E_POSTGRES_URL)
    try:
        async with engine.connect() as conn:
            row = (
                await conn.execute(
                    text(
                        """
                        SELECT score FROM game_sessions
                        WHERE player_id = :player_id AND game_id = 'word_hunt'
                        """,
                    ),
                    {"player_id": player_id},
                )
            ).one_or_none()
            return None if row is None else int(row[0])
    finally:
        await engine.dispose()


def load_seed_word_count() -> int:
    payload = json.loads(_WORD_HUNT_JSON.read_text())
    return len(payload["words"])


def word_hunt_session_row(sessions: List[dict]) -> Optional[dict]:
    for row in sessions:
        if row["game_id"] == "word_hunt":
            return row
    return None


async def get_my_sessions(client: httpx.AsyncClient, headers: Dict[str, str]) -> List[dict]:
    r = await client.get("/players/me/sessions", headers=headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert isinstance(body, list)
    return body


def assert_no_unfound_word_text_in_payload(payload: Any, unfound_words: List[str]) -> None:
    """Unfound answer strings must never appear anywhere in a serialized response."""
    serialized = json.dumps(payload)
    for word in unfound_words:
        assert word not in serialized, f"Unfound word {word!r} leaked in response"


def assert_clues_hide_unfound_words(clues: List[dict]) -> None:
    for clue in clues:
        if not clue["found"]:
            assert clue.get("word") is None
            assert clue.get("coordinates") is None


def install_word_hunt_deterministic_controls(
    *,
    terminal_elapsed_ms: int = 0,
) -> Tuple[Callable[[datetime], None], Callable[[], None], Callable[[], None], Callable[[], None]]:
    """Patch Word Hunt service clock.

    After ``play``, call ``bind_session_start(started_at)`` with the puzzle's
    ``started_at`` so elapsed time is computed relative to the real session row.
    Call ``advance_to_terminal`` immediately before the terminal ``find``/``submit``.
    Call ``reset_terminal`` between back-to-back terminal actions for different sessions.
    """
    session_start = [datetime.now(timezone.utc)]
    at_terminal = [False]

    def bind_session_start(started_at: datetime) -> None:
        if started_at.tzinfo is None:
            started_at = started_at.replace(tzinfo=timezone.utc)
        session_start[0] = started_at
        at_terminal[0] = False

    def _clock() -> datetime:
        if at_terminal[0]:
            return session_start[0] + timedelta(milliseconds=terminal_elapsed_ms)
        return session_start[0]

    def advance_to_terminal() -> None:
        at_terminal[0] = True

    def reset_terminal() -> None:
        at_terminal[0] = False

    original_clock = app.state.container.word_hunt._clock
    app.state.container.word_hunt._clock = _clock

    def restore() -> None:
        app.state.container.word_hunt._clock = original_clock

    return bind_session_start, advance_to_terminal, reset_terminal, restore


def parse_started_at(play_body: dict) -> datetime:
    puzzle = play_body["puzzle"]
    assert puzzle is not None
    raw = str(puzzle["started_at"])
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    return datetime.fromisoformat(raw)


async def submit_find(
    client: httpx.AsyncClient,
    headers: Dict[str, str],
    *,
    start_row: int,
    start_col: int,
    end_row: int,
    end_col: int,
    expect_status: int = 200,
) -> dict:
    r = await client.post(
        "/games/word-hunt/find",
        headers=headers,
        json={
            "start_row": start_row,
            "start_col": start_col,
            "end_row": end_row,
            "end_col": end_col,
        },
    )
    assert r.status_code == expect_status, r.text
    return r.json()


async def submit_session(
    client: httpx.AsyncClient,
    headers: Dict[str, str],
    *,
    expect_status: int = 200,
) -> dict:
    r = await client.post("/games/word-hunt/submit", headers=headers)
    assert r.status_code == expect_status, r.text
    return r.json()


async def play_word_hunt(
    client: httpx.AsyncClient,
    headers: Dict[str, str],
) -> dict:
    r = await client.post("/games/word-hunt/play", headers=headers)
    assert r.status_code == 200, r.text
    return r.json()


async def find_word_by_coords(
    client: httpx.AsyncClient,
    headers: Dict[str, str],
    word_entry: dict,
) -> dict:
    return await submit_find(
        client,
        headers,
        start_row=word_entry["start_row"],
        start_col=word_entry["start_col"],
        end_row=word_entry["end_row"],
        end_col=word_entry["end_col"],
    )


async def restore_word_hunt_production_seed() -> None:
    from leap.seeds.loader import _seed_word_hunt

    engine = create_async_engine(E2E_POSTGRES_URL)
    try:
        async with engine.begin() as conn:
            await conn.execute(text("DELETE FROM word_hunt_words"))
            await conn.execute(text("DELETE FROM word_hunt_puzzles"))
    finally:
        await engine.dispose()

    async with app.state.container.context_manager.session() as session:
        await _seed_word_hunt(session)
        await app.state.container.word_hunt.initialize(session)


async def install_collision_puzzle() -> None:
    """Replace the seeded puzzle with a 5×5 grid where CAT appears twice linearly."""
    puzzle_id = "22222222-2222-2222-2222-222222222222"
    grid = [
        ["C", "A", "T", "X", "X"],
        ["A", "X", "X", "X", "X"],
        ["T", "X", "X", "X", "X"],
        ["X", "X", "X", "X", "X"],
        ["X", "X", "X", "X", "X"],
    ]

    engine = create_async_engine(E2E_POSTGRES_URL)
    try:
        async with engine.begin() as conn:
            await conn.execute(text("DELETE FROM word_hunt_words"))
            await conn.execute(text("DELETE FROM word_hunt_puzzles"))
            await conn.execute(
                text(
                    """
                    INSERT INTO word_hunt_puzzles (id, rows, cols, grid)
                    VALUES (:id, :rows, :cols, CAST(:grid AS jsonb))
                    """,
                ),
                {
                    "id": puzzle_id,
                    "rows": 5,
                    "cols": 5,
                    "grid": json.dumps(grid),
                },
            )
            await conn.execute(
                text(
                    """
                    INSERT INTO word_hunt_words (
                        id, puzzle_id, word, clue,
                        start_row, start_col, end_row, end_col
                    )
                    VALUES (
                        :id, :puzzle_id, :word, :clue,
                        :start_row, :start_col, :end_row, :end_col
                    )
                    """,
                ),
                {
                    "id": "33333333-3333-3333-3333-333333333333",
                    "puzzle_id": puzzle_id,
                    "word": "CAT",
                    "clue": "Small furry predator.",
                    "start_row": 0,
                    "start_col": 0,
                    "end_row": 0,
                    "end_col": 2,
                },
            )
    finally:
        await engine.dispose()

    async with app.state.container.context_manager.session() as session:
        await app.state.container.word_hunt.initialize(session)


def expected_terminal_score(found_count: int, elapsed_ms: int) -> int:
    return compute_final_score(found_count, elapsed_ms)


def expected_time_bonus(elapsed_ms: int) -> int:
    return compute_time_bonus(elapsed_ms)
