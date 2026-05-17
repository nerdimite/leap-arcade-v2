# Sub-5: E2E API Journey Tests

**Type:** AFK
**Status:** ready-for-agent
**Depends on:** Sub-2, Sub-3, Sub-4
**Blocks:** nothing

## Parent

`docs/issues/pinpoint/parent.md`

## What to build

Lock the full Pinpoint behaviour behind end-to-end journey tests that drive the FastAPI app via real HTTP, exercise the database, and assert against player-visible state. Mirrors the prior art under `backend/tests/e2e/test_journeys.py`, `test_session_lifecycle_journeys.py`, and `test_leaderboard_ranking_journey.py`.

End-to-end behaviour delivered:

1. **`backend/tests/e2e/test_pinpoint_journey.py`** — full happy-and-mixed playthrough:
   - Login as a seeded player; navigate to Pinpoint; play through the entire seeded pool.
   - Mix outcomes: solve some puzzles on clue 1, some on clue 3, fail at least one (5 wrong guesses), and solve the last on clue 5.
   - Assert: `game_sessions.status == completed`; `game_sessions.score` equals the expected sum of `base + time_bonus` per solved puzzle plus 0 per failed; result schema rows match outcomes one-for-one; the answer is absent from every response body; the leaderboard reflects the new score within one polling interval.
   - Use a fixed clock (the same injectable-clock pattern Sub-3 introduced) so the time-bonus assertions are deterministic.
2. **`backend/tests/e2e/test_pinpoint_lifecycle_journeys.py`** — abandon and resume scenarios:
   - **Abandon mid-puzzle:** start a session, submit one wrong guess (advancing to `clues_revealed = 2`), call `abandon`. Assert: session `abandoned`; the active attempt closed as `failed` with `score = 0`; remaining puzzles surface as `not_reached`; `play` after abandon returns the result; lobby tile shows `abandoned`.
   - **Refresh resume:** start a session, submit two wrong guesses (advancing to `clues_revealed = 3`), then call `play` again without guessing. Assert: same `puzzle_id`, same `clues_revealed`, same revealed clues — i.e. `play` is idempotent and the server is the source of truth.
   - **Replay protection:** after a session reaches `completed`, `guess` returns 4xx and `play` returns the result block.
3. **Test fixtures** — reuse existing seeded-player fixtures and the existing async HTTP client setup from `backend/tests/e2e/conftest.py`. Add Pinpoint-specific helpers (e.g. `solve_puzzle(client, puzzle_id, on_clue=1)`) only if they make the journey scripts readable.

These tests intentionally do NOT mock the DAO or service layers — they exercise the real stack end-to-end against the test database, consistent with the rest of `tests/e2e/`.

## Acceptance criteria

- [ ] `tests/e2e/test_pinpoint_journey.py` runs against the FastAPI app, plays through the full seeded pool with mixed outcomes, and asserts the final session score and per-puzzle result rows match expectations
- [ ] The journey test asserts that no response body contains the canonical `answer` or `answer_aliases`
- [ ] The journey test runs with a fixed clock so time-bonus assertions are deterministic
- [ ] `tests/e2e/test_pinpoint_lifecycle_journeys.py` covers abandon-mid-puzzle, refresh-resume idempotency, and post-completion replay protection
- [ ] The leaderboard journey assertion confirms that a completed Pinpoint session updates the player's total score visible via the leaderboard endpoint
- [ ] All e2e tests pass when run with `uv run pytest tests/e2e/ -v` against a clean test database

## Blocked by

Sub-2, Sub-3, Sub-4 — the failure-path UI / time-bonus scoring / abandon endpoint must all exist before the e2e suite can assert on them. (The journey tests do not depend on the badge animation itself, but they assert on the time-bonus and abandon behaviour those slices introduce.)
