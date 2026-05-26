# Sub-4: E2E API Tests

**Type:** AFK
**Status:** done
**Depends on:** Sub-2
**Blocks:** nothing

## Parent

`docs/issues/four-pics-one-lie/parent.md`

## What to build

Add end-to-end API journey tests for Four Pics that exercise the full HTTP stack against a real (test) database, mirroring the existing `backend/tests/e2e/` structure used by Rapid Fire, Wiki, and Pinpoint.

End-to-end behaviour delivered:

1. **`backend/tests/e2e/test_four_pics_journey.py`** — full-pool happy-path playthrough:
   - Login as a seeded player
   - Confirm the Four Pics tile is `not_started` via `GET /players/me/sessions`
   - `POST /games/four-pics/play` to start the session; assert `question` is returned with 4 image paths and no `odd_one_out_index`
   - Loop over every seeded question, alternating correct and wrong taps to exercise both score paths
   - Assert each `POST /answer` response shape: `correct`, `score`, `time_bonus`, advancing `question`, `session_score` accumulating correctly
   - On the final answer, assert `question == null`, `result` is populated, and `session_status == "completed"`
   - Assert the final `session_score` equals the sum of expected per-question scores under the time-bonus formula (use a controllable clock or assert with tolerance bounds rather than exact ms)
   - Assert the lobby tile flips to `completed`
   - Assert the leaderboard reflects the new session score
2. **`backend/tests/e2e/test_four_pics_lifecycle_journeys.py`** — abandon and resume journeys:
   - **Abandon mid-session:** start, answer one or two questions, `POST /games/four-pics/abandon`, assert `result.questions_not_reached > 0`, assert session is `abandoned` with the partial score persisted, assert tile shows `abandoned`, assert no further `play` / `answer` is accepted (returns 409)
   - **Refresh mid-question:** start, call `POST /play` twice with no intervening answer, assert the second response returns the **same** `question_id` and **same** `started_at` (idempotency)
   - **Replay protection:** after a successful playthrough, attempt a fresh `POST /play` and assert it returns the result block (or 409 depending on the convention used by other games — match the convention of Rapid Fire / Pinpoint)
3. **Test infrastructure** — reuse the existing `backend/tests/e2e/` fixtures (DB setup, seeded players, login helper, HTTP client). Add Four Pics-specific seed fixtures only if the existing seed loader doesn't already cover them.

Test design: assert **external behaviour** — HTTP responses, DB state visible via API, and integration touchpoints (lobby, leaderboard) — not internal helpers, cache contents, or service-private state.

## Acceptance criteria

- [x] `backend/tests/e2e/test_four_pics_journey.py` exists and passes against a fresh test DB; covers a full-pool playthrough with a mix of correct and wrong answers; final `session_score` equals the expected sum within the time-bonus tolerance
- [x] `test_four_pics_journey.py` asserts `odd_one_out_index` is absent from every `play` and `answer` response body
- [x] `test_four_pics_journey.py` asserts the Lobby tile (`GET /players/me/sessions`) flips to `completed` and the leaderboard reflects the score
- [x] `backend/tests/e2e/test_four_pics_lifecycle_journeys.py` exists and passes; covers abandon-mid-session, refresh-mid-question idempotency, and post-completion replay protection
- [x] After abandon, the lifecycle test asserts `session_status == "abandoned"`, `result.questions_not_reached` matches the count of unattempted questions, and subsequent `play` / `answer` calls are rejected appropriately
- [x] Refresh-mid-question test asserts `question_id` and `started_at` are stable across consecutive `POST /play` calls with no intervening answer
- [x] Tests follow existing e2e patterns (fixtures, login helper, HTTP client) and do not introduce new test infrastructure unless strictly required
- [x] Tests run in CI alongside existing e2e suites and complete within a reasonable time budget

## Blocked by

Sub-2 — the lifecycle test asserts behaviour of the `abandon` endpoint, which ships in Sub-2. Sub-1 alone is insufficient.
