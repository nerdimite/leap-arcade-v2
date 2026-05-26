# Sub-1: Happy-Path Tracer Bullet

**Type:** AFK
**Status:** done
**Depends on:** nothing
**Blocks:** Sub-2, Sub-3

## Parent

`docs/issues/picture-illustration/parent.md`

## What to build

A thin vertical slice that proves the entire stack lights up: a player can log in, navigate to the Picture Illustration tile, type free-text answers, complete all seeded puzzles, and see a basic score on a minimal result screen.

This slice does NOT include skip support, the global Session Timer, the abandon endpoint, the time bonus, or the polished result screen — those land in Sub-2, Sub-3, and Sub-4. Wrong answers are reported but there is no required UX polish (shake animation, auto-clear) yet.

End-to-end behaviour delivered:

1. **DB** — two new tables (`picture_puzzles`, `picture_puzzle_attempts`) with appropriate columns, FKs, and constraints. Alembic migration.
2. **Seed** — `picture.json` with 5 entries: 3 for the known example images (`huggingface.png`, `large_language_model.png`, `nlp.png`) plus 2 placeholder puzzles. Each entry contains `image_filename`, `canonical_answer`, and a pre-normalised lowercase list of `accepted_answers`. Loader is idempotent (`ON CONFLICT DO NOTHING / DO UPDATE`) per project convention.
3. **Backend** — ORM models, `PicturePuzzleDAO`, `PicturePuzzleAttemptDAO`, internal types (`PicturePuzzleDTO`, `PicturePuzzleAttemptDTO`, `PictureResultDTO`, `PicturePlayPayload`, `PictureAnswerPayload`).
4. **Scoring module** — pure functions: `normalize_answer` (the full pipeline: lowercase + strip punctuation + collapse whitespace + trim), `score_per_puzzle(attempt_count)` returning 200/150/100/50, `compute_total_score` for the accuracy component only (time bonus is added in Sub-3).
5. **Service** — `PictureService` with `play(player_id)` and `submit_answer(player_id, puzzle_id, submitted_answer)`. Warms a puzzle cache from DB at startup via `initialize(session)` called from app lifespan, mirroring `RapidFireService`. On answer submit: normalises both submitted answer and accepted-answer entries, matches via membership; on match (or any resolution), creates an attempt row and the puzzle is considered resolved. On the final puzzle resolution, marks session `completed` and returns inline result.
6. **Routes** — `POST /games/picture/play` and `POST /games/picture/answer` mapping DTOs ↔ API schema. Schema does not expose `canonical_answer` or `accepted_answers` to the frontend.
7. **Frontend** — replace the existing stub `(games)/picture/page.tsx` with a real game shell: image element rendering `/games/picture/<filename>`, a text input, a Submit button, an inline area for wrong-answer feedback ("Incorrect, try again."), and a minimal result block on game end (just total score + "Back to Lobby"). Typed API client wrappers under `frontend/src/lib/api/picture.ts`.
8. **Static assets** — copy the 3 example images from `docs/games-examples/picture-illustration/` into `frontend/public/games/picture/`. Add 2 placeholder PNGs for the remaining puzzles (filename consistency with seed data is required and must be verified at implementation time).

The `submit_answer` API contract for this slice:

```
body: { puzzle_id: str, submitted_answer: str }
response: {
  correct: bool,
  score_earned: int,           # 0 on wrong; populated on correct resolution
  current_score: int,
  puzzles_solved: int,
  puzzles_remaining: int,
  next_puzzle: PuzzleSchema | null,   # null on wrong (stay on puzzle) or game over
  result: ResultSchema | null         # populated only on game over
}
```

`ResultSchema` for this slice contains only: `score`, `puzzles` (list of `{ puzzle_id, image_filename, status: correct|skipped|not_reached, score_earned }`). `accuracy_score`, `time_bonus`, and `time_remaining_seconds` will be added in Sub-3 alongside the time bonus.

## Acceptance criteria

- [x] `picture_puzzles` and `picture_puzzle_attempts` tables exist after migration; FKs and nullability match the PRD schema
- [x] `picture.json` seed loads 5 rows on startup; idempotent re-runs do not duplicate
- [x] `normalize_answer` correctly handles: lowercase, hyphen removal, dot removal, mixed punctuation, collapsed whitespace, trimmed edges
- [x] `score_per_puzzle` returns 200 / 150 / 100 / 50 for attempt counts 1 / 2 / 3 / 4+
- [x] `POST /games/picture/play` for a new player creates a session and returns the first puzzle
- [x] `POST /games/picture/play` mid-game returns an unresolved puzzle (one with no `correct=true` or `skipped=true` attempt row); puzzles already resolved are not served again
- [x] `POST /games/picture/answer` with a wrong answer returns `correct=false`, `next_puzzle=null`, creates an attempt row with `correct=false, skipped=false`
- [x] `POST /games/picture/answer` with a correct answer (in any accepted variation, including punctuation/case/whitespace variants) returns `correct=true`, `score_earned` reflecting the attempt count for that puzzle, advances `next_puzzle` to a different unresolved one
- [x] `POST /games/picture/answer` resolving the final puzzle returns `next_puzzle=null` and an inline `result` block; session is marked `completed` with the final score persisted on `game_sessions.score`
- [x] Replay protection: submitting an answer for a `puzzle_id` that already has a `correct=true` or `skipped=true` row returns 409
- [x] Frontend `(games)/picture/page.tsx` no longer renders the placeholder; player can play through the full game using only correct answers
- [x] All 5 image filenames referenced in seed data exist under `frontend/public/games/picture/`
- [x] Unit tests for `scoring.py` and `PictureService` happy paths pass; tests use hand-written DAO fakes (no `MagicMock`) per project convention

## Notes (implementation)

- Example images were not present under `docs/games-examples/picture-illustration/` in this checkout; minimal valid PNGs were written under `frontend/public/games/picture/` for all five seed filenames instead.
- `docs/games-examples/...` can still be synced later to swap in the real illustration assets without changing filenames.

## Blocked by

None — can start immediately.
