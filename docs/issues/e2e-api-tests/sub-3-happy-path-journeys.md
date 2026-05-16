# Sub-3: Happy Path + Auth Edge Case Journeys

**Status:** done  
**Blocked by:** Sub-2 (complete)  
**Blocks:** nothing

## Parent

`docs/issues/e2e-api-tests/parent.md`

## What to build

Write two e2e journey tests in `backend/tests/e2e/` using the infrastructure from Sub-2.

**Journey 1 — Full game happy path:**
A player logs in, calls `/play` to get the first question, answers every question in sequence (using the question returned by each `/play` or `/answer` response), and reaches a `completed` session. The player then appears on the leaderboard with a non-zero score.

Test flow:
1. `POST /auth/login` with valid `corp_id` + `event_code` → extract JWT
2. `POST /games/rapid-fire/play` → get first question
3. Loop: `POST /games/rapid-fire/answer` with `selected_option` until `next_question` is null and `result` is present
4. Assert final `POST /games/rapid-fire/play` returns `status="completed"` with `result` block
5. `GET /leaderboard` → assert player appears with `score > 0`

Tests must not hard-code question IDs or question counts — they drive the loop from the API responses.

**Journey 2 — Wrong event code:**
A login attempt with an invalid event code returns 401. No player row is created in the database.

Test flow:
1. `POST /auth/login` with valid `corp_id` but wrong `event_code` → assert 401
2. Assert no **new** player rows from the failed login: count before/after unchanged (see note below).

**Note:** With the current auth order (player lookup → event check), HTTP 401 `InvalidEventCode` requires a pre-existing player row. The journey inserts one probe row, attempts login with a wrong **same-length** event code (because `secrets.compare_digest` requires equal length), then asserts the row count is unchanged—i.e. login did not mint an extra player.

## Acceptance criteria

- [x] Full game journey passes: session ends with `status="completed"`, `result.score > 0`, player present on leaderboard
- [x] Journey does not hard-code question IDs or assume a specific question count (`questions_total` and question ids come from `/play` / `/answer`; answer correctness is looked up by id from the DB, not by hard-coded pool size)
- [x] Wrong event code returns 401 and does not add a player row (count before/after unchanged)
- [x] Both journeys pass under `make e2e` with a real `postgres_test` database
- [x] No assertions duplicate unit test coverage (field shapes, 422s, option index absence) — only journey-level outcomes are asserted

## Blocked by

Sub-2 (`docs/issues/e2e-api-tests/sub-2-e2e-infra.md`)
