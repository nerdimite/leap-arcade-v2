# Sub-5: E2E API Journey Tests

**Type:** AFK
**Status:** ready-for-agent
**Depends on:** Sub-1, Sub-2, Sub-3, Sub-4
**Blocks:** nothing

## Parent

`docs/issues/word-hunt/parent.md`

## What to build

End-to-end API tests in `backend/tests/e2e/` that exercise the full Word Hunt journey against the live FastAPI app and a real Postgres test database, mirroring the structure of existing e2e tests for Rapid Fire, Pinpoint, and Picture Illustration.

Two test files:

### `test_word_hunt_journey.py` — happy-path full playthrough

- Login → start (`POST /play`) → assert grid + clues + `found_count = 0` + no `word` field on any unfound clue
- Find every Hidden Word in order by submitting the seeded coordinates for each → assert each response: `matched=true`, correct found word + coordinates, score increments by 100 each time
- Assert the final `find` call (the one that solves the last word) carries `session_status="completed"` with `result` populated, including `base_score`, `time_bonus`, `time_elapsed_ms`, and exactly N found words (no unfound words)
- Assert `game_sessions.score = N * 100 + time_bonus` is persisted
- Assert `GET /players/me/sessions` reflects the Word Hunt session as `completed` with the correct score
- Assert the global leaderboard query reflects the score

### `test_word_hunt_lifecycle_journeys.py` — every other terminal path and edge case

- **Partial-find then explicit submit**: find some-but-not-all words, then `POST /submit`. Assert session `completed`, score = `found_count * 100 + time_bonus`, result lists exactly the found words. Verify no `word` text for unfound words anywhere in the response payload (string search the JSON for any unfound `word` value should return 0 hits).
- **Mid-game refresh-resume**: find some words, then re-call `play` (simulating a page refresh). Assert: same grid returned, the found clues marked `found=true` with `word` + `coordinates` populated, unfound clues still hidden, `session_score` reflects the running total.
- **Navigation-guard submit equivalence**: from a partial-find state, call `POST /submit` directly (the navigation guard's behaviour). Assert the result is identical to what an explicit Submit-button press would produce.
- **No abandon endpoint exists**: a `POST /games/word-hunt/abandon` call returns 404.
- **Re-entry after completion**: after a session is `completed`, calling `play` returns `puzzle: null` and the original `result`. Calling `find` or `submit` returns a clear error (4xx / `WordHuntSessionAlreadyCompletedException`).
- **Cheating-attempt rejection**: all of the following return `matched=false` with `session_score` unchanged and no `word_hunt_finds` row created:
  - Out-of-bounds coordinates (e.g. `start_row = -1`, or `end_col = cols`)
  - Non-linear trace (e.g. `dr=1, dc=2`)
  - Single-cell "trace" where start == end
  - Linear, in-bounds trace through letters that do not spell any unsolved word
  - Linear trace that exactly matches an already-found word's path
- **Collision case**: if the seed places the same answer string in two locations (or the test fixture seeds such a puzzle), the first valid trace of either location credits the find; the second trace (of the other location) returns `matched=false` because the word is now solved.
- **Time-bonus determinism**: using an injectable clock fixture, run a journey where the session completes at simulated `elapsed_ms = 300_000` and assert `time_bonus = 250` in the result (boundary value from Sub-3).
- **Lobby tile + leaderboard reflect terminal state**: after each terminal path above, `GET /players/me/sessions` shows the Word Hunt tile as `completed` with the right score; the leaderboard reflects the score.

These tests are written against the same e2e harness used by other games (real Postgres, real FastAPI app, test seed loaded). The test seed for Word Hunt may be a small purpose-built puzzle (e.g. 5×5 grid, 3 words) to keep assertions tight — does not need to be the production seed.

## Acceptance criteria

- [ ] `test_word_hunt_journey.py` and `test_word_hunt_lifecycle_journeys.py` exist under `backend/tests/e2e/`
- [ ] Both test files pass against the e2e harness
- [ ] Happy-path journey asserts the final persisted `game_sessions.score = N * 100 + time_bonus`, lobby reflection, and leaderboard reflection
- [ ] Partial-submit, refresh-resume, and navigation-guard-equivalence scenarios all assert that unfound `word` text never appears in any response
- [ ] All cheating-attempt scenarios assert `matched=false` AND no DB write
- [ ] Time-bonus boundary scenario uses the injectable clock and asserts the exact `time_bonus` value
- [ ] `POST /games/word-hunt/abandon` returns 404 (covered explicitly)

## Blocked by

Sub-1, Sub-2, Sub-3, Sub-4 — every layer must be in place before journey tests are meaningful.
