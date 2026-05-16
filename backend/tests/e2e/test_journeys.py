"""End-to-end API journeys: full Rapid Fire completion and auth edge cases."""

from __future__ import annotations

from typing import Dict, Optional, Set

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from leap.config.settings import get_settings
from tests.e2e.conftest import E2E_POSTGRES_URL


def _wrong_event_code_same_length(valid: str) -> str:
    """Return a code equal in length to ``valid`` but not equal (compare_digest-safe)."""
    if not valid:
        return "!"
    replacement = "z" if valid[0] != "z" else "y"
    return replacement + valid[1:]


async def _player_count() -> int:
    engine = create_async_engine(E2E_POSTGRES_URL)
    try:
        async with engine.connect() as conn:
            return int(
                (await conn.execute(text("SELECT COUNT(*) FROM players"))).scalar_one()
            )
    finally:
        await engine.dispose()


async def _insert_player(player_id: str, display_name: str) -> None:
    engine = create_async_engine(E2E_POSTGRES_URL)
    try:
        async with engine.begin() as conn:
            await conn.execute(
                text(
                    "INSERT INTO players (id, display_name) VALUES (:id, :display_name)"
                ),
                {"id": player_id, "display_name": display_name},
            )
    finally:
        await engine.dispose()


async def _fetch_correct_option_index(question_id: str) -> int:
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


async def test_full_rapid_fire_happy_path_completed_and_leaderboard(client) -> None:
    """Login → play → answer until complete → /play shows completed → leaderboard shows score."""
    player_id = "e2e_rf_happy"
    await _insert_player(player_id, "E2E Rapid Fire")

    settings = get_settings()
    login = await client.post(
        "/auth/login",
        json={"corp_id": player_id, "event_code": settings.EVENT_CODE},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    play_first = await client.post("/games/rapid-fire/play", headers=headers)
    assert play_first.status_code == 200
    play_body = play_first.json()
    assert play_body["status"] == "active"
    question = play_body["question"]
    assert question is not None
    questions_total = play_body["questions_total"]
    assert questions_total is not None and questions_total >= 1

    seen_ids: Set[str] = set()
    iterations = 0
    last: Optional[Dict[str, object]] = None

    while question is not None:
        iterations += 1
        assert iterations <= questions_total, (
            "More answer steps than /play questions_total — pool may be out of sync with DB"
        )
        qid = str(question["id"])
        assert qid not in seen_ids
        seen_ids.add(qid)
        correct = await _fetch_correct_option_index(qid)
        ans = await client.post(
            "/games/rapid-fire/answer",
            headers=headers,
            json={
                "question_id": qid,
                "selected_option": correct,
                "time_ms": 1000,
            },
        )
        assert ans.status_code == 200, ans.text
        last = ans.json()
        if last.get("result") is not None:
            assert last.get("next_question") is None
            break
        question = last.get("next_question")

    assert last is not None
    result_block = last.get("result")
    assert isinstance(result_block, dict)
    assert int(result_block["score"]) > 0
    assert len(seen_ids) == questions_total

    final_play = await client.post("/games/rapid-fire/play", headers=headers)
    assert final_play.status_code == 200
    final = final_play.json()
    assert final["status"] == "completed"
    assert final.get("result") is not None
    assert final["result"]["score"] > 0

    board = await client.get("/leaderboard", headers=headers)
    assert board.status_code == 200
    payload = board.json()
    row = next(e for e in payload["entries"] if e["player_id"] == player_id)
    assert row["total_score"] > 0


async def test_login_wrong_event_code_401_no_extra_player_row(client) -> None:
    """Invalid event code returns 401; auth does not insert an additional player row.

    With the current auth order (player lookup before event check), a player row must
    exist to reach ``InvalidEventCodeException`` and HTTP 401.
    """
    player_id = "e2e_wrong_event"
    base_count = await _player_count()

    await _insert_player(player_id, "Wrong Event Probe")
    assert await _player_count() == base_count + 1

    settings = get_settings()
    bad = _wrong_event_code_same_length(settings.EVENT_CODE)
    assert bad != settings.EVENT_CODE

    r = await client.post(
        "/auth/login",
        json={"corp_id": player_id, "event_code": bad},
    )
    assert r.status_code == 401

    assert await _player_count() == base_count + 1
