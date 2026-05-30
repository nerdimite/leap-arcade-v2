"""End-to-end Four Pics API journeys: full-pool playthrough, lobby, leaderboard."""

from __future__ import annotations

from typing import Dict, List, Optional, Set

import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from leap.config.settings import get_settings
from leap.games.four_pics.scoring import FOUR_PICS_BASE_SCORE, FOUR_PICS_TIME_BONUS_MAX
from tests.e2e.conftest import E2E_POSTGRES_URL
from tests.unit.api.four_pics.assertions import assert_no_odd_one_out_index_in_payload

_PLAYER_ID = "e2e_fp_happy"


def _auth_headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def _login(client: httpx.AsyncClient, corp_id: str) -> str:
    r = await client.post(
        "/auth/login",
        json={"corp_id": corp_id, "event_code": get_settings().EVENT_CODE},
    )
    assert r.status_code == 200, r.text
    return str(r.json()["access_token"])


async def _insert_player(player_id: str, display_name: str) -> None:
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


async def _fetch_odd_one_out_index(question_id: str) -> int:
    engine = create_async_engine(E2E_POSTGRES_URL)
    try:
        async with engine.connect() as conn:
            row = (
                await conn.execute(
                    text(
                        "SELECT odd_one_out_index FROM four_pics_questions WHERE id = :id",
                    ),
                    {"id": question_id},
                )
            ).one()
            return int(row[0])
    finally:
        await engine.dispose()


async def _fetch_pool_size() -> int:
    engine = create_async_engine(E2E_POSTGRES_URL)
    try:
        async with engine.connect() as conn:
            return int(
                (await conn.execute(text("SELECT COUNT(*) FROM four_pics_questions"))).scalar_one(),
            )
    finally:
        await engine.dispose()


def _four_pics_session_row(sessions: List[dict]) -> Optional[dict]:
    for row in sessions:
        if row["game_id"] == "four_pics":
            return row
    return None


async def _get_my_sessions(client: httpx.AsyncClient, headers: Dict[str, str]) -> List[dict]:
    r = await client.get("/players/me/sessions", headers=headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert isinstance(body, list)
    return body


def _wrong_index(correct_index: int) -> int:
    return (correct_index + 1) % 4


async def test_full_pool_happy_path_completed_lobby_and_leaderboard(
    client: httpx.AsyncClient,
) -> None:
    """Login → play all seeded questions (mix correct/wrong) → lobby completed → leaderboard."""
    await _insert_player(_PLAYER_ID, "E2E Four Pics Happy")
    token = await _login(client, _PLAYER_ID)
    h = _auth_headers(token)

    pool_size = await _fetch_pool_size()
    assert pool_size >= 3

    before_sessions = await _get_my_sessions(client, h)
    assert _four_pics_session_row(before_sessions) is None

    play_first = await client.post("/games/four-pics/play", headers=h)
    assert play_first.status_code == 200, play_first.text
    play_body = play_first.json()
    assert_no_odd_one_out_index_in_payload(play_body)
    assert play_body["session_status"] == "active"
    assert play_body["session_score"] == 0
    question = play_body["question"]
    assert question is not None
    assert len(question["image_paths"]) == 4
    total_questions = question["total_questions"]
    assert total_questions == pool_size

    seen_ids: Set[str] = set()
    answer_index = 0
    running_score = 0
    last: Optional[dict] = None

    while question is not None:
        qid = str(question["question_id"])
        assert qid not in seen_ids
        seen_ids.add(qid)

        correct_index = await _fetch_odd_one_out_index(qid)
        want_correct = answer_index % 2 == 0
        selected = correct_index if want_correct else _wrong_index(correct_index)

        ans = await client.post(
            "/games/four-pics/answer",
            headers=h,
            json={"question_id": qid, "selected_index": selected, "time_ms": 0},
        )
        assert ans.status_code == 200, ans.text
        body = ans.json()
        assert_no_odd_one_out_index_in_payload(body)
        assert body["correct"] is want_correct

        if want_correct:
            assert (
                FOUR_PICS_BASE_SCORE
                <= body["score"]
                <= FOUR_PICS_BASE_SCORE + FOUR_PICS_TIME_BONUS_MAX
            )
            assert 0 <= body["time_bonus"] <= FOUR_PICS_TIME_BONUS_MAX
        else:
            assert body["score"] == 0
            assert body["time_bonus"] == 0

        running_score += int(body["score"])
        assert body["session_score"] == running_score

        if body.get("result") is not None:
            assert body["session_status"] == "completed"
            assert body["question"] is None
            last = body
            break

        assert body["session_status"] == "active"
        question = body["question"]
        assert question is not None
        answer_index += 1

    assert last is not None
    result = last["result"]
    assert isinstance(result, dict)
    assert len(seen_ids) == total_questions
    assert last["session_score"] == running_score

    expected_min = sum(FOUR_PICS_BASE_SCORE if i % 2 == 0 else 0 for i in range(total_questions))
    expected_max = sum(
        (FOUR_PICS_BASE_SCORE + FOUR_PICS_TIME_BONUS_MAX if i % 2 == 0 else 0)
        for i in range(total_questions)
    )
    assert expected_min <= last["session_score"] <= expected_max

    after_sessions = await _get_my_sessions(client, h)
    fp_row = _four_pics_session_row(after_sessions)
    assert fp_row is not None
    assert fp_row["status"] == "completed"
    assert fp_row["score"] == last["session_score"]

    board = await client.get("/leaderboard", headers=h)
    assert board.status_code == 200, board.text
    entry = next(e for e in board.json()["entries"] if e["player_id"] == _PLAYER_ID)
    assert entry["total_score"] == last["session_score"]
    assert entry["games_completed"] == 1

    replay_play = await client.post("/games/four-pics/play", headers=h)
    assert replay_play.status_code == 200, replay_play.text
    replay_body = replay_play.json()
    assert replay_body["session_status"] == "completed"
    assert replay_body["question"] is None
    assert replay_body["result"] is not None
    assert replay_body["result"]["score"] == last["session_score"]
