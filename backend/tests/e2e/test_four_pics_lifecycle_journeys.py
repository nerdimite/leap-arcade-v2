"""Four Pics lifecycle e2e journeys: abandon, refresh idempotency, replay protection."""

from __future__ import annotations

from typing import Dict, Optional, Set

import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from leap.config.settings import get_settings
from tests.e2e.conftest import E2E_POSTGRES_URL
from tests.unit.api.four_pics.assertions import assert_no_odd_one_out_index_in_payload


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


def _four_pics_session_row(sessions: list[dict]) -> Optional[dict]:
    for row in sessions:
        if row["game_id"] == "four_pics":
            return row
    return None


async def _get_my_sessions(client: httpx.AsyncClient, headers: Dict[str, str]) -> list[dict]:
    r = await client.get("/players/me/sessions", headers=headers)
    assert r.status_code == 200, r.text
    return r.json()


async def _answer_question(
    client: httpx.AsyncClient,
    headers: Dict[str, str],
    question_id: str,
    *,
    correct: bool,
) -> dict:
    correct_index = await _fetch_odd_one_out_index(question_id)
    selected = correct_index if correct else (correct_index + 1) % 4
    r = await client.post(
        "/games/four-pics/answer",
        headers=headers,
        json={"question_id": question_id, "selected_index": selected, "time_ms": 500},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert_no_odd_one_out_index_in_payload(body)
    return body


async def test_abandon_mid_session_partial_score_tile_abandoned_play_answer_blocked(
    client: httpx.AsyncClient,
) -> None:
    """Abandon after two answers; partial score persists; terminal play/answer behaviour."""
    player_id = "e2e_fp_abandon"
    await _insert_player(player_id, "E2E Four Pics Abandon")
    token = await _login(client, player_id)
    h = _auth_headers(token)
    pool_size = await _fetch_pool_size()

    play = await client.post("/games/four-pics/play", headers=h)
    assert play.status_code == 200, play.text
    play_body = play.json()
    assert_no_odd_one_out_index_in_payload(play_body)
    question = play_body["question"]
    assert question is not None

    partial_score = 0
    qid = str(question["question_id"])
    body = await _answer_question(client, h, qid, correct=True)
    partial_score = int(body["session_score"])
    assert body.get("result") is None
    next_question = body.get("question")
    assert next_question is not None

    abandon = await client.post("/games/four-pics/abandon", headers=h)
    assert abandon.status_code == 200, abandon.text
    abandon_body = abandon.json()
    result = abandon_body["result"]
    assert result["score"] == partial_score
    assert result["questions_not_reached"] > 0
    assert result["questions_not_reached"] == sum(
        1 for row in result["questions"] if row["status"] == "not_reached"
    )
    assert len(result["questions"]) == pool_size

    sessions = await _get_my_sessions(client, h)
    fp_row = _four_pics_session_row(sessions)
    assert fp_row is not None
    assert fp_row["status"] == "abandoned"
    assert fp_row["score"] == partial_score

    resumed = await client.post("/games/four-pics/play", headers=h)
    assert resumed.status_code == 200, resumed.text
    resumed_body = resumed.json()
    assert resumed_body["session_status"] == "abandoned"
    assert resumed_body["question"] is None
    assert resumed_body["result"] is not None

    blocked = await client.post(
        "/games/four-pics/answer",
        headers=h,
        json={"question_id": str(next_question["question_id"]), "selected_index": 0, "time_ms": 0},
    )
    assert blocked.status_code == 409


async def test_refresh_mid_question_play_idempotent(client: httpx.AsyncClient) -> None:
    """Two consecutive /play calls with no answer return the same active question."""
    player_id = "e2e_fp_refresh"
    await _insert_player(player_id, "E2E Four Pics Refresh")
    token = await _login(client, player_id)
    h = _auth_headers(token)

    r1 = await client.post("/games/four-pics/play", headers=h)
    assert r1.status_code == 200, r1.text
    b1 = r1.json()
    assert_no_odd_one_out_index_in_payload(b1)
    assert b1["session_status"] == "active"
    q1 = b1["question"]
    assert q1 is not None

    r2 = await client.post("/games/four-pics/play", headers=h)
    assert r2.status_code == 200, r2.text
    b2 = r2.json()
    assert_no_odd_one_out_index_in_payload(b2)
    q2 = b2["question"]
    assert q2 is not None
    assert q2["question_id"] == q1["question_id"]
    assert q2["started_at"] == q1["started_at"]


async def test_replay_protection_after_completion_play_returns_result_answer_409(
    client: httpx.AsyncClient,
) -> None:
    """Completed session: /play surfaces result; further /answer is rejected."""
    player_id = "e2e_fp_replay"
    await _insert_player(player_id, "E2E Four Pics Replay")
    token = await _login(client, player_id)
    h = _auth_headers(token)
    pool_size = await _fetch_pool_size()

    play = await client.post("/games/four-pics/play", headers=h)
    assert play.status_code == 200, play.text
    question = play.json()["question"]
    assert question is not None

    seen: Set[str] = set()
    last_qid: Optional[str] = None
    final_score = 0

    while question is not None:
        qid = str(question["question_id"])
        seen.add(qid)
        last_qid = qid
        body = await _answer_question(client, h, qid, correct=True)
        final_score = int(body["session_score"])
        if body.get("result") is not None:
            assert body["session_status"] == "completed"
            break
        question = body.get("question")

    assert len(seen) == pool_size

    replay_play = await client.post("/games/four-pics/play", headers=h)
    assert replay_play.status_code == 200, replay_play.text
    replay_body = replay_play.json()
    assert replay_body["session_status"] == "completed"
    assert replay_body["question"] is None
    assert replay_body["result"] is not None
    assert replay_body["result"]["score"] == final_score

    assert last_qid is not None
    blocked = await client.post(
        "/games/four-pics/answer",
        headers=h,
        json={"question_id": last_qid, "selected_index": 0, "time_ms": 0},
    )
    assert blocked.status_code == 409
