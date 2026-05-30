"""End-to-end Crossword API journey: full puzzle playthrough."""

from __future__ import annotations

import httpx

from tests.e2e.crossword_helpers import (
    assert_clues_hide_unsolved_entries,
    assert_no_unsolved_answer_text_in_payload,
    assert_skeleton_has_no_letters,
    auth_headers,
    check_entry,
    crossword_session_row,
    expected_terminal_score,
    expected_time_bonus,
    fetch_entry_count,
    fetch_persisted_session_score,
    fetch_seeded_entries,
    get_my_sessions,
    insert_player,
    install_crossword_deterministic_controls,
    install_e2e_crossword_puzzle,
    login,
    parse_started_at,
    play_crossword,
    restore_crossword_production_seed,
    unsolved_answers,
)

_PLAYER_ID = "e2e_xw_happy"
_ELAPSED_MS = 0
_TIME_BONUS = expected_time_bonus(_ELAPSED_MS)


async def test_full_playthrough_completed_score_lobby_leaderboard(
    client: httpx.AsyncClient,
) -> None:
    """Login → play → solve every entry → lobby + leaderboard reflect final score."""
    await install_e2e_crossword_puzzle()
    bind_session_start, advance_to_terminal, _, restore_clock = (
        install_crossword_deterministic_controls(
            terminal_elapsed_ms=_ELAPSED_MS,
        )
    )
    try:
        await insert_player(_PLAYER_ID, "E2E Crossword Happy")
        token = await login(client, _PLAYER_ID)
        headers = auth_headers(token)

        entries = await fetch_seeded_entries()
        entry_count = len(entries)
        assert entry_count == await fetch_entry_count() == 2

        before_sessions = await get_my_sessions(client, headers)
        assert crossword_session_row(before_sessions) is None

        play_body = await play_crossword(client, headers)
        bind_session_start(parse_started_at(play_body))
        assert play_body["session_status"] == "active"
        assert play_body["session_score"] == 0
        assert play_body["result"] is None
        puzzle = play_body["puzzle"]
        assert puzzle is not None
        assert puzzle["solved_count"] == 0
        assert puzzle["total_entries"] == entry_count
        assert_skeleton_has_no_letters(puzzle)
        assert_clues_hide_unsolved_entries(puzzle["clues"])
        assert_no_unsolved_answer_text_in_payload(
            play_body,
            unsolved_answers(entries, set()),
        )

        running_score = 0
        last: dict | None = None

        for index, entry in enumerate(entries):
            if index == entry_count - 1:
                advance_to_terminal()
            last = await check_entry(
                client,
                headers,
                entry["entry_id"],
                entry["answer"],
            )
            assert last["correct"] is True
            assert last["entry"] is not None
            assert last["entry"]["answer"] == entry["answer"]
            assert last["entry"]["entry_id"] == entry["entry_id"]

            if index < entry_count - 1:
                running_score += 100
                assert last["session_status"] == "active"
                assert last["session_score"] == running_score
                assert last["result"] is None
            else:
                expected_total = entry_count * 100 + _TIME_BONUS
                assert last["session_status"] == "completed"
                assert last["session_score"] == expected_total
                result = last["result"]
                assert isinstance(result, dict)
                assert result["base_score"] == entry_count * 100
                assert result["time_bonus"] == _TIME_BONUS
                assert result["time_elapsed_ms"] == _ELAPSED_MS
                assert result["solved_count"] == entry_count
                assert result["total_entries"] == entry_count
                assert len(result["solved_entries"]) == entry_count
                remaining = unsolved_answers(entries, {e["entry_id"] for e in entries})
                assert_no_unsolved_answer_text_in_payload(last, remaining)

        assert last is not None
        expected_total = expected_terminal_score(entry_count, _ELAPSED_MS)
        assert await fetch_persisted_session_score(_PLAYER_ID) == expected_total

        final_play = await play_crossword(client, headers)
        assert final_play["session_status"] == "completed"
        assert final_play["session_score"] == expected_total
        assert final_play["puzzle"] is None
        assert final_play["result"] is not None
        assert final_play["result"]["solved_count"] == entry_count
        assert final_play["result"]["base_score"] == entry_count * 100

        after_sessions = await get_my_sessions(client, headers)
        xw_row = crossword_session_row(after_sessions)
        assert xw_row is not None
        assert xw_row["status"] == "completed"
        assert xw_row["score"] == expected_total

        board = await client.get("/leaderboard", headers=headers)
        assert board.status_code == 200, board.text
        entry = next(e for e in board.json()["entries"] if e["player_id"] == _PLAYER_ID)
        assert entry["total_score"] == expected_total
        assert entry["games_completed"] == 1
    finally:
        restore_clock()
        await restore_crossword_production_seed()
