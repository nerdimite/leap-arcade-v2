# Sub-4: Session Lifecycle Journeys

**Status:** done  
**Blocked by:** Sub-2  
**Blocks:** nothing

## Parent

`docs/issues/e2e-api-tests/parent.md`

## What to build

Write three e2e journey tests covering session state transitions and guard rails.

**Journey 1 — Abandon mid-game:**
A player logs in, starts a rapid fire session, answers some (but not all) questions, then abandons. The session ends with `status="abandoned"`, the partial score appears on the leaderboard, and `games_completed=0`.

Test flow:
1. `POST /auth/login` → JWT
2. `POST /games/rapid-fire/play` → start session, get first question
3. Answer 2–3 questions via `POST /games/rapid-fire/answer`
4. `POST /games/rapid-fire/abandon` → assert 200, `result.score >= 0`
5. `GET /leaderboard` → assert player present, `games_completed=0`

**Journey 2 — Resume mid-game:**
A player starts a session, answers some questions, then calls `/play` again. The resumed response returns `status="active"`, the correct `questions_answered` count, and a question that was not in the already-answered set.

Test flow:
1. `POST /auth/login` → JWT
2. `POST /games/rapid-fire/play` → start session, record question ID
3. `POST /games/rapid-fire/answer` for that question, record answered question ID
4. `POST /games/rapid-fire/play` again → assert `status="active"`, `questions_answered=1`, returned `question.id` not in answered set

**Journey 3 — Duplicate session (409):**
A player starts a session and, while it is still active, calls `/play` a second time. The second call returns 409.

Test flow:
1. `POST /auth/login` → JWT
2. `POST /games/rapid-fire/play` → 200, session created
3. `POST /games/rapid-fire/play` again immediately → assert 409

## Acceptance criteria

- [x] Abandon journey: response is 200, leaderboard shows player with `games_completed=0`
- [x] Resume journey: `questions_answered` reflects previously answered count, returned question not in answered set
- [x] Duplicate session journey: second `/play` returns 409
- [x] All three journeys pass under `make e2e`
- [x] `clean_db` fixture ensures these journeys are fully independent of each other and of Sub-3 journeys

## Blocked by

Sub-2 (`docs/issues/e2e-api-tests/sub-2-e2e-infra.md`)
