"""Shared helpers for Pinpoint end-to-end API journeys."""

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
from leap.games.pinpoint.scoring import base_score_for_clues, compute_time_bonus
from tests.e2e.conftest import E2E_POSTGRES_URL

_PINPOINT_JSON = (
    Path(__file__).resolve().parents[2] / "leap" / "seeds" / "data" / "pinpoint.json"
)
_WRONG_GUESS = "definitely-not-the-answer"


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


async def fetch_pool_size() -> int:
    engine = create_async_engine(E2E_POSTGRES_URL)
    try:
        async with engine.connect() as conn:
            return int(
                (
                    await conn.execute(text("SELECT COUNT(*) FROM pinpoint_puzzles"))
                ).scalar_one(),
            )
    finally:
        await engine.dispose()


async def fetch_puzzle_ids_ordered() -> List[str]:
    engine = create_async_engine(E2E_POSTGRES_URL)
    try:
        async with engine.connect() as conn:
            rows = (
                await conn.execute(
                    text("SELECT id FROM pinpoint_puzzles ORDER BY id"),
                )
            ).all()
            return [str(row[0]) for row in rows]
    finally:
        await engine.dispose()


async def fetch_puzzle_answer(puzzle_id: str) -> str:
    engine = create_async_engine(E2E_POSTGRES_URL)
    try:
        async with engine.connect() as conn:
            row = (
                await conn.execute(
                    text("SELECT answer FROM pinpoint_puzzles WHERE id = :id"),
                    {"id": puzzle_id},
                )
            ).one()
            return str(row[0])
    finally:
        await engine.dispose()


def assert_no_answer_fields_in_payload(payload: Any) -> None:
    """Canonical answer fields must never appear in serialized responses."""
    if isinstance(payload, dict):
        assert "answer" not in payload
        assert "answer_aliases" not in payload
        for value in payload.values():
            assert_no_answer_fields_in_payload(value)
    elif isinstance(payload, list):
        for item in payload:
            assert_no_answer_fields_in_payload(item)


def pinpoint_session_row(sessions: List[dict]) -> Optional[dict]:
    for row in sessions:
        if row["game_id"] == "pinpoint":
            return row
    return None


async def get_my_sessions(client: httpx.AsyncClient, headers: Dict[str, str]) -> List[dict]:
    r = await client.get("/players/me/sessions", headers=headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert isinstance(body, list)
    return body


def install_pinpoint_deterministic_controls(
    *,
    elapsed_per_solve_ms: int = 0,
) -> Tuple[Callable[[], datetime], Callable[[], None]]:
    """Patch Pinpoint service clock and puzzle pick order for deterministic e2e runs.

    ``submit_guess`` invokes ``_now()`` on every guess (including wrong ones), so an
    advancing clock would burn ticks on red herrings and collapse time bonus. A fixed
    clock keeps ``elapsed_ms == 0`` for every scored guess, yielding a stable
    ``time_bonus`` of ``100`` (see ``compute_time_bonus(0)``).
    """
    import leap.games.pinpoint.service as pinpoint_service_mod

    base = datetime(2026, 5, 26, 12, 0, 0, tzinfo=timezone.utc)

    def _clock() -> datetime:
        return base + timedelta(milliseconds=elapsed_per_solve_ms)

    original_clock = app.state.container.pinpoint._clock
    original_choice = pinpoint_service_mod.random.choice

    app.state.container.pinpoint._clock = _clock
    pinpoint_service_mod.random.choice = lambda seq: sorted(seq, key=lambda p: p.id)[0]

    def restore() -> None:
        app.state.container.pinpoint._clock = original_clock
        pinpoint_service_mod.random.choice = original_choice

    return _clock, restore


def expected_solve_score(clues_revealed: int, elapsed_ms: int) -> int:
    return base_score_for_clues(clues_revealed) + compute_time_bonus(elapsed_ms)


async def submit_guess(
    client: httpx.AsyncClient,
    headers: Dict[str, str],
    puzzle_id: str,
    guess: str,
) -> dict:
    r = await client.post(
        "/games/pinpoint/guess",
        headers=headers,
        json={"puzzle_id": puzzle_id, "guess": guess},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert_no_answer_fields_in_payload(body)
    return body


async def solve_puzzle_on_clue(
    client: httpx.AsyncClient,
    headers: Dict[str, str],
    puzzle_id: str,
    *,
    on_clue: int,
    answer: str,
) -> dict:
    """Submit wrong guesses until ``on_clue`` clues are visible, then the correct answer."""
    assert 1 <= on_clue <= 5
    last: dict = {}
    for _ in range(on_clue - 1):
        last = await submit_guess(client, headers, puzzle_id, _WRONG_GUESS)
        assert last["correct"] is False
    last = await submit_guess(client, headers, puzzle_id, answer)
    assert last["correct"] is True
    assert last["puzzle"]["clues_revealed"] == on_clue
    return last


async def fail_puzzle(
    client: httpx.AsyncClient,
    headers: Dict[str, str],
    puzzle_id: str,
) -> dict:
    """Exhaust all five clues with wrong guesses."""
    last: dict = {}
    for i in range(5):
        last = await submit_guess(client, headers, puzzle_id, f"{_WRONG_GUESS}-{i}")
        if i < 4:
            assert last["correct"] is False
    assert last["correct"] is False
    assert last["puzzle"]["status"] == "failed"
    assert last["puzzle"]["time_bonus"] is None
    assert last["puzzle"]["score"] == 0
    return last


def load_seed_puzzle_count() -> int:
    return len(json.loads(_PINPOINT_JSON.read_text()))
