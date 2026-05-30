"""End-to-end Pinpoint API journey: full pool playthrough with mixed outcomes."""

from __future__ import annotations

from typing import List, Optional

import httpx

from leap.games.pinpoint.scoring import compute_time_bonus
from tests.e2e.pinpoint_helpers import (
    assert_no_answer_fields_in_payload,
    auth_headers,
    expected_solve_score,
    fail_puzzle,
    fetch_pool_size,
    fetch_puzzle_answer,
    fetch_puzzle_ids_ordered,
    get_my_sessions,
    insert_player,
    install_pinpoint_deterministic_controls,
    load_seed_puzzle_count,
    login,
    pinpoint_session_row,
    solve_puzzle_on_clue,
)

_PLAYER_ID = "e2e_pp_happy"
_ELAPSED_MS = 0
_TIME_BONUS = compute_time_bonus(_ELAPSED_MS)


async def test_full_pool_mixed_outcomes_score_and_leaderboard(
    client: httpx.AsyncClient,
) -> None:
    """Login → play all seeded puzzles (mixed clue depths + one fail) → lobby + leaderboard."""
    await insert_player(_PLAYER_ID, "E2E Pinpoint Happy")
    token = await login(client, _PLAYER_ID)
    headers = auth_headers(token)

    pool_size = await fetch_pool_size()
    assert pool_size == load_seed_puzzle_count() == 10

    _, restore = install_pinpoint_deterministic_controls(elapsed_per_solve_ms=_ELAPSED_MS)
    try:
        before_sessions = await get_my_sessions(client, headers)
        assert pinpoint_session_row(before_sessions) is None

        play_first = await client.post("/games/pinpoint/play", headers=headers)
        assert play_first.status_code == 200, play_first.text
        play_body = play_first.json()
        assert_no_answer_fields_in_payload(play_body)
        assert play_body["session_status"] == "active"
        assert play_body["session_score"] == 0
        puzzle = play_body["puzzle"]
        assert puzzle is not None
        assert puzzle["total_puzzles"] == pool_size

        ordered_ids = await fetch_puzzle_ids_ordered()
        assert len(ordered_ids) == pool_size

        # Mixed outcomes across the full seeded pool (8 solves, 2 fails).
        outcome_plan: List[tuple[str, int | None]] = [
            ("solve", 1),
            ("solve", 3),
            ("fail", None),
            ("solve", 1),
            ("solve", 5),
            ("solve", 2),
            ("fail", None),
            ("solve", 4),
            ("solve", 1),
            ("solve", 5),
        ]
        assert len(outcome_plan) == pool_size

        running_score = 0
        result_rows: List[dict] = []
        last: Optional[dict] = None

        for puzzle_index, (kind, on_clue) in enumerate(outcome_plan):
            assert puzzle is not None
            puzzle_id = str(puzzle["puzzle_id"])
            assert puzzle_id == ordered_ids[puzzle_index]

            if kind == "solve":
                assert on_clue is not None
                answer = await fetch_puzzle_answer(puzzle_id)
                last = await solve_puzzle_on_clue(
                    client,
                    headers,
                    puzzle_id,
                    on_clue=on_clue,
                    answer=answer,
                )
                expected_piece = expected_solve_score(on_clue, _ELAPSED_MS)
                assert last["puzzle"]["score"] == expected_piece
                assert last["puzzle"]["time_bonus"] == _TIME_BONUS
                running_score += expected_piece
            else:
                last = await fail_puzzle(client, headers, puzzle_id)

            assert last["session_score"] == running_score
            result_rows.append(
                {
                    "puzzle_id": puzzle_id,
                    "status": last["puzzle"]["status"],
                    "clues_used": on_clue if kind == "solve" else 5,
                    "score": last["puzzle"]["score"] or 0,
                    "time_bonus": last["puzzle"]["time_bonus"] or 0,
                },
            )

            if last.get("result") is not None:
                assert last["session_status"] == "completed"
                break

            assert last["session_status"] == "active"
            play_next = await client.post("/games/pinpoint/play", headers=headers)
            assert play_next.status_code == 200, play_next.text
            next_body = play_next.json()
            assert_no_answer_fields_in_payload(next_body)
            assert next_body["session_status"] == "active"
            puzzle = next_body["puzzle"]
            assert puzzle is not None
            assert puzzle["status"] == "active"

        assert last is not None
        result = last["result"]
        assert isinstance(result, dict)
        assert result["score"] == running_score
        assert result["puzzles_solved"] == 8
        assert result["puzzles_failed"] == 2
        assert result["puzzles_not_reached"] == 0
        assert len(result["puzzles"]) == pool_size

        # Result ordering is not a contract (all attempts share the deterministic
        # fixed clock, so started_at ties); compare per-puzzle outcomes by id.
        actual_by_id = {row["puzzle_id"]: row for row in result["puzzles"]}
        assert set(actual_by_id) == {row["puzzle_id"] for row in result_rows}
        for expected in result_rows:
            actual = actual_by_id[expected["puzzle_id"]]
            assert actual["status"] == expected["status"]
            assert actual["clues_used"] == expected["clues_used"]
            assert actual["score"] == expected["score"]
            assert actual["time_bonus"] == expected["time_bonus"]

        expected_total = sum(row["score"] for row in result_rows)
        assert last["session_score"] == expected_total

        final_play = await client.post("/games/pinpoint/play", headers=headers)
        assert final_play.status_code == 200, final_play.text
        final = final_play.json()
        assert_no_answer_fields_in_payload(final)
        assert final["session_status"] == "completed"
        assert final["session_score"] == expected_total
        assert final["puzzle"] is None
        assert final["result"] is not None
        assert final["result"]["score"] == expected_total

        after_sessions = await get_my_sessions(client, headers)
        pp_row = pinpoint_session_row(after_sessions)
        assert pp_row is not None
        assert pp_row["status"] == "completed"
        assert pp_row["score"] == expected_total

        board = await client.get("/leaderboard", headers=headers)
        assert board.status_code == 200, board.text
        assert_no_answer_fields_in_payload(board.json())
        entry = next(e for e in board.json()["entries"] if e["player_id"] == _PLAYER_ID)
        assert entry["total_score"] == expected_total
        assert entry["games_completed"] == 1
    finally:
        restore()
