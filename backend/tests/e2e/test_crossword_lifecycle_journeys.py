"""Crossword lifecycle e2e journeys: partial submit, resume, cheating, time bonus."""

from __future__ import annotations

import httpx

from tests.e2e.crossword_helpers import (
    _UNKNOWN_ENTRY_ID,
    assert_clues_hide_unsolved_entries,
    assert_no_unsolved_answer_text_in_payload,
    assert_skeleton_has_no_letters,
    assert_completed_lobby_and_leaderboard,
    auth_headers,
    check_entry,
    count_solves_for_player,
    crossword_session_row,
    expected_terminal_score,
    expected_time_bonus,
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
    submit_session,
    unsolved_answers,
)

_TERMINAL_ELAPSED_MS = 300_000
_TIME_BONUS = expected_time_bonus(_TERMINAL_ELAPSED_MS)


def _cell_structure(cells: list) -> list:
    """Open/blocked layout and corner numbers — letters are excluded."""
    out: list = []
    for row in cells:
        out_row: list = []
        for cell in row:
            if cell is None:
                out_row.append(None)
            else:
                out_row.append((cell["row"], cell["col"], cell.get("number")))
        out.append(out_row)
    return out


async def _partial_solve_across(
    client: httpx.AsyncClient,
    headers: dict[str, str],
    entries: list[dict],
    bind_session_start,
) -> tuple[dict, list[str]]:
    play_body = await play_crossword(client, headers)
    bind_session_start(parse_started_at(play_body))
    across = next(e for e in entries if e["direction"] == "across")
    await check_entry(client, headers, across["entry_id"], across["answer"])
    unsolved = unsolved_answers(entries, {across["entry_id"]})
    return play_body, unsolved


async def test_shared_cell_double_credit(
    client: httpx.AsyncClient,
) -> None:
    """Intersection at (0,0): solving across and down each awards 100 independently."""
    await install_e2e_crossword_puzzle()
    player_id = "e2e_xw_shared"
    await insert_player(player_id, "E2E Crossword Shared")
    headers = auth_headers(await login(client, player_id))
    entries = await fetch_seeded_entries()
    across = next(e for e in entries if e["direction"] == "across")
    down = next(e for e in entries if e["direction"] == "down")

    _, _, _, restore_clock = install_crossword_deterministic_controls()
    try:
        await play_crossword(client, headers)

        first = await check_entry(client, headers, across["entry_id"], across["answer"])
        assert first["correct"] is True
        assert first["session_score"] == 100

        second = await check_entry(client, headers, down["entry_id"], down["answer"])
        assert second["correct"] is True
        assert second["session_status"] == "completed"
        assert second["session_score"] == expected_terminal_score(2, 0)
        assert second["result"] is not None
        assert second["result"]["base_score"] == 200
        assert second["result"]["solved_count"] == 2
        assert await count_solves_for_player(player_id) == 2
    finally:
        restore_clock()
        await restore_crossword_production_seed()


async def test_partial_solve_then_submit(
    client: httpx.AsyncClient,
) -> None:
    """Solve one entry, submit early, and never leak the other answer."""
    await install_e2e_crossword_puzzle()
    player_id = "e2e_xw_partial"
    await insert_player(player_id, "E2E Crossword Partial")
    headers = auth_headers(await login(client, player_id))
    entries = await fetch_seeded_entries()

    bind_session_start, advance_to_terminal, _, restore_clock = install_crossword_deterministic_controls(
        terminal_elapsed_ms=_TERMINAL_ELAPSED_MS,
    )
    try:
        _, unfound = await _partial_solve_across(
            client,
            headers,
            entries,
            bind_session_start,
        )
        advance_to_terminal()
        submit_body = await submit_session(client, headers)
        result = submit_body["result"]
        expected_score = expected_terminal_score(1, _TERMINAL_ELAPSED_MS)
        assert result["score"] == expected_score
        assert result["base_score"] == 100
        assert result["time_bonus"] == _TIME_BONUS
        assert result["solved_count"] == 1
        assert len(result["solved_entries"]) == 1
        assert_no_unsolved_answer_text_in_payload(submit_body, unfound)
        await assert_completed_lobby_and_leaderboard(
            client,
            headers,
            player_id,
            expected_score,
        )
    finally:
        restore_clock()
        await restore_crossword_production_seed()


async def test_mid_game_refresh_resume(
    client: httpx.AsyncClient,
) -> None:
    """Re-calling /play returns the same skeleton with solved clues hydrated."""
    await install_e2e_crossword_puzzle()
    player_id = "e2e_xw_refresh"
    await insert_player(player_id, "E2E Crossword Refresh")
    headers = auth_headers(await login(client, player_id))
    entries = await fetch_seeded_entries()
    across = next(e for e in entries if e["direction"] == "across")

    _, _, _, restore_clock = install_crossword_deterministic_controls()
    try:
        first_play = await play_crossword(client, headers)
        puzzle = first_play["puzzle"]
        assert puzzle is not None
        started_at = puzzle["started_at"]
        structure_before = _cell_structure(puzzle["cells"])
        assert_skeleton_has_no_letters(puzzle)

        await check_entry(client, headers, across["entry_id"], across["answer"])

        resumed = await play_crossword(client, headers)
        assert resumed["session_status"] == "active"
        assert resumed["session_score"] == 100
        resumed_puzzle = resumed["puzzle"]
        assert resumed_puzzle is not None
        assert _cell_structure(resumed_puzzle["cells"]) == structure_before
        assert resumed_puzzle["started_at"] == started_at
        assert resumed_puzzle["solved_count"] == 1

        solved_clue = next(c for c in resumed_puzzle["clues"] if c["entry_id"] == across["entry_id"])
        assert solved_clue["solved"] is True
        assert solved_clue["answer"] == across["answer"]
        assert solved_clue["cells"] is not None

        for row in resumed_puzzle["cells"]:
            for cell in row:
                if cell is None:
                    continue
                if (cell["row"], cell["col"]) in {(0, 0), (0, 1), (0, 2)}:
                    assert cell["letter"] is not None
                else:
                    assert cell.get("letter") is None

        unsolved = unsolved_answers(entries, {across["entry_id"]})
        assert_no_unsolved_answer_text_in_payload(resumed, unsolved)
        assert_clues_hide_unsolved_entries(
            [c for c in resumed_puzzle["clues"] if not c["solved"]],
        )
    finally:
        restore_clock()
        await restore_crossword_production_seed()


async def test_navigation_guard_submit_equivalence(
    client: httpx.AsyncClient,
) -> None:
    """POST /submit from identical partial progress yields byte-equivalent results."""
    await install_e2e_crossword_puzzle()
    entries = await fetch_seeded_entries()
    bind_session_start, advance_to_terminal, reset_terminal, restore_clock = (
        install_crossword_deterministic_controls(
            terminal_elapsed_ms=_TERMINAL_ELAPSED_MS,
        )
    )
    try:
        player_a = "e2e_xw_nav_a"
        player_b = "e2e_xw_nav_b"
        await insert_player(player_a, "E2E Crossword Nav A")
        await insert_player(player_b, "E2E Crossword Nav B")
        headers_a = auth_headers(await login(client, player_a))
        headers_b = auth_headers(await login(client, player_b))

        play_a, _ = await _partial_solve_across(
            client,
            headers_a,
            entries,
            bind_session_start,
        )
        play_b, _ = await _partial_solve_across(
            client,
            headers_b,
            entries,
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
        expected_score = expected_terminal_score(1, _TERMINAL_ELAPSED_MS)
        assert result_a["score"] == expected_score
        assert result_a["time_bonus"] == _TIME_BONUS
    finally:
        restore_clock()
        await restore_crossword_production_seed()


async def test_abandon_endpoint_returns_404(client: httpx.AsyncClient) -> None:
    await install_e2e_crossword_puzzle()
    player_id = "e2e_xw_no_abandon"
    await insert_player(player_id, "E2E Crossword No Abandon")
    headers = auth_headers(await login(client, player_id))
    try:
        await play_crossword(client, headers)
        abandon = await client.post("/games/crossword/abandon", headers=headers)
        assert abandon.status_code == 404
    finally:
        await restore_crossword_production_seed()


async def test_reentry_after_completion(
    client: httpx.AsyncClient,
) -> None:
    """Completed session: /play returns result; /check and /submit return 409."""
    await install_e2e_crossword_puzzle()
    player_id = "e2e_xw_reentry"
    await insert_player(player_id, "E2E Crossword Reentry")
    headers = auth_headers(await login(client, player_id))
    entries = await fetch_seeded_entries()

    bind_session_start, advance_to_terminal, _, restore_clock = install_crossword_deterministic_controls(
        terminal_elapsed_ms=_TERMINAL_ELAPSED_MS,
    )
    try:
        play_body = await play_crossword(client, headers)
        bind_session_start(parse_started_at(play_body))
        for index, entry in enumerate(entries):
            if index == len(entries) - 1:
                advance_to_terminal()
            body = await check_entry(
                client,
                headers,
                entry["entry_id"],
                entry["answer"],
            )
            if body.get("result") is not None:
                break

        replay_play = await play_crossword(client, headers)
        assert replay_play["session_status"] == "completed"
        assert replay_play["puzzle"] is None
        assert replay_play["result"] is not None

        blocked_check = await check_entry(
            client,
            headers,
            entries[0]["entry_id"],
            entries[0]["answer"],
            expect_status=409,
        )
        assert blocked_check["code"] == 2011

        blocked_submit = await submit_session(client, headers, expect_status=409)
        assert blocked_submit["code"] == 2011
    finally:
        restore_clock()
        await restore_crossword_production_seed()


async def test_cheating_attempts_rejected_without_db_writes(
    client: httpx.AsyncClient,
) -> None:
    """Malformed checks return correct=false and do not insert crossword_solves rows."""
    await install_e2e_crossword_puzzle()
    player_id = "e2e_xw_cheat"
    await insert_player(player_id, "E2E Crossword Cheat")
    headers = auth_headers(await login(client, player_id))
    entries = await fetch_seeded_entries()
    across = next(e for e in entries if e["direction"] == "across")
    down = next(e for e in entries if e["direction"] == "down")

    _, _, _, restore_clock = install_crossword_deterministic_controls()
    try:
        await play_crossword(client, headers)
        await check_entry(client, headers, across["entry_id"], across["answer"])
        baseline_score = 100

        async def assert_rejected(entry_id: str, letters: str) -> None:
            before = await count_solves_for_player(player_id)
            body = await check_entry(client, headers, entry_id, letters)
            assert body["correct"] is False
            assert body["session_score"] == baseline_score
            after = await count_solves_for_player(player_id)
            assert after == before

        await assert_rejected(_UNKNOWN_ENTRY_ID, "FOO")
        await assert_rejected(down["entry_id"], "FI")
        await assert_rejected(down["entry_id"], "BAR")
        await assert_rejected(across["entry_id"], across["answer"])
    finally:
        restore_clock()
        await restore_crossword_production_seed()


async def test_duplicate_solve_idempotency(
    client: httpx.AsyncClient,
) -> None:
    """Re-checking a solved entry does not double-score or add a second solve row."""
    await install_e2e_crossword_puzzle()
    player_id = "e2e_xw_dup"
    await insert_player(player_id, "E2E Crossword Dup")
    headers = auth_headers(await login(client, player_id))
    entries = await fetch_seeded_entries()
    across = next(e for e in entries if e["direction"] == "across")

    _, _, _, restore_clock = install_crossword_deterministic_controls()
    try:
        await play_crossword(client, headers)
        first = await check_entry(client, headers, across["entry_id"], across["answer"])
        assert first["correct"] is True
        assert await count_solves_for_player(player_id) == 1

        second = await check_entry(client, headers, across["entry_id"], across["answer"])
        assert second["correct"] is False
        assert second["session_score"] == 100
        assert await count_solves_for_player(player_id) == 1
    finally:
        restore_clock()
        await restore_crossword_production_seed()


async def test_time_bonus_determinism_at_boundary(
    client: httpx.AsyncClient,
) -> None:
    """Completing at elapsed_ms=300_000 yields time_bonus=250."""
    await install_e2e_crossword_puzzle()
    player_id = "e2e_xw_time_bonus"
    await insert_player(player_id, "E2E Crossword Time Bonus")
    headers = auth_headers(await login(client, player_id))
    entries = await fetch_seeded_entries()

    bind_session_start, advance_to_terminal, _, restore_clock = install_crossword_deterministic_controls(
        terminal_elapsed_ms=_TERMINAL_ELAPSED_MS,
    )
    try:
        play_body = await play_crossword(client, headers)
        bind_session_start(parse_started_at(play_body))
        last: dict | None = None
        for index, entry in enumerate(entries):
            if index == len(entries) - 1:
                advance_to_terminal()
            last = await check_entry(
                client,
                headers,
                entry["entry_id"],
                entry["answer"],
            )

        assert last is not None
        result = last["result"]
        assert result is not None
        assert result["time_elapsed_ms"] == _TERMINAL_ELAPSED_MS
        assert result["time_bonus"] == _TIME_BONUS == 250
        expected_score = expected_terminal_score(len(entries), _TERMINAL_ELAPSED_MS)
        assert result["score"] == expected_score
        assert await fetch_persisted_session_score(player_id) == expected_score
        await assert_completed_lobby_and_leaderboard(
            client,
            headers,
            player_id,
            expected_score,
        )
    finally:
        restore_clock()
        await restore_crossword_production_seed()
