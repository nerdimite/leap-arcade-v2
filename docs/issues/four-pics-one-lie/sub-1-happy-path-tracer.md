# Sub-1: Happy-Path Tracer Bullet

**Type:** AFK
**Status:** done
**Depends on:** nothing
**Blocks:** Sub-2, Sub-3, Sub-4

## Parent

`docs/issues/four-pics-one-lie/parent.md`

## What to build

A thin vertical slice that proves the entire stack lights up: a player can log in, navigate to the Four Pics tile, see four images in a 2×2 grid, tap one to answer, see basic correct/wrong feedback, progress through every seeded question in random order, and land on a minimal result screen with a total score that reflects base + time bonus.

This slice does NOT include the `abandon` endpoint, the navigation guard wiring, the polished 2-second overlay with score breakdown, the live stopwatch UI, or the polished per-question result rows — those land in Sub-2 and Sub-3. Wrong feedback is reported but the visual treatment can be minimal (no overlay, no auto-advance delay required — instant advance is acceptable for this slice).

End-to-end behaviour delivered:

1. **DB** — two new tables (`four_pics_questions`, `four_pics_question_attempts`) with the columns, FKs, and CHECK constraints from the PRD. Alembic migration. The `game_sessions.game_id` CHECK already includes `four_pics`; no change needed there.
2. **Seed** — `four_pics.json` with at least the wearables sample question (the existing `docs/games-examples/Fourpics/round 1/` images), plus 2–3 additional placeholder questions so randomisation and progression are observable. Each entry contains `image_paths` (array of 4) and `odd_one_out_index` (0–3). Loader is idempotent (`ON CONFLICT DO NOTHING / DO UPDATE`) per project convention.
3. **Static assets** — copy/move the 4 sample images into `frontend/public/images/four-pics/wearables/` (renaming as needed). Add image sets for the placeholder questions. All paths referenced in seed JSON must exist on disk and resolve via Next.js static serving.
4. **Backend** — ORM models (`FourPicsQuestionModel`, `FourPicsQuestionAttemptModel`) registered in `leap/dao/models/__init__.py`; `FourPicsQuestionDAO` (read-only, `get_all` for cache warm; abstract `_to_orm` / `_apply_filters` stubbed with `raise NotImplementedError` per AGENTS.md); `FourPicsQuestionAttemptDAO` with `create`, `get_active_for_session`, `get_all_for_session`, `update_status_and_score`. Internal types in `leap/types/four_pics.py`.
5. **Scoring module** — `leap/games/four_pics/scoring.py`: pure functions `compute_time_bonus(elapsed_ms) -> int` and `compute_question_score(correct: bool, elapsed_ms: int) -> tuple[int, int]` (returns `(score, time_bonus)`). Constants `FOUR_PICS_BASE_SCORE = 100`, `FOUR_PICS_TIME_BONUS_MAX = 50`, `FOUR_PICS_TIME_DECAY_MS = 30_000`.
6. **Service** — `FourPicsService` with `play(player_id)` and `submit_answer(player_id, question_id, selected_index, time_ms)`. Warms a question cache from DB at startup via `initialize(session)` called from app lifespan, mirroring `RapidFireService`. Wired into `ServiceContainer`. `play` is idempotent for the active attempt. `submit_answer` clamps `time_ms` server-side to `min(client_time_ms, now − started_at)`, compares `selected_index == odd_one_out_index`, computes score via the scoring module, persists the attempt, and either advances to the next random unattempted question or marks the session `completed` and returns the inline result. Service uses an injectable clock so time-bonus tests are deterministic.
7. **Routes** — `POST /games/four-pics/play` and `POST /games/four-pics/answer` mapping DTOs ↔ API schema (`leap/api/schema/four_pics.py`). `QuestionState` exposes only `question_id`, `question_number`, `total_questions`, `image_paths`, `status`. `odd_one_out_index` MUST NOT appear in any response schema. Mounted at prefix `/games/four-pics` in `leap/api/main.py`.
8. **Frontend** — replace the existing stub `(games)/four-pics/page.tsx` with a real game shell: a 2×2 grid of four equally-sized image tiles, tap-to-answer, basic inline correct/wrong indicator (no overlay polish), and a minimal result block on game end (just total score + "Back to Lobby"). Typed API client wrappers under `frontend/src/lib/api/four-pics.ts`. React Query hooks for `play` and `answer`.
9. **Glossary** — add Four Pics terms (Four Pics Question, Four Pics Question Attempt) to `CONTEXT.md`.

The `submit_answer` API contract for this slice:

```
body: { question_id: UUID, selected_index: int (0–3), time_ms: int }
response: {
  correct: bool,
  score: int,                 # base + time_bonus on correct; 0 on wrong
  time_bonus: int,            # 0 on wrong
  session_status: "active" | "completed",
  session_score: int,
  question: QuestionState | null,    # next question; null on game over
  result: ResultSchema | null        # populated only on game over
}
```

`ResultSchema` for this slice contains `score`, `questions_correct`, `questions_wrong`, `questions_not_reached: 0` (will be nonzero only with abandon support in Sub-2), and `questions: List[{ question_id, status: "correct" | "wrong", score, time_bonus }]`.

## Acceptance criteria

- [x] `four_pics_questions` and `four_pics_question_attempts` tables exist after migration; FKs, nullability, and CHECK constraints match the PRD schema
- [x] `four_pics.json` seed loads ≥3 rows on startup; idempotent re-runs do not duplicate
- [x] All image paths referenced in seed data exist under `frontend/public/images/four-pics/`
- [x] `compute_time_bonus` returns `50` at 0 ms, `25` at 15 000 ms, `0` at 30 000 ms, `0` at 45 000 ms (clamped)
- [x] `compute_question_score(correct=True, elapsed_ms=15_000)` returns `(125, 25)`; `compute_question_score(correct=False, elapsed_ms=0)` returns `(0, 0)`
- [x] `POST /games/four-pics/play` for a new player creates a session and returns a randomly chosen first question with `status = "active"`; `odd_one_out_index` is not present in the response
- [x] `POST /games/four-pics/play` mid-game returns the same active question idempotently (same `question_id`, same `started_at`); after a terminal attempt advances to a different unattempted question
- [x] `POST /games/four-pics/answer` with the matching `selected_index` returns `correct=true`, `score = 100 + time_bonus`, persists an attempt with `status = "correct"`, and advances `question` to a different unattempted question
- [x] `POST /games/four-pics/answer` with a non-matching `selected_index` returns `correct=false`, `score=0`, `time_bonus=0`, persists an attempt with `status = "wrong"`, and advances `question` to a different unattempted question
- [x] `POST /games/four-pics/answer` resolving the final question returns `question=null` and an inline `result` block; session is marked `completed` with the final score persisted on `game_sessions.score`
- [x] Server-side time clamping: a client-submitted `time_ms` greater than `now − started_at` is clamped down before scoring
- [x] Replay protection: submitting an answer for a `question_id` that already has a terminal attempt row returns 409 (or the configured `QuestionAlreadyAnsweredException` mapping)
- [x] Submitting an answer for a `question_id` that does not match the session's currently-active attempt returns 400/409 (`InvalidQuestionIdException` mapping)
- [x] `selected_index` outside 0–3 is rejected at the schema layer with 422
- [x] Frontend `(games)/four-pics/page.tsx` no longer renders the placeholder; player can play the full game using the 2×2 grid and reach the minimal result screen
- [x] `odd_one_out_index` is not present in any HTTP response — verified by an API-level test that asserts the field is absent on `play` and `answer` responses
- [x] Unit tests for `scoring.py` and `FourPicsService` happy paths pass; tests use hand-written DAO fakes (no `MagicMock`) per project convention

## Blocked by

None — can start immediately.
