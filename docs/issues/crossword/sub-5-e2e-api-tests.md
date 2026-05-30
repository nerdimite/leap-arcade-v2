# Sub-5: E2E API Journey Tests

**Type:** AFK
**Status:** todo
**Depends on:** Sub-1, Sub-2, Sub-3, Sub-4
**Blocks:** nothing

## Parent

`docs/issues/crossword/parent.md`

## What to build

End-to-end API tests in `backend/tests/e2e/` that exercise the full Crossword journey against the live FastAPI app and a real Postgres test database, mirroring the structure of existing e2e tests for Word Hunt, Pinpoint, and Picture Illustration.

A small purpose-built test seed is used (not the production 12×12 puzzle) to keep assertions tight — e.g. a tiny grid with **at least one intersection** so the shared-cell crediting path is exercised. Example: a 3×3 grid with `FOO` across at row 0 and `FIZ` down at col 0 sharing the `F` at (0,0).

Two test files:

### `test_crossword_journey.py` — happy-path full playthrough

- Login → start (`POST /play`) → assert the blank skeleton (open/blocked cells + corner numbers), the Across/Down clues, `solved_count = 0`, no `answer`/`cells`/`letter` on any unsolved clue or cell
- Solve every entry by submitting the correct `{entry_id, letters}` for each → assert each response: `correct=true`, the solved entry + cells, score increments by 100 each time
- Assert the `check` that solves the last entry carries `session_status="completed"` with `result` populated, including `base_score`, `time_bonus`, `time_elapsed_ms`, and exactly N solved entries (no unsolved entries)
- Assert `game_sessions.score = N * 100 + time_bonus` is persisted
- Assert `GET /players/me/sessions` reflects the Crossword session as `completed` with the correct score
- Assert the global leaderboard query reflects the score

### `test_crossword_lifecycle_journeys.py` — every other terminal path and edge case

- **Shared-cell double-credit**: filling the intersection then checking both the across and the down entry credits both independently; the running score reflects both.
- **Partial-solve then explicit submit**: solve some-but-not-all entries, then `POST /submit`. Assert session `completed`, score = `solved_count * 100 + time_bonus`, result lists exactly the solved entries. String-search the entire response JSON for any unsolved answer value → 0 hits.
- **Mid-game refresh-resume**: solve some entries, then re-call `play` (simulating a refresh). Assert: same skeleton, solved clues marked `solved=true` with `answer` + `cells`, the solved cells carry `letter`, unsolved clues/cells still blank/hidden, `session_score` reflects the running total.
- **Navigation-guard submit equivalence**: from a partial-solve state, call `POST /submit` directly (the guard's behaviour). Assert the result is identical to an explicit Submit-button press.
- **No abandon endpoint exists**: a `POST /games/crossword/abandon` call returns 404.
- **Re-entry after completion**: after a session is `completed`, `play` returns `puzzle: null` and the original `result`; `check` or `submit` returns a clear error (`CrosswordSessionAlreadyCompletedException`).
- **Cheating / malformed-input rejection** — all of the following return `correct=false` with `session_score` unchanged and no `crossword_solves` row created:
  - `entry_id` not belonging to this puzzle
  - `letters` whose length ≠ the entry's answer length
  - correct-length `letters` that don't match the entry's answer
  - re-checking an already-solved entry
- **Duplicate-solve idempotency**: checking an already-solved entry's correct letters again returns `correct=false` and does not create a second `crossword_solves` row or re-add 100.
- **Time-bonus determinism**: using an injectable clock fixture, run a journey where the session completes at simulated `elapsed_ms = 300_000` and assert `time_bonus = 250` in the result.
- **No-leak invariant**: across every terminal path above, string-search each response payload for any unsolved entry's answer text → 0 hits; assert the initial `play` skeleton carries zero letters.
- **Lobby tile + leaderboard reflect terminal state**: after each terminal path, `GET /players/me/sessions` shows the Crossword tile as `completed` with the right score; the leaderboard reflects the score.

These tests run against the same e2e harness used by other games (real Postgres, real FastAPI app, test seed loaded).

## Technical nuances (must get right)

- **Test seed must contain an intersection** — without a shared cell, the most crossword-specific path (one fill crediting two entries) goes untested.
- **No-leak assertions are string-searches, not field checks** — search the raw JSON for unsolved answer substrings so a future schema change can't silently start leaking.
- **Cheating assertions check BOTH the response AND the DB** — `correct=false` is necessary but not sufficient; assert no `crossword_solves` row was written.
- **Injectable clock drives the time-bonus assertion** — don't rely on wall-clock timing; advance the fake clock to hit the exact boundary value.
- **Guard-equivalence is an explicit assertion** — the guard `/submit` and the button `/submit` must produce byte-equivalent results from the same state.

## Acceptance criteria

- [ ] `test_crossword_journey.py` and `test_crossword_lifecycle_journeys.py` exist under `backend/tests/e2e/`
- [ ] Both test files pass against the e2e harness
- [ ] Happy-path journey asserts the final persisted `game_sessions.score = N * 100 + time_bonus`, lobby reflection, and leaderboard reflection
- [ ] Shared-cell double-credit path is exercised and asserts both entries score
- [ ] Partial-submit, refresh-resume, and navigation-guard-equivalence scenarios all assert that no unsolved answer text appears in any response (string search → 0 hits) and that the initial skeleton carries zero letters
- [ ] All cheating/malformed-input scenarios assert `correct=false` AND no DB write
- [ ] Duplicate-solve scenario asserts no second row and no double score
- [ ] Time-bonus boundary scenario uses the injectable clock and asserts the exact `time_bonus` value
- [ ] `POST /games/crossword/abandon` returns 404 (covered explicitly)

## Blocked by

Sub-1, Sub-2, Sub-3, Sub-4 — every layer must be in place before journey tests are meaningful.
