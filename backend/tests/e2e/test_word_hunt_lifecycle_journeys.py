"""Word Hunt lifecycle e2e journeys: partial submit, resume, cheating, collision."""

from __future__ import annotations

import httpx

from tests.e2e.word_hunt_helpers import (
    assert_clues_hide_unfound_words,
    assert_no_unfound_word_text_in_payload,
    auth_headers,
    count_finds_for_player,
    expected_terminal_score,
    expected_time_bonus,
    fetch_persisted_session_score,
    fetch_puzzle_dims,
    fetch_seeded_words,
    find_word_by_coords,
    get_my_sessions,
    insert_player,
    install_collision_puzzle,
    install_word_hunt_deterministic_controls,
    login,
    parse_started_at,
    play_word_hunt,
    restore_word_hunt_production_seed,
    submit_find,
    submit_session,
    word_hunt_session_row,
)

_TERMINAL_ELAPSED_MS = 300_000
_TIME_BONUS = expected_time_bonus(_TERMINAL_ELAPSED_MS)


async def _partial_find_two_words(
    client: httpx.AsyncClient,
    headers: dict[str, str],
    seeded_words: list[dict],
    bind_session_start,
) -> tuple[dict, list[str]]:
    play_body = await play_word_hunt(client, headers)
    bind_session_start(parse_started_at(play_body))
    puzzle = play_body["puzzle"]
    assert puzzle is not None
    for word_entry in seeded_words[:2]:
        await find_word_by_coords(client, headers, word_entry)
    unfound = [entry["word"] for entry in seeded_words[2:]]
    return play_body, unfound


async def _assert_completed_lobby_and_leaderboard(
    client: httpx.AsyncClient,
    headers: dict[str, str],
    player_id: str,
    expected_score: int,
) -> None:
    sessions = await get_my_sessions(client, headers)
    row = word_hunt_session_row(sessions)
    assert row is not None
    assert row["status"] == "completed"
    assert row["score"] == expected_score

    board = await client.get("/leaderboard", headers=headers)
    assert board.status_code == 200, board.text
    entry = next(e for e in board.json()["entries"] if e["player_id"] == player_id)
    assert entry["total_score"] == expected_score


async def test_partial_find_then_submit(
    client: httpx.AsyncClient,
) -> None:
    """Find some words, submit early, and never leak unfound answer text."""
    player_id = "e2e_wh_partial"
    await insert_player(player_id, "E2E Word Hunt Partial")
    token = await login(client, player_id)
    headers = auth_headers(token)
    seeded_words = await fetch_seeded_words()

    bind_session_start, advance_to_terminal, _, restore = install_word_hunt_deterministic_controls(
        terminal_elapsed_ms=_TERMINAL_ELAPSED_MS,
    )
    try:
        _, unfound = await _partial_find_two_words(
            client,
            headers,
            seeded_words,
            bind_session_start,
        )
        advance_to_terminal()
        submit_body = await submit_session(client, headers)
        result = submit_body["result"]
        expected_score = expected_terminal_score(2, _TERMINAL_ELAPSED_MS)
        assert result["score"] == expected_score
        assert result["base_score"] == 200
        assert result["time_bonus"] == _TIME_BONUS
        assert result["found_count"] == 2
        assert len(result["found_words"]) == 2
        assert_no_unfound_word_text_in_payload(submit_body, unfound)
        assert await fetch_persisted_session_score(player_id) == expected_score
        await _assert_completed_lobby_and_leaderboard(
            client,
            headers,
            player_id,
            expected_score,
        )
    finally:
        restore()


async def test_mid_game_refresh_resume(
    client: httpx.AsyncClient,
) -> None:
    """Re-calling /play returns the same grid with found clues revealed."""
    player_id = "e2e_wh_refresh"
    await insert_player(player_id, "E2E Word Hunt Refresh")
    token = await login(client, player_id)
    headers = auth_headers(token)
    seeded_words = await fetch_seeded_words()

    _, _, _, restore = install_word_hunt_deterministic_controls()
    try:
        first_play = await play_word_hunt(client, headers)
        puzzle = first_play["puzzle"]
        assert puzzle is not None
        started_at = puzzle["started_at"]
        grid = puzzle["grid"]

        await find_word_by_coords(client, headers, seeded_words[0])
        await find_word_by_coords(client, headers, seeded_words[1])

        resumed = await play_word_hunt(client, headers)
        assert resumed["session_status"] == "active"
        assert resumed["session_score"] == 200
        resumed_puzzle = resumed["puzzle"]
        assert resumed_puzzle is not None
        assert resumed_puzzle["grid"] == grid
        assert resumed_puzzle["started_at"] == started_at
        assert resumed_puzzle["found_count"] == 2

        found_ids = {seeded_words[0]["word_id"], seeded_words[1]["word_id"]}
        for clue in resumed_puzzle["clues"]:
            if clue["word_id"] in found_ids:
                assert clue["found"] is True
                assert clue["word"] is not None
                assert clue["coordinates"] is not None
            else:
                assert clue["found"] is False
                assert clue.get("word") is None

        unfound = [entry["word"] for entry in seeded_words[2:]]
        assert_no_unfound_word_text_in_payload(resumed, unfound)
        assert_clues_hide_unfound_words(resumed_puzzle["clues"])
    finally:
        restore()


async def test_navigation_guard_submit_equivalence(
    client: httpx.AsyncClient,
) -> None:
    """POST /submit from partial progress matches an identical explicit submit."""
    seeded_words = await fetch_seeded_words()
    bind_session_start, advance_to_terminal, reset_terminal, restore = (
        install_word_hunt_deterministic_controls(
            terminal_elapsed_ms=_TERMINAL_ELAPSED_MS,
        )
    )
    try:
        player_a = "e2e_wh_nav_a"
        player_b = "e2e_wh_nav_b"
        await insert_player(player_a, "E2E Word Hunt Nav A")
        await insert_player(player_b, "E2E Word Hunt Nav B")
        headers_a = auth_headers(await login(client, player_a))
        headers_b = auth_headers(await login(client, player_b))

        play_a, _ = await _partial_find_two_words(
            client,
            headers_a,
            seeded_words,
            bind_session_start,
        )
        play_b, _ = await _partial_find_two_words(
            client,
            headers_b,
            seeded_words,
            bind_session_start,
        )

        bind_session_start(parse_started_at(play_a))
        advance_to_terminal()
        result_a = (await submit_session(client, headers_a))["result"]

        reset_terminal()
        bind_session_start(parse_started_at(play_b))
        advance_to_terminal()
        result_b = (await submit_session(client, headers_b))["result"]

        assert result_a == result_b
        expected_score = expected_terminal_score(2, _TERMINAL_ELAPSED_MS)
        assert result_a["score"] == expected_score
        assert result_a["time_bonus"] == _TIME_BONUS
    finally:
        restore()


async def test_abandon_endpoint_returns_404(client: httpx.AsyncClient) -> None:
    player_id = "e2e_wh_no_abandon"
    await insert_player(player_id, "E2E Word Hunt No Abandon")
    headers = auth_headers(await login(client, player_id))

    await play_word_hunt(client, headers)
    abandon = await client.post("/games/word-hunt/abandon", headers=headers)
    assert abandon.status_code == 404


async def test_reentry_after_completion(
    client: httpx.AsyncClient,
) -> None:
    player_id = "e2e_wh_reentry"
    await insert_player(player_id, "E2E Word Hunt Reentry")
    headers = auth_headers(await login(client, player_id))
    seeded_words = await fetch_seeded_words()

    bind_session_start, advance_to_terminal, _, restore = install_word_hunt_deterministic_controls(
        terminal_elapsed_ms=_TERMINAL_ELAPSED_MS,
    )
    try:
        play_body = await play_word_hunt(client, headers)
        bind_session_start(parse_started_at(play_body))
        for index, word_entry in enumerate(seeded_words):
            if index == len(seeded_words) - 1:
                advance_to_terminal()
            body = await find_word_by_coords(client, headers, word_entry)
            if body.get("result") is not None:
                break

        replay_play = await play_word_hunt(client, headers)
        assert replay_play["session_status"] == "completed"
        assert replay_play["puzzle"] is None
        assert replay_play["result"] is not None

        blocked_find = await submit_find(
            client,
            headers,
            start_row=0,
            start_col=0,
            end_row=0,
            end_col=5,
        )
        assert blocked_find["matched"] is False
        assert blocked_find["session_status"] == "completed"

        blocked_submit = await submit_session(client, headers, expect_status=409)
        assert blocked_submit["code"] == 2010
    finally:
        restore()


async def test_cheating_attempts_rejected_without_db_writes(
    client: httpx.AsyncClient,
) -> None:
    player_id = "e2e_wh_cheat"
    await insert_player(player_id, "E2E Word Hunt Cheat")
    headers = auth_headers(await login(client, player_id))
    seeded_words = await fetch_seeded_words()
    rows, cols = await fetch_puzzle_dims()

    _, _, _, restore = install_word_hunt_deterministic_controls()
    try:
        await play_word_hunt(client, headers)
        await find_word_by_coords(client, headers, seeded_words[0])
        baseline_score = 100

        async def assert_rejected(
            *,
            start_row: int,
            start_col: int,
            end_row: int,
            end_col: int,
            expect_status: int = 200,
        ) -> None:
            before = await count_finds_for_player(player_id)
            body = await submit_find(
                client,
                headers,
                start_row=start_row,
                start_col=start_col,
                end_row=end_row,
                end_col=end_col,
                expect_status=expect_status,
            )
            if expect_status == 200:
                assert body["matched"] is False
                assert body["session_score"] == baseline_score
            after = await count_finds_for_player(player_id)
            assert after == before

        await assert_rejected(start_row=0, start_col=0, end_row=1, end_col=2)
        await assert_rejected(start_row=0, start_col=0, end_row=0, end_col=0)
        await assert_rejected(start_row=rows, start_col=0, end_row=rows, end_col=4)
        await assert_rejected(start_row=0, start_col=0, end_row=0, end_col=cols)
        await assert_rejected(start_row=1, start_col=1, end_row=1, end_col=4)
        await assert_rejected(
            start_row=seeded_words[0]["start_row"],
            start_col=seeded_words[0]["start_col"],
            end_row=seeded_words[0]["end_row"],
            end_col=seeded_words[0]["end_col"],
        )
    finally:
        restore()


async def test_collision_case_first_trace_wins(
    client: httpx.AsyncClient,
) -> None:
    """Two linear CAT traces exist; only the first credits the find."""
    player_id = "e2e_wh_collision"
    await insert_player(player_id, "E2E Word Hunt Collision")
    headers = auth_headers(await login(client, player_id))

    await install_collision_puzzle()
    try:
        await play_word_hunt(client, headers)

        vertical = await submit_find(
            client,
            headers,
            start_row=0,
            start_col=0,
            end_row=2,
            end_col=0,
        )
        assert vertical["matched"] is True
        assert vertical["word"]["word"] == "CAT"
        assert await count_finds_for_player(player_id) == 1

        horizontal = await submit_find(
            client,
            headers,
            start_row=0,
            start_col=0,
            end_row=0,
            end_col=2,
        )
        assert horizontal["matched"] is False
        assert await count_finds_for_player(player_id) == 1
    finally:
        await restore_word_hunt_production_seed()


async def test_time_bonus_determinism_at_boundary(
    client: httpx.AsyncClient,
) -> None:
    """Completing at elapsed_ms=300_000 yields time_bonus=250."""
    player_id = "e2e_wh_time_bonus"
    await insert_player(player_id, "E2E Word Hunt Time Bonus")
    headers = auth_headers(await login(client, player_id))
    seeded_words = await fetch_seeded_words()

    bind_session_start, advance_to_terminal, _, restore = install_word_hunt_deterministic_controls(
        terminal_elapsed_ms=_TERMINAL_ELAPSED_MS,
    )
    try:
        play_body = await play_word_hunt(client, headers)
        bind_session_start(parse_started_at(play_body))
        last: dict | None = None
        for index, word_entry in enumerate(seeded_words):
            if index == len(seeded_words) - 1:
                advance_to_terminal()
            last = await find_word_by_coords(client, headers, word_entry)

        assert last is not None
        result = last["result"]
        assert result is not None
        assert result["time_elapsed_ms"] == _TERMINAL_ELAPSED_MS
        assert result["time_bonus"] == _TIME_BONUS == 250
        expected_score = expected_terminal_score(len(seeded_words), _TERMINAL_ELAPSED_MS)
        assert result["score"] == expected_score
        assert await fetch_persisted_session_score(player_id) == expected_score
        await _assert_completed_lobby_and_leaderboard(
            client,
            headers,
            player_id,
            expected_score,
        )
    finally:
        restore()
