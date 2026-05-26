# Sub-5: E2E API Tests

**Type:** AFK
**Status:** done
**Depends on:** Sub-3
**Blocks:** nothing

## Parent

`docs/issues/picture-illustration/parent.md`

## What to build

End-to-end API tests covering all behaviours of the Picture Illustration game. Tests exercise the full HTTP surface (FastAPI test client through to a real Postgres test database) and validate external behaviour only — no service-internal assertions, no mocked DAOs.

Mirrors the patterns in `backend/tests/e2e/` for Rapid Fire and Wikipedia Speed Run.

End-to-end behaviour delivered:

1. **Happy path** — create player, login, `play` returns first puzzle, submit correct answers for all 5 puzzles, final answer returns inline result with `score` reflecting all-correct first-attempt scoring + time bonus
2. **Wrong then correct** — submit wrong answer, response is `correct=false, next_puzzle=null`, `play` again returns the SAME puzzle, submit correct on second attempt, `score_earned=150`
3. **Accepted variation matching** — submit answers using each variation listed in seed data (e.g. `"NLP"`, `"Natural Language Processing"`, `"natural language models"` for the same puzzle); all should match
4. **Normalisation edge cases** — submit answers with mixed case, hyphens, dots, leading/trailing whitespace, double internal spaces; all should match the canonical accepted answers
5. **Skip path** — `submit_answer` with `submitted_answer: null` advances to next puzzle; skipped puzzle is not served again; final puzzle skipped → result block with that puzzle marked `skipped` and 0 pts
6. **Abandon mid-game** — `POST /abandon` after some puzzles resolved → session `completed`, `score = accuracy_score` (time_bonus=0), result block reflects `not_reached` for remaining puzzles
7. **Abandon with no session** — `POST /abandon` for a player with no picture session → 404
8. **Abandon already completed** — `POST /abandon` after the session is already `completed` → 409
9. **Replay protection** — submit a correct answer for puzzle X, then submit again for puzzle X → 409
10. **Session locked once completed** — `POST /play` after `completed` returns the result block; submitting answer after `completed` → 409
11. **Resume across `play` calls** — call `play`, do not submit, call `play` again → returns the same active session (session_id matches), still serves an unresolved puzzle
12. **Server-side time-limit enforcement** — simulate a session whose `started_at` is older than `PICTURE_TIME_LIMIT_MS` (insert directly or use a clock fake); next `submit_answer` causes the session to be closed as `completed` with `time_bonus=0`
13. **Canonical answers never leak** — assert that no API response (play, answer, abandon) ever contains the `canonical_answer` or the `accepted_answers` list

## Acceptance criteria

- [x] Test file exists alongside other game e2e suites under `backend/tests/e2e/`
- [x] All 13 scenarios above are covered by named test cases
- [x] Tests use the existing e2e fixtures (test DB, test client, login helper) — do not introduce a parallel test infrastructure
- [x] No test asserts on internal service state — only on HTTP responses, DB rows where relevant, and game_session.status / .score
- [x] All tests pass against the implementation produced by Sub-1 + Sub-2 + Sub-3 (and ideally Sub-4 for the response shape, but Sub-4 is not a strict prerequisite)
- [x] Suite runs in under 30 seconds locally — no real timer-waits; use clock fakes or direct DB inserts for time-elapsed scenarios

### Implementation notes (tests vs wording above)

- **Scenario 2 ("play again → same puzzle"):** Current `PictureService.play` picks a random unresolved puzzle on each `/play`. The e2e asserts the intended streak/scoring behaviour via **two consecutive `/answer` calls** on the same `puzzle_id` after a wrong attempt (`next_puzzle=null`), rather than inserting `/play` between wrong and correct.
- **Scenario 11:** Assertions cover **same `game_session_id`, unchanged `puzzles_answered`, still active**; surfaced `puzzle.id` may differ across `/play` calls because of random reshuffling among unresolved puzzles (PRD).

## Blocked by

Sub-3 — the abandon endpoint, time bonus, and final result schema shape must all be in place to write meaningful e2e coverage.
