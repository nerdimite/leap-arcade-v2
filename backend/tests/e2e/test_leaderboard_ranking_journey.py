"""E2e journey: two players finish rapid_fire with different scores; leaderboard orders by score."""

from __future__ import annotations

from typing import Dict, Optional, Set

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from leap.config.settings import get_settings
from tests.e2e.conftest import E2E_POSTGRES_URL, truncate_transaction_tables

_PLAYER_A_ID = "emp_rank_a"
_PLAYER_B_ID = "emp_rank_b"


async def _login(client, corp_id: str) -> str:
    settings = get_settings()
    r = await client.post(
        "/auth/login",
        json={"corp_id": corp_id, "event_code": settings.EVENT_CODE},
    )
    assert r.status_code == 200, r.text
    return str(r.json()["access_token"])


async def _correct_option_index(question_id: str) -> int:
    """IDs come from the API; lookup scored rows in the seeded pool (no hard-coded question IDs)."""
    engine = create_async_engine(E2E_POSTGRES_URL)
    try:
        async with engine.connect() as conn:
            row = (
                await conn.execute(
                    text(
                        "SELECT correct_option_index FROM rapid_fire_questions "
                        "WHERE id = :id"
                    ),
                    {"id": question_id},
                )
            ).one()
            return int(row[0])
    finally:
        await engine.dispose()


async def _complete_rapid_fire(client, token: str) -> None:
    """Same control flow as the full-game e2e journey: cap steps with /play questions_total."""
    headers = {"Authorization": f"Bearer {token}"}
    r = await client.post("/games/rapid-fire/play", headers=headers)
    assert r.status_code == 200, r.text
    payload = r.json()
    assert payload["status"] == "active"
    question = payload["question"]
    assert question is not None
    questions_total = payload["questions_total"]
    assert questions_total is not None and questions_total >= 1

    seen_ids: Set[str] = set()
    iterations = 0
    last: Optional[Dict[str, object]] = None

    while question is not None:
        iterations += 1
        assert iterations <= questions_total
        qid = str(question["id"])
        assert qid not in seen_ids
        seen_ids.add(qid)
        correct = await _correct_option_index(qid)
        ans = await client.post(
            "/games/rapid-fire/answer",
            headers=headers,
            json={
                "question_id": qid,
                "selected_option": correct,
                "time_ms": 5_000,
            },
        )
        assert ans.status_code == 200, ans.text
        last = ans.json()
        if last.get("result") is not None:
            assert last.get("next_question") is None
            result_block = last.get("result")
            assert isinstance(result_block, dict)
            assert int(result_block["score"]) > 0
            break
        question = last.get("next_question")

    assert last is not None
    assert last.get("result") is not None
    assert len(seen_ids) == questions_total

    final_play = await client.post("/games/rapid-fire/play", headers=headers)
    assert final_play.status_code == 200, final_play.text
    final = final_play.json()
    assert final["status"] == "completed"
    assert final.get("result") is not None


async def test_multi_player_leaderboard_ranking_journey(client) -> None:
    engine = create_async_engine(E2E_POSTGRES_URL)
    try:
        await truncate_transaction_tables(engine)
        async with engine.begin() as conn:
            await conn.execute(
                text(
                    "INSERT INTO players (id, display_name) VALUES "
                    "(:a, 'Rank Journey A'), (:b, 'Rank Journey B')"
                ),
                {"a": _PLAYER_A_ID, "b": _PLAYER_B_ID},
            )
    finally:
        await engine.dispose()

    token_b = await _login(client, _PLAYER_B_ID)
    hdr_b = {"Authorization": f"Bearer {token_b}"}
    r_play_b = await client.post("/games/rapid-fire/play", headers=hdr_b)
    assert r_play_b.status_code == 200, r_play_b.text
    r_abandon = await client.post("/games/rapid-fire/abandon", headers=hdr_b)
    assert r_abandon.status_code == 200, r_abandon.text
    assert r_abandon.json()["result"]["score"] == 0

    token_a = await _login(client, _PLAYER_A_ID)
    await _complete_rapid_fire(client, token_a)

    r_board = await client.get(
        "/leaderboard",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert r_board.status_code == 200, r_board.text
    data = r_board.json()
    entries = data["entries"]
    assert len(entries) == 2
    assert data["total_players"] == 2

    first, second = entries[0], entries[1]
    assert first["player_id"] == _PLAYER_A_ID
    assert second["player_id"] == _PLAYER_B_ID
    assert first["total_score"] > second["total_score"]
    assert first["total_score"] > 0
    assert second["total_score"] == 0
