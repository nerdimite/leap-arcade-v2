"""End-to-end Word Hunt API journey: full puzzle playthrough."""

from __future__ import annotations

import httpx

from leap.games.word_hunt.scoring import compute_time_bonus
from tests.e2e.word_hunt_helpers import (
    assert_clues_hide_unfound_words,
    assert_no_unfound_word_text_in_payload,
    auth_headers,
    fetch_persisted_session_score,
    fetch_seeded_words,
    find_word_by_coords,
    get_my_sessions,
    insert_player,
    install_word_hunt_deterministic_controls,
    load_seed_word_count,
    login,
    parse_started_at,
    play_word_hunt,
    word_hunt_session_row,
)

_PLAYER_ID = "e2e_wh_happy"
_ELAPSED_MS = 0
_TIME_BONUS = compute_time_bonus(_ELAPSED_MS)


async def test_full_playthrough_completed_score_lobby_leaderboard(
    client: httpx.AsyncClient,
) -> None:
    """Login → play → find every word → lobby + leaderboard reflect final score."""
    await insert_player(_PLAYER_ID, "E2E Word Hunt Happy")
    token = await login(client, _PLAYER_ID)
    headers = auth_headers(token)

    seeded_words = await fetch_seeded_words()
    word_count = len(seeded_words)
    assert word_count == load_seed_word_count() == 5

    bind_session_start, advance_to_terminal, _, restore = install_word_hunt_deterministic_controls(
        terminal_elapsed_ms=_ELAPSED_MS,
    )
    try:
        before_sessions = await get_my_sessions(client, headers)
        assert word_hunt_session_row(before_sessions) is None

        play_body = await play_word_hunt(client, headers)
        bind_session_start(parse_started_at(play_body))
        assert play_body["session_status"] == "active"
        assert play_body["session_score"] == 0
        assert play_body["result"] is None
        puzzle = play_body["puzzle"]
        assert puzzle is not None
        assert puzzle["found_count"] == 0
        assert puzzle["total_words"] == word_count
        assert_clues_hide_unfound_words(puzzle["clues"])
        unfound_texts = [entry["word"] for entry in seeded_words]
        assert_no_unfound_word_text_in_payload(play_body, unfound_texts)

        running_score = 0
        last: dict | None = None

        for index, word_entry in enumerate(seeded_words):
            if index == word_count - 1:
                advance_to_terminal()
            last = await find_word_by_coords(client, headers, word_entry)
            assert last["matched"] is True
            assert last["word"] is not None
            assert last["word"]["word"] == word_entry["word"]
            assert last["word"]["coordinates"]["start_row"] == word_entry["start_row"]
            assert last["word"]["coordinates"]["start_col"] == word_entry["start_col"]
            assert last["word"]["coordinates"]["end_row"] == word_entry["end_row"]
            assert last["word"]["coordinates"]["end_col"] == word_entry["end_col"]

            if index < word_count - 1:
                running_score += 100
                assert last["session_status"] == "active"
                assert last["session_score"] == running_score
                assert last["result"] is None
            else:
                expected_total = word_count * 100 + _TIME_BONUS
                assert last["session_status"] == "completed"
                assert last["session_score"] == expected_total
                result = last["result"]
                assert isinstance(result, dict)
                assert result["base_score"] == word_count * 100
                assert result["time_bonus"] == _TIME_BONUS
                assert result["time_elapsed_ms"] == _ELAPSED_MS
                assert result["found_count"] == word_count
                assert result["total_words"] == word_count
                assert len(result["found_words"]) == word_count
                remaining = [entry["word"] for entry in seeded_words[index + 1 :]]
                assert_no_unfound_word_text_in_payload(last, remaining)

        assert last is not None
        expected_total = word_count * 100 + _TIME_BONUS
        assert await fetch_persisted_session_score(_PLAYER_ID) == expected_total

        final_play = await play_word_hunt(client, headers)
        assert final_play["session_status"] == "completed"
        assert final_play["session_score"] == expected_total
        assert final_play["puzzle"] is None
        assert final_play["result"] is not None
        assert final_play["result"]["found_count"] == word_count
        assert final_play["result"]["base_score"] == word_count * 100

        after_sessions = await get_my_sessions(client, headers)
        wh_row = word_hunt_session_row(after_sessions)
        assert wh_row is not None
        assert wh_row["status"] == "completed"
        assert wh_row["score"] == expected_total

        board = await client.get("/leaderboard", headers=headers)
        assert board.status_code == 200, board.text
        entry = next(e for e in board.json()["entries"] if e["player_id"] == _PLAYER_ID)
        assert entry["total_score"] == expected_total
        assert entry["games_completed"] == 1
    finally:
        restore()
