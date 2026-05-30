"""Shared helpers for Crossword end-to-end API journeys."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, List, Optional, Tuple

import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from leap.api.main import app
from leap.config.settings import get_settings
from leap.games.crossword.scoring import compute_final_score, compute_time_bonus
from tests.e2e.conftest import E2E_POSTGRES_URL

E2E_PUZZLE_ID = "cccccccc-cccc-cccc-cccc-cccccccccccc"
E2E_ENTRY_ACROSS_ID = "cccccccc-cccc-cccc-cccc-cccccccccc01"
E2E_ENTRY_DOWN_ID = "cccccccc-cccc-cccc-cccc-cccccccccc02"
_UNKNOWN_ENTRY_ID = "00000000-0000-0000-0000-000000000099"


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


async def fetch_seeded_entries() -> List[dict]:
    """Return seeded entries ordered for stable play (across before down)."""
    engine = create_async_engine(E2E_POSTGRES_URL)
    try:
        async with engine.connect() as conn:
            rows = (
                await conn.execute(
                    text(
                        """
                        SELECT id, answer, clue, number, direction,
                               start_row, start_col
                        FROM crossword_entries
                        WHERE puzzle_id = :puzzle_id
                        ORDER BY number, direction DESC
                        """,
                    ),
                    {"puzzle_id": E2E_PUZZLE_ID},
                )
            ).all()
            return [
                {
                    "entry_id": str(row[0]),
                    "answer": str(row[1]),
                    "clue": str(row[2]),
                    "number": int(row[3]),
                    "direction": str(row[4]),
                    "start_row": int(row[5]),
                    "start_col": int(row[6]),
                }
                for row in rows
            ]
    finally:
        await engine.dispose()


async def fetch_entry_count() -> int:
    entries = await fetch_seeded_entries()
    return len(entries)


async def count_solves_for_player(player_id: str) -> int:
    engine = create_async_engine(E2E_POSTGRES_URL)
    try:
        async with engine.connect() as conn:
            return int(
                (
                    await conn.execute(
                        text(
                            """
                            SELECT COUNT(*)
                            FROM crossword_solves cs
                            JOIN game_sessions gs ON gs.id = cs.session_id
                            WHERE gs.player_id = :player_id
                              AND gs.game_id = 'crossword'
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
                        WHERE player_id = :player_id AND game_id = 'crossword'
                        """,
                    ),
                    {"player_id": player_id},
                )
            ).one_or_none()
            return None if row is None else int(row[0])
    finally:
        await engine.dispose()


def crossword_session_row(sessions: List[dict]) -> Optional[dict]:
    for row in sessions:
        if row["game_id"] == "crossword":
            return row
    return None


async def get_my_sessions(client: httpx.AsyncClient, headers: Dict[str, str]) -> List[dict]:
    r = await client.get("/players/me/sessions", headers=headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert isinstance(body, list)
    return body


def unsolved_answers(entries: List[dict], solved_entry_ids: set[str]) -> List[str]:
    return [e["answer"] for e in entries if e["entry_id"] not in solved_entry_ids]


def assert_no_unsolved_answer_text_in_payload(
    payload: Any,
    unsolved_answers: List[str],
) -> None:
    """Unsolved answer strings must never appear anywhere in a serialized response."""
    serialized = json.dumps(payload)
    for answer in unsolved_answers:
        assert answer not in serialized, f"Unsolved answer {answer!r} leaked in response"


def assert_skeleton_has_no_letters(puzzle: dict) -> None:
    for row in puzzle["cells"]:
        for cell in row:
            if cell is not None:
                assert cell.get("letter") is None


def assert_clues_hide_unsolved_entries(clues: List[dict]) -> None:
    for clue in clues:
        if not clue["solved"]:
            assert clue.get("answer") is None
            assert clue.get("cells") is None


def install_crossword_deterministic_controls(
    *,
    terminal_elapsed_ms: int = 0,
) -> Tuple[Callable[[datetime], None], Callable[[], None], Callable[[], None], Callable[[], None]]:
    """Patch Crossword service clock (same pattern as Word Hunt e2e)."""
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

    original_clock = app.state.container.crossword._clock
    app.state.container.crossword._clock = _clock

    def restore() -> None:
        app.state.container.crossword._clock = original_clock

    return bind_session_start, advance_to_terminal, reset_terminal, restore


def parse_started_at(play_body: dict) -> datetime:
    puzzle = play_body["puzzle"]
    assert puzzle is not None
    raw = str(puzzle["started_at"])
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    return datetime.fromisoformat(raw)


async def install_e2e_crossword_puzzle() -> None:
    """Replace production crossword with a 3×3 grid (FOO across ∩ FIZ down at 0,0)."""
    grid = [
        ["F", "O", "O"],
        ["I", None, None],
        ["Z", None, None],
    ]
    engine = create_async_engine(E2E_POSTGRES_URL)
    try:
        async with engine.begin() as conn:
            await conn.execute(text("DELETE FROM crossword_entries"))
            await conn.execute(text("DELETE FROM crossword_puzzles"))
            await conn.execute(
                text(
                    """
                    INSERT INTO crossword_puzzles (id, rows, cols, grid)
                    VALUES (:id, :rows, :cols, CAST(:grid AS jsonb))
                    """,
                ),
                {
                    "id": E2E_PUZZLE_ID,
                    "rows": 3,
                    "cols": 3,
                    "grid": json.dumps(grid),
                },
            )
            await conn.execute(
                text(
                    """
                    INSERT INTO crossword_entries (
                        id, puzzle_id, number, direction,
                        start_row, start_col, answer, clue
                    )
                    VALUES (
                        :id, :puzzle_id, :number, :direction,
                        :start_row, :start_col, :answer, :clue
                    )
                    """,
                ),
                {
                    "id": E2E_ENTRY_ACROSS_ID,
                    "puzzle_id": E2E_PUZZLE_ID,
                    "number": 1,
                    "direction": "across",
                    "start_row": 0,
                    "start_col": 0,
                    "answer": "FOO",
                    "clue": "E2E across: sounds like a cry of discovery.",
                },
            )
            await conn.execute(
                text(
                    """
                    INSERT INTO crossword_entries (
                        id, puzzle_id, number, direction,
                        start_row, start_col, answer, clue
                    )
                    VALUES (
                        :id, :puzzle_id, :number, :direction,
                        :start_row, :start_col, :answer, :clue
                    )
                    """,
                ),
                {
                    "id": E2E_ENTRY_DOWN_ID,
                    "puzzle_id": E2E_PUZZLE_ID,
                    "number": 1,
                    "direction": "down",
                    "start_row": 0,
                    "start_col": 0,
                    "answer": "FIZ",
                    "clue": "E2E down: carbonated drink, informally.",
                },
            )
    finally:
        await engine.dispose()

    async with app.state.container.context_manager.session() as session:
        await app.state.container.crossword.initialize(session)


async def restore_crossword_production_seed() -> None:
    from leap.seeds.loader import _seed_crossword

    engine = create_async_engine(E2E_POSTGRES_URL)
    try:
        async with engine.begin() as conn:
            await conn.execute(text("DELETE FROM crossword_entries"))
            await conn.execute(text("DELETE FROM crossword_puzzles"))
    finally:
        await engine.dispose()

    async with app.state.container.context_manager.session() as session:
        await _seed_crossword(session)
        await app.state.container.crossword.initialize(session)


async def play_crossword(
    client: httpx.AsyncClient,
    headers: Dict[str, str],
    *,
    expect_status: int = 200,
) -> dict:
    r = await client.post("/games/crossword/play", headers=headers)
    assert r.status_code == expect_status, r.text
    return r.json()


async def check_entry(
    client: httpx.AsyncClient,
    headers: Dict[str, str],
    entry_id: str,
    letters: str,
    *,
    expect_status: int = 200,
) -> dict:
    r = await client.post(
        "/games/crossword/check",
        headers=headers,
        json={"entry_id": entry_id, "letters": letters},
    )
    assert r.status_code == expect_status, r.text
    return r.json()


async def submit_session(
    client: httpx.AsyncClient,
    headers: Dict[str, str],
    *,
    expect_status: int = 200,
) -> dict:
    r = await client.post("/games/crossword/submit", headers=headers)
    assert r.status_code == expect_status, r.text
    return r.json()


def expected_terminal_score(solved_count: int, elapsed_ms: int) -> int:
    return compute_final_score(solved_count, elapsed_ms)


def expected_time_bonus(elapsed_ms: int) -> int:
    return compute_time_bonus(elapsed_ms)


async def assert_completed_lobby_and_leaderboard(
    client: httpx.AsyncClient,
    headers: Dict[str, str],
    player_id: str,
    expected_score: int,
) -> None:
    sessions = await get_my_sessions(client, headers)
    row = crossword_session_row(sessions)
    assert row is not None
    assert row["status"] == "completed"
    assert row["score"] == expected_score

    board = await client.get("/leaderboard", headers=headers)
    assert board.status_code == 200, board.text
    entry = next(e for e in board.json()["entries"] if e["player_id"] == player_id)
    assert entry["total_score"] == expected_score
