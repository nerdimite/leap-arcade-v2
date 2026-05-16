# Sub-3: Rapid Fire Subcutaneous Tests

**Status:** done  
**Blocked by:** ~~Sub-1~~ (complete)  
**Blocks:** nothing

## What to build

Write the full subcutaneous test suite for the three Rapid Fire routes using `TestClient` + `app.dependency_overrides`. These tests verify end-to-end behaviour through the HTTP surface — status codes, response body shape, field presence and absence — without touching a real database.

The Rapid Fire implementation (routes, service, schemas, DAOs, scoring) is already in place. This slice adds the missing behavioural verification. Tests live under `tests/unit/api/rapid_fire/`.

The `compute_rapid_fire_score` pure function already has its own test file (`tests/unit/games/rapid_fire/test_scoring.py`) and should not be duplicated here.

### `POST /games/rapid-fire/play`

| Case | Expected |
|---|---|
| New player (no existing session) | 200, `status="active"`, `question` present, `game_session_id` present, `questions_answered=0` |
| Mid-game resume (active session, some answers recorded) | 200, `status="active"`, `question` present, `questions_answered` reflects answers so far, returned question not in previously asked set |
| Completed session | 200, `status="completed"`, `result` block present, `question` absent |
| Abandoned session | 200, `status="abandoned"`, `result` block present, `question` absent |
| No JWT | 401 |

### `POST /games/rapid-fire/answer`

| Case | Expected |
|---|---|
| Correct answer | 200, `correct=true`, `current_score > 0`, `next_question` present |
| Wrong answer | 200, `correct=false`, `current_score=0`, `next_question` present, `correct_option` and `correct_answer_text` present |
| Skipped (`selected_option=null`) | 200, `correct=false`, `current_score=0`, `next_question` present |
| Last question (game over) | 200, `next_question=null`, `result` block present with score and counts |
| Replay same `question_id` | 409 |
| `selected_option=5` | 422 |
| No active session | 404 |
| No JWT | 401 |

Additional invariant to verify: `correct_option_index` must be absent from any `QuestionSchema` in the response (including `next_question`).

### `POST /games/rapid-fire/abandon`

| Case | Expected |
|---|---|
| Abandon with answers submitted | 200, `result.score > 0`, counts reflect submitted answers |
| Abandon with 0 answers | 200, `result.score=0`, all counts 0 |
| Already completed session | 409 |
| No active session | 404 |
| No JWT | 401 |

## Acceptance criteria

- [x] All `play` cases above pass through `TestClient` with fake DAOs
- [x] All `answer` cases above pass; `correct_option_index` absent from `QuestionSchema` in every response
- [x] All `abandon` cases above pass
- [x] 401 is verified for all three routes when no `Authorization` header is provided
- [x] No test calls service methods or DAO methods directly — all assertions are on HTTP response status and body
- [x] Tests use the fake infrastructure established in Sub-1 (`app.dependency_overrides`, auth fixture)
- [x] `uv run pytest tests/unit/api/rapid_fire/ -v` passes cleanly

## Blocked by

~~Sub-1 (test infrastructure + updated fakes required)~~ — complete.
