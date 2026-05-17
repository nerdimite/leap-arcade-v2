"""Session lifecycle e2e journeys: abandon, resume, repeat /play idempotency."""

from __future__ import annotations

import os
from typing import Dict

import httpx


async def _login(client: httpx.AsyncClient, corp_id: str) -> str:
    r = await client.post(
        "/auth/login",
        json={
            "corp_id": corp_id,
            "event_code": os.environ.get("EVENT_CODE", "e2e-event-code"),
        },
    )
    assert r.status_code == 200, r.text
    return str(r.json()["access_token"])


def _auth_headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def test_abandon_mid_game_partial_score_on_leaderboard(
    client: httpx.AsyncClient,
) -> None:
    token = await _login(client, "emp001")
    h = _auth_headers(token)

    r_play = await client.post("/games/rapid-fire/play", headers=h)
    assert r_play.status_code == 200
    start = r_play.json()
    assert start["status"] == "active"
    question = start["question"]
    assert question is not None

    last: dict[str, object] | None = None
    for _ in range(2):
        assert isinstance(question, dict)
        r_ans = await client.post(
            "/games/rapid-fire/answer",
            headers=h,
            json={
                "question_id": question["id"],
                "selected_option": 1,
                "time_ms": 500,
            },
        )
        assert r_ans.status_code == 200, r_ans.text
        last = r_ans.json()
        question = last.get("next_question")
    assert last is not None
    assert last.get("result") is None
    assert question is not None

    r_abandon = await client.post("/games/rapid-fire/abandon", headers=h)
    assert r_abandon.status_code == 200
    assert r_abandon.json()["result"]["score"] >= 0

    r_lb = await client.get("/leaderboard", headers=h)
    assert r_lb.status_code == 200
    entry = next(e for e in r_lb.json()["entries"] if e["player_id"] == "emp001")
    assert entry["games_completed"] == 0


async def test_resume_mid_game_reflects_prior_answers(client: httpx.AsyncClient) -> None:
    token = await _login(client, "emp002")
    h = _auth_headers(token)

    r_play1 = await client.post("/games/rapid-fire/play", headers=h)
    assert r_play1.status_code == 200
    b1 = r_play1.json()
    assert b1["status"] == "active"
    q1 = b1["question"]
    assert q1 is not None
    qid1 = str(q1["id"])

    r_ans = await client.post(
        "/games/rapid-fire/answer",
        headers=h,
        json={"question_id": qid1, "selected_option": 2, "time_ms": 500},
    )
    assert r_ans.status_code == 200

    r_play2 = await client.post("/games/rapid-fire/play", headers=h)
    assert r_play2.status_code == 200
    b2 = r_play2.json()
    assert b2["status"] == "active"
    assert b2["questions_answered"] == 1
    q_resume = b2["question"]
    assert q_resume is not None
    assert str(q_resume["id"]) not in {qid1}


async def test_second_play_while_session_active_resumes_same_session(
    client: httpx.AsyncClient,
) -> None:
    token = await _login(client, "emp003")
    h = _auth_headers(token)

    r1 = await client.post("/games/rapid-fire/play", headers=h)
    assert r1.status_code == 200
    b1 = r1.json()
    assert b1["status"] == "active"

    r2 = await client.post("/games/rapid-fire/play", headers=h)
    assert r2.status_code == 200
    b2 = r2.json()
    assert b2["game_session_id"] == b1["game_session_id"]
    assert b2["status"] == "active"
    assert b2["questions_answered"] == 0
