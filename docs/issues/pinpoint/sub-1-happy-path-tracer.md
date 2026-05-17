# Sub-1: Happy-Path Tracer Bullet

**Type:** AFK
**Status:** ready-for-agent
**Depends on:** nothing
**Blocks:** Sub-2, Sub-3, Sub-4

## Parent

`docs/issues/pinpoint/parent.md`

## What to build

A thin vertical slice that proves the entire Pinpoint stack lights up: a player can log in, navigate to the Pinpoint tile, see clues appear one at a time, type guesses, work through every seeded puzzle, and see a basic total score on a minimal result screen.

This slice does NOT include time-bonus scoring, the stopwatch, the polished 5-card badge UI with reveal animations, the failure-state flash, the abandon endpoint, or the navigation guard wiring — those land in Sub-2 / Sub-3 / Sub-4. Wrong guesses still increment `clues_revealed` and reveal the next clue (the core mechanic must work), but the visual treatment is barebones (e.g. clues rendered as a plain text list).

End-to-end behaviour delivered:

1. **DB / migration / registry** — Alembic migration adds `pinpoint_puzzles` and `pinpoint_puzzle_attempts` per the PRD schema, extends the `game_sessions.game_id` CHECK constraint to include `"pinpoint"`, and `leap/config/constants.py` `GAMES` adds the `pinpoint` entry. ORM models registered in `leap/dao/models/__init__.py`.
2. **Seed** — `leap/seeds/data/pinpoint.json` seeded with at least 5 puzzles. Each entry has `answer`, `answer_aliases` (list, may include reasonable variants like singular/plural and common abbreviations), and `clue1`–`clue5`. The 3 examples from `docs/games-examples/pinpoint.json` are extended with `answer_aliases`. Loader is idempotent (`ON CONFLICT DO NOTHING / DO UPDATE`) per project convention.
3. **Backend** — `PinpointPuzzleDAO` (read-only; `get_all` for cache warm; abstract methods stubbed with `raise NotImplementedError`), `PinpointPuzzleAttemptDAO` (`create`, `get_for_session`, `get_by_session_and_puzzle`, `update_status_and_score`, `append_guess_and_increment_clues`). Internal types in `leap/types/pinpoint.py`: `PinpointPuzzleDTO`, `PinpointPuzzleAttemptDTO`, `PinpointPuzzleStateDTO`, `PinpointResultDTO`, `PinpointPlayPayload`, `PinpointGuessPayload`.
4. **Scoring module** (`leap/games/pinpoint/scoring.py`) — pure functions: `normalize_answer(s)` (`strip().lower()`), `match_answer(guess, answer, aliases)` (membership after normalisation), `base_score_for_clues(clues_revealed)` returning `(500, 400, 300, 200, 100)[clues_revealed - 1]`. The `compute_time_bonus` function is intentionally deferred to Sub-3.
5. **Service** (`leap/games/pinpoint/service.py`) — `PinpointService.play(player_id)` and `PinpointService.submit_guess(player_id, puzzle_id, guess)`. Warms a puzzle cache from the DB at startup via `initialize(session)` called from app lifespan, mirroring `RapidFireService`. `play` is idempotent: returns the current active puzzle if one exists, otherwise picks a random unattempted puzzle and creates a fresh attempt row with `clues_revealed = 1`, `started_at = now`, `status = active`. `submit_guess` enforces that `puzzle_id` matches the session's currently active puzzle; on correct guess marks `solved` with `score = base_score_for_clues(clues_revealed)` (no time bonus yet); on wrong guess with `clues_revealed < 5` increments `clues_revealed` and appends the raw guess to `guesses`; on wrong guess with `clues_revealed == 5` marks `failed` with score 0. When the final unattempted puzzle reaches a terminal status, the session is marked `completed` and `game_sessions.score` is persisted.
6. **Routes** (`leap/api/routes/games/pinpoint.py`) — `POST /games/pinpoint/play` and `POST /games/pinpoint/guess`. Schema models in `leap/api/schema/pinpoint.py`. The response shape **must never** include `answer` or `answer_aliases` — even on `solved` or `failed`. Mounted at prefix `/games/pinpoint` in `leap/api/main.py`. Wired into `ServiceContainer`.
7. **Frontend** — replace the placeholder route at `app/(games)/pinpoint/page.tsx` with a real game shell. Components: a plain text list of revealed clues, a guess input + "Guess" button, an inline area for the running session score, and a minimal result block on game end (just total score + "Back to Lobby"). Typed API client wrappers in `frontend/src/lib/api/pinpoint.ts`. React Query hooks for `play` and `guess`. Auto-advance to the next puzzle on solved/failed by re-calling `play` (no fancy 2s flash overlay yet — Sub-2 adds that).

The API contracts for this slice (subset of the final PRD contract; `time_bonus` field absent until Sub-3):

```
POST /games/pinpoint/play
  → 200 PlayResponse {
      session_status: "active" | "completed",
      session_score: int,
      puzzle: PuzzleState | null,
      result: ResultSchema | null
    }

POST /games/pinpoint/guess
  body: { puzzle_id: UUID, guess: str }
  → 200 GuessResponse {
      correct: bool,
      puzzle: PuzzleState,
      session_status: "active" | "completed",
      session_score: int,
      result: ResultSchema | null
    }
```

`PuzzleState` for this slice: `{ puzzle_id, puzzle_number, total_puzzles, clues_revealed, clues, status, score }` — no `time_bonus`. `ResultSchema` for this slice: `{ score, puzzles_solved, puzzles_failed, puzzles: [{ puzzle_id, status, clues_used, score }] }` — no `time_bonus` row, no `puzzles_not_reached` (added in Sub-4 alongside abandon).

## Acceptance criteria

- [ ] Migration creates `pinpoint_puzzles` and `pinpoint_puzzle_attempts` with the columns, FKs, and constraints described in the PRD; `(session_id, puzzle_id)` UNIQUE constraint enforced; `game_sessions.game_id` CHECK includes `pinpoint`
- [ ] `pinpoint` appears in `GAMES` and `GAME_IDS`; lobby exposes the new tile
- [ ] `pinpoint.json` seed loads at startup; idempotent re-runs do not duplicate; every puzzle has 5 clues and at least one alias
- [ ] `normalize_answer` returns `s.strip().lower()` and is idempotent
- [ ] `match_answer` accepts the canonical answer and every alias regardless of input casing or surrounding whitespace; rejects clearly wrong strings; handles empty alias list gracefully
- [ ] `base_score_for_clues` returns 500 / 400 / 300 / 200 / 100 for inputs 1 / 2 / 3 / 4 / 5; raises for out-of-range
- [ ] `POST /games/pinpoint/play` for a new player creates a session, creates an attempt row for one randomly-chosen puzzle, and returns it with `clues_revealed = 1`
- [ ] `POST /games/pinpoint/play` with an active puzzle returns the same `puzzle_id` and same `clues_revealed` (idempotent)
- [ ] `POST /games/pinpoint/guess` with a wrong guess on `clues_revealed = k < 5` returns `correct: false`, `puzzle.status: active`, `puzzle.clues_revealed = k + 1`, and an additional clue word in `puzzle.clues`
- [ ] `POST /games/pinpoint/guess` with a correct guess marks the puzzle `solved`, sets `score = base_score_for_clues(clues_revealed)`, and on the next `play` call serves a different unattempted puzzle
- [ ] `POST /games/pinpoint/guess` with a 5th wrong guess marks the puzzle `failed`, sets `score = 0`, never includes the answer in any response
- [ ] `POST /games/pinpoint/guess` with a `puzzle_id` that does not match the session's active puzzle returns 4xx (e.g. 409 / `InvalidPuzzleIdException`)
- [ ] `POST /games/pinpoint/guess` resolving the final puzzle returns `result` inline; session marked `completed`; `game_sessions.score` persisted
- [ ] No response body in any endpoint contains the canonical `answer` or `answer_aliases`
- [ ] Frontend Pinpoint page no longer renders a placeholder; player can play through the full pool with correct answers and reach the result screen
- [ ] Unit tests for `scoring.py` and `PinpointService` happy paths pass; tests use hand-written DAO fakes (no `MagicMock`) per project convention

## Blocked by

None — can start immediately.
