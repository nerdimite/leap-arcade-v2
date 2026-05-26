# Sub-1: Happy-Path Tracer Bullet

**Type:** AFK
**Status:** done
**Depends on:** nothing
**Blocks:** Sub-2, Sub-3, Sub-4

## Parent

`docs/issues/word-hunt/parent.md`

## What to build

A thin vertical slice that proves the entire Word Hunt stack lights up: a player can log in, navigate to the Word Hunt tile, see a real letter grid and the list of riddles, drag across cells to trace words, have correct traces register as Finds, and reach a basic result screen when they either find every word or press Submit.

This slice does NOT include drag-direction snapping polish, the miss red-flash, the clue-card flip animation, the time bonus, the live stopwatch, the navigation guard wiring, or the polished result breakdown — those land in Sub-2 / Sub-3 / Sub-4. The mechanic must work end-to-end, but the visual treatment is barebones (e.g. clue list rendered as plain `<ul>`; found cells highlighted with a solid background; result screen showing only `found_count / total_words` and total score).

End-to-end behaviour delivered:

1. **Foundation rename** — `leap/config/constants.py` `GAMES`: drop the `crossword` entry, add `{"id": "word_hunt", "display_name": "Word Hunt", ...}` in the existing alphabetic position. Alembic migration drops `"crossword"` from the `game_sessions.game_id` CHECK constraint and adds `"word_hunt"`. Frontend route renamed from `frontend/src/app/(games)/crossword/` to `(games)/word-hunt/`. `game-tiles.ts`, lobby constants, and any `crossword`-referencing stories updated to `word_hunt` / "Word Hunt". No string `crossword` left anywhere in the repo (excluding historical migrations and PRD prose).
2. **DB / migration** — Same Alembic migration (or a stacked second one) creates `word_hunt_puzzles`, `word_hunt_words`, and `word_hunt_finds` per the PRD schema (`(session_id, word_id)` UNIQUE on finds). ORM models registered in `leap/dao/models/__init__.py`.
3. **Pure logic modules** — `leap/games/word_hunt/scoring.py` with `WORD_HUNT_BASE_PER_WORD = 100` and `compute_base_score(found_count)`. `compute_time_bonus` and `compute_final_score` are intentionally deferred to Sub-3 (this slice's "final score" is just `found_count * 100`). `leap/games/word_hunt/grid.py` with `direction_of`, `validate_trace`, `walk_cells`, `validate_seeded_word` — full implementation; the seed loader and the service both depend on it. Unit tests for both modules pass.
4. **Seed** — `leap/seeds/data/word_hunt.json` with a single hand-edited puzzle: 2-D letter matrix (uppercase A–Z only), and a `words` array of at least 5 entries with `word`, `clue`, and `start_row` / `start_col` / `end_row` / `end_col`. The reference grid at `docs/games-examples/crossword.jpeg` is a good source for content; the content team will iterate post-merge. Seed loader is idempotent (`ON CONFLICT DO NOTHING / DO UPDATE`) per project convention and calls `grid.validate_seeded_word` on every word at startup, raising and preventing boot on mismatch.
5. **Backend** — DAOs: `WordHuntPuzzleDAO` and `WordHuntWordDAO` (read-only; `get_all_with_words` / `get_for_puzzle`; abstract methods stubbed with `raise NotImplementedError`), `WordHuntFindDAO` (`create`, `get_for_session`, `count_for_session`). Internal types in `leap/types/word_hunt.py`: `WordHuntPuzzleDTO` (includes its words), `WordHuntWordDTO`, `WordHuntFindDTO`, `WordHuntPuzzleStateDTO`, `WordHuntResultDTO`, `WordHuntPlayPayload`, `WordHuntFindPayload`, `WordHuntFoundWordDTO`.
6. **Service** (`leap/games/word_hunt/service.py`) — `WordHuntService` warms a puzzle cache from the DB at startup via `initialize(session)` from app lifespan, mirroring `RapidFireService` and `PinpointService`. Three methods:
   - `play(player_id)` — idempotent: creates the `game_sessions` row on first call, otherwise returns the existing session state. Returns the grid + clues (no answer text for unfound words; answer text + coordinates for already-found words) + running score (`found_count * 100`).
   - `submit_find(player_id, payload)` — validates the trace via `grid.validate_trace`; if invalid returns `matched=false`. Otherwise walks the cells via `grid.walk_cells`, compares case-insensitively against each unsolved word, and on a match: creates a `word_hunt_finds` row with the actual traced coordinates, recomputes `session_score = found_count * 100`, and if `found_count == total_words` marks the session `completed` and persists `game_sessions.score`. Returns `matched`, the found word (when matched), updated session score, and the result payload when the session just completed.
   - `submit(player_id)` — finalises the session as `completed`, persists `game_sessions.score = found_count * 100` (no time bonus in this slice), and returns the `ResultSchema`. Raises `WordHuntSessionAlreadyCompletedException` if the session is already `completed`.
7. **Errors** — `leap/config/errors.py`: add `NO_WORD_HUNT_PUZZLE_AVAILABLE` (3xxx) and `WORD_HUNT_SESSION_ALREADY_COMPLETED` (2xxx). Service exceptions in `leap/service/exceptions.py` subclass `BaseServiceException`.
8. **Routes** (`leap/api/routes/games/word_hunt.py`) — `POST /play`, `POST /find`, `POST /submit`. Schema models in `leap/api/schema/word_hunt.py`. The response shape for every endpoint **must never** include the `word` text for any unfound Hidden Word. Mounted at prefix `/games/word-hunt` in `leap/api/main.py`. Wired into `ServiceContainer`.
9. **Frontend** — replace the placeholder route at `app/(games)/word-hunt/page.tsx` with a real game shell. Components for this slice: a `LetterGrid` that supports pointer-drag from one cell to another and emits `{start_row, start_col, end_row, end_col}` on commit (snapping and animation polish deferred to Sub-2), a plain clue list (unstyled `<ul>`; flip animation deferred to Sub-2), and a minimal inline result block on game end (just `found_count / total_words` + total score + "Back to Lobby"). Typed API client wrappers in `frontend/src/lib/api/word-hunt.ts`. React Query hooks for `play`, `find`, `submit`. A visible Submit button that calls `/submit`. Auto-complete behaviour: when `/find` response carries `session_status="completed"`, transition to the result block.

API contracts for this slice (subset of the final PRD contract; `time_bonus` and `base_score` fields absent until Sub-3; polished result fields like `time_elapsed_ms` deferred to Sub-3/Sub-4):

```
POST /games/word-hunt/play
  → 200 PlayResponse {
      session_status: "active" | "completed",
      session_score: int,
      puzzle: PuzzleState | null,
      result: ResultSchema | null
    }

POST /games/word-hunt/find
  body: { start_row: int, start_col: int, end_row: int, end_col: int }
  → 200 FindResponse {
      matched: bool,
      word: FoundWord | null,
      session_status: "active" | "completed",
      session_score: int,
      result: ResultSchema | null
    }

POST /games/word-hunt/submit
  → 200 SubmitResponse { result: ResultSchema }
```

`PuzzleState` for this slice: `{ puzzle_id, rows, cols, grid, clues, found_count, total_words }` — no `started_at` (deferred to Sub-3 with the stopwatch).
`ResultSchema` for this slice: `{ score, found_count, total_words, found_words: [{ word_id, word, clue, coordinates }] }` — no `base_score` / `time_bonus` / `time_elapsed_ms` (added in Sub-3/Sub-4).
`PuzzleState.clues[*]` shape: `{ word_id, clue, found, word | null, coordinates | null }` per the PRD.

## Acceptance criteria

- [ ] Migration creates `word_hunt_puzzles`, `word_hunt_words`, `word_hunt_finds` with the columns, FKs, and constraints described in the PRD; `(session_id, word_id)` UNIQUE on finds; `game_sessions.game_id` CHECK accepts `word_hunt` and rejects `crossword`
- [ ] `GAMES` registry contains `word_hunt` and not `crossword`; lobby exposes the "Word Hunt" tile; no string `crossword` remains in app code (historical migration files and PRD prose excluded)
- [ ] `word_hunt.json` seed loads at startup; idempotent re-runs do not duplicate; every word in the seed passes `grid.validate_seeded_word` and a deliberately broken seed (word coords don't spell the word) prevents app boot with a clear error
- [ ] `grid.py` correctly handles all 8 directions including reverse diagonals; out-of-bounds and non-linear traces rejected; uppercase normalisation applied
- [ ] `scoring.compute_base_score` returns `found_count * 100`
- [ ] `POST /games/word-hunt/play` for a new player creates a session, returns `PuzzleState` with `found_count = 0`, every `clues[*].found = false`, no `word` field on any clue
- [ ] `POST /games/word-hunt/play` on an active session with prior finds returns the same grid, marks the found clues with `found=true`, populates `word` and `coordinates` on those clues only
- [ ] `POST /games/word-hunt/find` with a correct trace returns `matched=true`, response includes the found word + its traced coordinates, `session_score` increments by 100
- [ ] `POST /games/word-hunt/find` with a wrong trace (any of: out-of-bounds, non-linear, valid-but-doesn't-spell-an-unsolved-word) returns `matched=false`, score unchanged, no `word_hunt_finds` row created
- [ ] `POST /games/word-hunt/find` against an already-found word returns `matched=false` (no duplicate row)
- [ ] `POST /games/word-hunt/find` matching the final unsolved word auto-completes the session: response carries `session_status="completed"`, `result` populated, `game_sessions.score` persisted as `found_count * 100`
- [ ] Collision case: when the same answer string appears in two grid locations, tracing either location credits the find; tracing the other after the find is a miss
- [ ] `POST /games/word-hunt/submit` on an active session marks it `completed` and persists `game_sessions.score = found_count * 100`; on an already-`completed` session raises `WordHuntSessionAlreadyCompletedException`
- [ ] No response body in any endpoint contains the `word` text for an unfound Hidden Word
- [ ] Frontend Word Hunt page no longer renders a placeholder; player can drag across cells to find words, watch found cells stay highlighted, hit Submit (or find them all) and see a basic result block
- [ ] Unit tests for `scoring.py`, `grid.py`, and `WordHuntService` happy paths pass; tests use hand-written DAO fakes (no `MagicMock`) per project convention

## Blocked by

None — can start immediately.
