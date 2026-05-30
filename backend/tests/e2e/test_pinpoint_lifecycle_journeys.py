"""Pinpoint lifecycle e2e journeys: abandon, refresh idempotency, replay protection."""

from __future__ import annotations

from typing import Optional, Set

import httpx

from tests.e2e.pinpoint_helpers import (
    assert_no_answer_fields_in_payload,
    auth_headers,
    fetch_pool_size,
    fetch_puzzle_answer,
    get_my_sessions,
    insert_player,
    install_pinpoint_deterministic_controls,
    login,
    pinpoint_session_row,
    solve_puzzle_on_clue,
    submit_guess,
)

_WRONG_GUESS = "definitely-not-the-answer"


async def test_abandon_mid_puzzle_closes_attempt_and_lobby_shows_abandoned(
    client: httpx.AsyncClient,
) -> None:
    """One wrong guess → abandon; active attempt failed; remaining puzzles not_reached."""
    player_id = "e2e_pp_abandon"
    await insert_player(player_id, "E2E Pinpoint Abandon")
    token = await login(client, player_id)
    headers = auth_headers(token)
    pool_size = await fetch_pool_size()

    _, restore = install_pinpoint_deterministic_controls()
    try:
        play = await client.post("/games/pinpoint/play", headers=headers)
        assert play.status_code == 200, play.text
        play_body = play.json()
        assert_no_answer_fields_in_payload(play_body)
        puzzle = play_body["puzzle"]
        assert puzzle is not None
        puzzle_id = str(puzzle["puzzle_id"])

        wrong = await submit_guess(client, headers, puzzle_id, _WRONG_GUESS)
        assert wrong["correct"] is False
        assert wrong["puzzle"]["clues_revealed"] == 2
        assert wrong["session_status"] == "active"

        abandon = await client.post("/games/pinpoint/abandon", headers=headers)
        assert abandon.status_code == 200, abandon.text
        abandon_body = abandon.json()
        assert_no_answer_fields_in_payload(abandon_body)
        result = abandon_body["result"]
        assert result["score"] == 0
        assert result["puzzles_solved"] == 0
        assert result["puzzles_failed"] == 1
        assert result["puzzles_not_reached"] == pool_size - 1

        failed_rows = [p for p in result["puzzles"] if p["status"] == "failed"]
        assert len(failed_rows) == 1
        assert failed_rows[0]["puzzle_id"] == puzzle_id
        assert failed_rows[0]["score"] == 0
        assert failed_rows[0]["time_bonus"] == 0

        not_reached = [p for p in result["puzzles"] if p["status"] == "not_reached"]
        assert len(not_reached) == pool_size - 1
        assert all(p["score"] == 0 and p["time_bonus"] == 0 for p in not_reached)

        sessions = await get_my_sessions(client, headers)
        pp_row = pinpoint_session_row(sessions)
        assert pp_row is not None
        assert pp_row["status"] == "abandoned"
        assert pp_row["score"] == 0

        resumed = await client.post("/games/pinpoint/play", headers=headers)
        assert resumed.status_code == 200, resumed.text
        resumed_body = resumed.json()
        assert_no_answer_fields_in_payload(resumed_body)
        assert resumed_body["session_status"] == "abandoned"
        assert resumed_body["puzzle"] is None
        assert resumed_body["result"] is not None
        assert resumed_body["result"]["score"] == 0
    finally:
        restore()


async def test_refresh_mid_puzzle_play_is_idempotent(client: httpx.AsyncClient) -> None:
    """Two wrong guesses then /play again returns the same puzzle and clue state."""
    player_id = "e2e_pp_refresh"
    await insert_player(player_id, "E2E Pinpoint Refresh")
    token = await login(client, player_id)
    headers = auth_headers(token)

    _, restore = install_pinpoint_deterministic_controls()
    try:
        play1 = await client.post("/games/pinpoint/play", headers=headers)
        assert play1.status_code == 200, play1.text
        b1 = play1.json()
        assert_no_answer_fields_in_payload(b1)
        assert b1["session_status"] == "active"
        p1 = b1["puzzle"]
        assert p1 is not None
        puzzle_id = str(p1["puzzle_id"])

        last_guess: dict | None = None
        for _ in range(2):
            last_guess = await submit_guess(client, headers, puzzle_id, _WRONG_GUESS)
            assert last_guess["correct"] is False
        assert last_guess is not None

        play2 = await client.post("/games/pinpoint/play", headers=headers)
        assert play2.status_code == 200, play2.text
        b2 = play2.json()
        assert_no_answer_fields_in_payload(b2)
        assert b2["session_status"] == "active"
        p2 = b2["puzzle"]
        assert p2 is not None
        assert p2["puzzle_id"] == puzzle_id
        assert p2["clues_revealed"] == last_guess["puzzle"]["clues_revealed"] == 3
        assert p2["clues"] == last_guess["puzzle"]["clues"]
        assert p2["started_at"] == p1["started_at"]
    finally:
        restore()


async def test_replay_protection_after_completion(client: httpx.AsyncClient) -> None:
    """Completed session: /guess returns 409; /play surfaces the result block."""
    player_id = "e2e_pp_replay"
    await insert_player(player_id, "E2E Pinpoint Replay")
    token = await login(client, player_id)
    headers = auth_headers(token)
    pool_size = await fetch_pool_size()

    _, restore = install_pinpoint_deterministic_controls()
    try:
        play = await client.post("/games/pinpoint/play", headers=headers)
        assert play.status_code == 200, play.text
        puzzle = play.json()["puzzle"]
        assert puzzle is not None

        seen: Set[str] = set()
        last_puzzle_id: Optional[str] = None
        final_score = 0

        while puzzle is not None:
            puzzle_id = str(puzzle["puzzle_id"])
            seen.add(puzzle_id)
            last_puzzle_id = puzzle_id
            answer = await fetch_puzzle_answer(puzzle_id)
            body = await solve_puzzle_on_clue(
                client,
                headers,
                puzzle_id,
                on_clue=1,
                answer=answer,
            )
            final_score = int(body["session_score"])
            if body.get("result") is not None:
                assert body["session_status"] == "completed"
                break
            next_play = await client.post("/games/pinpoint/play", headers=headers)
            assert next_play.status_code == 200, next_play.text
            puzzle = next_play.json()["puzzle"]

        assert len(seen) == pool_size

        replay_play = await client.post("/games/pinpoint/play", headers=headers)
        assert replay_play.status_code == 200, replay_play.text
        replay_body = replay_play.json()
        assert_no_answer_fields_in_payload(replay_body)
        assert replay_body["session_status"] == "completed"
        assert replay_body["puzzle"] is None
        assert replay_body["result"] is not None
        assert replay_body["result"]["score"] == final_score

        assert last_puzzle_id is not None
        blocked = await client.post(
            "/games/pinpoint/guess",
            headers=headers,
            json={"puzzle_id": last_puzzle_id, "guess": "anything"},
        )
        assert blocked.status_code == 409
    finally:
        restore()
