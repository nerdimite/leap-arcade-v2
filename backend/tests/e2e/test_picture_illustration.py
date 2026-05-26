"""End-to-end Picture Illustration API journeys (real Postgres + ASGI stack)."""

from __future__ import annotations

import json
from typing import Dict, List, Optional, Union

import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from leap.config.settings import get_settings
from tests.e2e.conftest import E2E_POSTGRES_URL

_FORBIDDEN_KEYS = frozenset({"canonical_answer", "accepted_answers"})

_P1 = "aaaaaaaa-aaaa-aaaa-aaaa-000000000001"
_P2 = "aaaaaaaa-aaaa-aaaa-aaaa-000000000002"
_P3 = "aaaaaaaa-aaaa-aaaa-aaaa-000000000003"
_P4 = "aaaaaaaa-aaaa-aaaa-aaaa-000000000004"
_P5 = "aaaaaaaa-aaaa-aaaa-aaaa-000000000005"

_CORRECT_FIRST_TRY: Dict[str, str] = {
    _P1: "hugging face",
    _P2: "llm",
    _P3: "nlp",
    _P4: "nn",
    _P5: "sgd",
}


def _assert_no_answer_leaks(body: object) -> None:
    """Picture API must never expose canonical_answer or accepted_answers."""

    def walk(node: object) -> None:
        if isinstance(node, dict):
            for key, val in node.items():
                assert key not in _FORBIDDEN_KEYS, f"forbidden key leaked in JSON body: {key!r}"
                walk(val)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(body)


def _picture_payload(raw: Union[httpx.Response, dict]) -> dict:
    """Parse JSON if needed and enforce no canonical / accepted-answers leakage."""
    payload = raw.json() if isinstance(raw, httpx.Response) else raw
    _assert_no_answer_leaks(payload)
    return payload


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


async def _fetch_picture_session_row(player_id: str) -> tuple[str, str, Optional[int]]:
    engine = create_async_engine(E2E_POSTGRES_URL)
    try:
        async with engine.connect() as conn:
            row = (
                await conn.execute(
                    text(
                        "SELECT id, status, score FROM game_sessions "
                        "WHERE player_id = :pid AND game_id = 'picture'",
                    ),
                    {"pid": player_id},
                )
            ).one()
            sid = str(row[0])
            status = str(row[1])
            score_val = row[2]
            score_int = int(score_val) if score_val is not None else None
            return sid, status, score_int
    finally:
        await engine.dispose()


async def _backdate_session_started_at(session_id: str) -> None:
    """Force ``started_at`` older than ``PICTURE_TIME_LIMIT_MS`` (five-minute budget)."""
    engine = create_async_engine(E2E_POSTGRES_URL)
    try:
        async with engine.begin() as conn:
            await conn.execute(
                text(
                    "UPDATE game_sessions SET started_at = started_at - interval '10 minutes' "
                    "WHERE id = :sid",
                ),
                {"sid": session_id},
            )
    finally:
        await engine.dispose()


async def _picture_answer(
    client: httpx.AsyncClient,
    headers: Dict[str, str],
    puzzle_id: str,
    submitted_answer: Optional[str],
) -> httpx.Response:
    return await client.post(
        "/games/picture/answer",
        headers=headers,
        json={"puzzle_id": puzzle_id, "submitted_answer": submitted_answer},
    )


async def _play(client: httpx.AsyncClient, headers: Dict[str, str]) -> dict:
    r = await client.post("/games/picture/play", headers=headers)
    assert r.status_code == 200, r.text
    return _picture_payload(r)


async def _complete_session_first_try(client: httpx.AsyncClient, headers: Dict[str, str]) -> dict:
    body = await _play(client, headers)
    assert body["status"] == "active"
    puzzle = body["puzzle"]
    assert puzzle is not None

    while True:
        pid = str(puzzle["id"])
        ans = await _picture_answer(client, headers, pid, _CORRECT_FIRST_TRY[pid])
        assert ans.status_code == 200, ans.text
        payload = _picture_payload(ans)
        if payload.get("result") is not None:
            return payload
        nxt = payload.get("next_puzzle")
        assert nxt is not None
        puzzle = nxt


async def _run_until_puzzle_then_answer(
    client: httpx.AsyncClient,
    headers: Dict[str, str],
    target_puzzle_id: str,
    submitted_answer: str,
) -> dict:
    """Reach ``target_puzzle_id`` via first-try correct solves, then submit ``submitted_answer``."""
    body = await _play(client, headers)
    puzzle = body["puzzle"]
    assert puzzle is not None

    while True:
        pid = str(puzzle["id"])
        if pid == target_puzzle_id:
            ans = await _picture_answer(client, headers, pid, submitted_answer)
            assert ans.status_code == 200, ans.text
            return _picture_payload(ans)

        submit = _CORRECT_FIRST_TRY[pid]
        ans = await _picture_answer(client, headers, pid, submit)
        assert ans.status_code == 200, ans.text
        payload = _picture_payload(ans)
        assert payload.get("result") is None, "session ended before target puzzle appeared"
        nxt = payload["next_puzzle"]
        assert nxt is not None
        puzzle = nxt


async def test_happy_path_all_correct_first_attempt_time_bonus(client: httpx.AsyncClient) -> None:
    """Play through all puzzles correctly on first attempt; inline result includes time bonus."""
    await _insert_player("e2e_pic_happy", "E2E Picture Happy")
    token = await _login(client, "e2e_pic_happy")
    h = _auth_headers(token)

    final = await _complete_session_first_try(client, h)
    result = final["result"]
    assert result is not None
    assert result["accuracy_score"] == 1000
    assert result["time_bonus"] > 0
    assert result["score"] == result["accuracy_score"] + result["time_bonus"]
    assert all(p["status"] == "correct" for p in result["puzzles"])
    assert sum(int(p["score_earned"]) for p in result["puzzles"]) == 1000

    wrap = await _play(client, h)
    assert wrap["status"] == "completed"
    assert wrap["result"]["score"] == result["score"]

    _, status, score = await _fetch_picture_session_row("e2e_pic_happy")
    assert status == "completed"
    assert score == int(result["score"])


async def test_wrong_then_correct_second_attempt_scores_150(client: httpx.AsyncClient) -> None:
    """Wrong guess yields next_puzzle=null; immediate retry on same puzzle scores 150 on 2nd attempt.

    Note: ``POST /play`` reshuffles among unresolved puzzles (PRD); continuity after a wrong
    ``/answer`` is via submitting again on the same ``puzzle_id``, not necessarily via ``/play``.
    """
    await _insert_player("e2e_pic_wrong", "E2E Picture Wrong/Correct")
    token = await _login(client, "e2e_pic_wrong")
    h = _auth_headers(token)

    opening = await _play(client, h)
    puzzle_id = str(opening["puzzle"]["id"])

    wrong = await _picture_answer(client, h, puzzle_id, "not-a-real-concept-xyz")
    assert wrong.status_code == 200
    wrong_body = _picture_payload(wrong)
    assert wrong_body["correct"] is False
    assert wrong_body["next_puzzle"] is None

    correct_second = await _picture_answer(client, h, puzzle_id, _CORRECT_FIRST_TRY[puzzle_id])
    assert correct_second.status_code == 200
    ok_body = _picture_payload(correct_second)
    assert ok_body["correct"] is True
    assert ok_body["score_earned"] == 150


async def test_accepted_variation_matching_all_seed_variants_for_nlp_puzzle(
    client: httpx.AsyncClient,
) -> None:
    """Each NLP seed variant matches when that puzzle is reached."""
    variants = ["NLP", "Natural Language Processing", "natural language models"]

    for idx, variant in enumerate(variants):
        corp = f"e2e_pic_nlp_{idx}"
        await _insert_player(corp, "E2E NLP Variant")
        token = await _login(client, corp)
        h = _auth_headers(token)

        resp = await _run_until_puzzle_then_answer(client, h, _P3, variant)
        assert resp["correct"] is True


async def test_normalisation_edge_cases_match_hugging_face_puzzle(client: httpx.AsyncClient) -> None:
    """Hyphens, dots, casing, and whitespace collapse match Hugging Face puzzle."""
    variants = [
        "  Hugging-Face  ",
        "hugging.face",
        "HUGGINGFACE",
        " hugging  face ",
        "Hugging Face",
    ]

    for idx, typed in enumerate(variants):
        corp = f"e2e_pic_norm_{idx}"
        await _insert_player(corp, "E2E Picture Normalisation")
        token = await _login(client, corp)
        h = _auth_headers(token)

        resp = await _run_until_puzzle_then_answer(client, h, _P1, typed)
        assert resp["correct"] is True


async def test_skip_path_advances_skipped_never_resurfaced_final_result_skipped_zero_pts(
    client: httpx.AsyncClient,
) -> None:
    """Skip advances; skipped puzzle is not served again; final puzzle skip yields finished result."""
    await _insert_player("e2e_pic_skip", "E2E Picture Skip")
    token = await _login(client, "e2e_pic_skip")
    h = _auth_headers(token)

    body = await _play(client, h)
    skipped_ids: List[str] = []

    puzzle = body["puzzle"]
    assert puzzle is not None

    while True:
        pid = str(puzzle["id"])
        assert pid not in skipped_ids

        ans = await _picture_answer(client, h, pid, None)
        assert ans.status_code == 200
        payload = _picture_payload(ans)
        assert payload["correct"] is False
        skipped_ids.append(pid)

        if payload.get("result") is not None:
            result = payload["result"]
            assert result["accuracy_score"] == 0
            assert all(p["status"] == "skipped" for p in result["puzzles"])
            assert all(int(p["score_earned"]) == 0 for p in result["puzzles"])
            assert result["time_bonus"] >= 0
            assert result["score"] == result["accuracy_score"] + result["time_bonus"]
            break

        nxt = payload["next_puzzle"]
        assert nxt is not None
        assert str(nxt["id"]) not in skipped_ids
        puzzle = nxt


async def test_abandon_mid_game_completed_accuracy_only_remaining_not_reached(
    client: httpx.AsyncClient,
) -> None:
    """Abandon after partial progress completes session with accuracy-only score."""
    await _insert_player("e2e_pic_abandon", "E2E Picture Abandon")
    token = await _login(client, "e2e_pic_abandon")
    h = _auth_headers(token)

    body = await _play(client, h)
    puzzle = body["puzzle"]
    assert puzzle is not None

    # Resolve exactly two puzzles on first attempt.
    for _ in range(2):
        pid = str(puzzle["id"])
        ans = await _picture_answer(client, h, pid, _CORRECT_FIRST_TRY[pid])
        assert ans.status_code == 200
        payload = _picture_payload(ans)
        assert payload.get("result") is None
        puzzle = payload["next_puzzle"]
        assert puzzle is not None

    abandon = await client.post("/games/picture/abandon", headers=h)
    assert abandon.status_code == 200
    abandon_payload = _picture_payload(abandon)
    result = abandon_payload["result"]
    assert result["accuracy_score"] == 400
    assert result["time_bonus"] == 0
    assert result["score"] == 400

    not_reached = [p for p in result["puzzles"] if p["status"] == "not_reached"]
    assert len(not_reached) == 3

    _, status, score = await _fetch_picture_session_row("e2e_pic_abandon")
    assert status == "completed"
    assert score == 400


async def test_abandon_no_picture_session_returns_404(client: httpx.AsyncClient) -> None:
    """Abandon without ever starting Picture returns 404 SESSION_NOT_FOUND."""
    await _insert_player("e2e_pic_no_sess", "E2E Picture No Session")
    token = await _login(client, "e2e_pic_no_sess")
    h = _auth_headers(token)

    r = await client.post("/games/picture/abandon", headers=h)
    assert r.status_code == 404


async def test_abandon_already_completed_returns_409(client: httpx.AsyncClient) -> None:
    """Second abandon after natural completion conflicts."""
    await _insert_player("e2e_pic_abandon_twice", "E2E Picture Double Abandon")
    token = await _login(client, "e2e_pic_abandon_twice")
    h = _auth_headers(token)

    await _complete_session_first_try(client, h)

    second = await client.post("/games/picture/abandon", headers=h)
    assert second.status_code == 409


async def test_replay_protection_second_submit_same_resolved_puzzle_returns_409(
    client: httpx.AsyncClient,
) -> None:
    """Correct resolution then duplicate submit for same puzzle is rejected."""
    await _insert_player("e2e_pic_replay", "E2E Picture Replay")
    token = await _login(client, "e2e_pic_replay")
    h = _auth_headers(token)

    opening = await _play(client, h)
    puzzle_id = str(opening["puzzle"]["id"])

    first = await _picture_answer(client, h, puzzle_id, _CORRECT_FIRST_TRY[puzzle_id])
    assert first.status_code == 200
    _picture_payload(first)

    replay = await _picture_answer(client, h, puzzle_id, _CORRECT_FIRST_TRY[puzzle_id])
    assert replay.status_code == 409


async def test_session_locked_play_returns_result_answer_returns_409_after_completion(
    client: httpx.AsyncClient,
) -> None:
    """Completed sessions surface results on /play and reject further answers."""
    await _insert_player("e2e_pic_locked", "E2E Picture Locked")
    token = await _login(client, "e2e_pic_locked")
    h = _auth_headers(token)

    await _complete_session_first_try(client, h)

    resumed = await _play(client, h)
    assert resumed["status"] == "completed"
    assert resumed["puzzle"] is None
    assert resumed["result"] is not None

    # Any puzzle id from the seeded pool should still be rejected once session completed.
    blocked = await _picture_answer(client, h, _P1, "hugging face")
    assert blocked.status_code == 409


async def test_resume_across_play_calls_same_session_unresolved_puzzle_preserved(
    client: httpx.AsyncClient,
) -> None:
    """Second /play without submits keeps one active session and progress count.

    Each ``/play`` picks randomly among unresolved puzzles, so the surfaced ``puzzle.id``
    may change even though the session is unchanged.
    """
    await _insert_player("e2e_pic_resume", "E2E Picture Resume")
    token = await _login(client, "e2e_pic_resume")
    h = _auth_headers(token)

    first = await _play(client, h)
    second = await _play(client, h)

    assert second["game_session_id"] == first["game_session_id"]
    assert second["status"] == "active"
    assert second["puzzles_answered"] == first["puzzles_answered"]
    assert second["puzzle"] is not None


async def test_server_side_time_limit_enforces_completed_zero_time_bonus_on_submit(
    client: httpx.AsyncClient,
) -> None:
    """Backdated ``started_at`` triggers expiry on next submit with ``time_bonus`` clamped to 0."""
    await _insert_player("e2e_pic_time", "E2E Picture Timer")
    token = await _login(client, "e2e_pic_time")
    h = _auth_headers(token)

    opening = await _play(client, h)
    session_id = str(opening["game_session_id"])
    puzzle_id = str(opening["puzzle"]["id"])

    await _backdate_session_started_at(session_id)

    expired = await _picture_answer(client, h, puzzle_id, "wrong-answer-forcing-submit-path")
    assert expired.status_code == 200
    payload = _picture_payload(expired)
    result = payload["result"]
    assert result is not None
    assert result["time_bonus"] == 0

    _, status, score = await _fetch_picture_session_row("e2e_pic_time")
    assert status == "completed"
    assert score == int(result["score"])
    assert int(result["accuracy_score"]) == score


async def test_canonical_answers_never_leaked_in_picture_api_payloads(client: httpx.AsyncClient) -> None:
    """Responses from play / answer / abandon never include canonical or accepted answer lists."""
    await _insert_player("e2e_pic_leak", "E2E Picture Leak Sweep")
    token = await _login(client, "e2e_pic_leak")
    h = _auth_headers(token)

    bodies: List[object] = []

    play_body = await _play(client, h)
    bodies.append(play_body)

    pid = str(play_body["puzzle"]["id"])
    ans = await _picture_answer(client, h, pid, _CORRECT_FIRST_TRY[pid])
    assert ans.status_code == 200
    bodies.append(ans.json())

    abandon = await client.post("/games/picture/abandon", headers=h)
    assert abandon.status_code == 200
    bodies.append(abandon.json())

    raw = json.dumps(bodies)
    assert "canonical_answer" not in raw
    assert "accepted_answers" not in raw

    for blob in bodies:
        _assert_no_answer_leaks(blob)