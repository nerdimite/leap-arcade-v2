# Sub-1: Happy-Path Tracer Bullet

**Type:** AFK
**Status:** done
**Depends on:** nothing
**Blocks:** Sub-2, Sub-3, Sub-4

## Parent

`docs/issues/crossword/parent.md`

## What to build

A thin vertical slice that proves the entire Crossword stack lights up: a player can log in, navigate to the Crossword tile, see a real blank grid (open/blocked cells with corner numbers) and the Across/Down clue list, type letters into cells, have a correctly-completed entry register as a Crossword Solve, and reach a basic result screen when they either solve every entry or press Submit.

This slice does NOT include the polished keyboard UX (direction toggle, arrow nav, active-entry highlight, +100 chip, clue checkmark, red-flash on wrong), the time bonus, the live stopwatch, the navigation guard wiring, or the polished result breakdown — those land in Sub-2 / Sub-3 / Sub-4. The mechanic must work end-to-end, but the visual treatment is barebones (e.g. clue list rendered as plain `<ul>` with two sections; solved cells highlighted with a solid background; result screen showing only `solved_count / total_entries` and total score). The **backend miss/wrong-entry logic is fully implemented here** (it is part of `submit_check`); only the *visual* wrong-entry treatment is deferred to Sub-2.

End-to-end behaviour delivered:

1. **Foundation** — `leap/config/constants.py` `GAMES`: append `{"id": "crossword", "display_name": "Crossword"}`. Alembic migration adds `"crossword"` to the `game_sessions.game_id` CHECK constraint. Frontend route at `frontend/src/app/(games)/crossword/` (currently an empty stub) is replaced with a real game shell. `game-tiles.ts`, lobby constants, and any related stories updated to surface the "Crossword" tile.
2. **DB / migration** — the same Alembic migration (or a stacked second one) creates `crossword_puzzles`, `crossword_entries`, and `crossword_solves` per the PRD schema (`(session_id, entry_id)` UNIQUE on solves; `direction` CHECK in (`across`,`down`)). ORM models registered in `leap/dao/models/__init__.py`.
3. **Pure logic modules** —
   - `leap/games/crossword/scoring.py` with `CROSSWORD_BASE_PER_ENTRY = 100` and `compute_base_score(solved_count)`. `compute_time_bonus` / `compute_final_score` are intentionally deferred to Sub-3 (this slice's "final score" is just `solved_count * 100`).
   - `leap/games/crossword/grid.py` — full implementation, used by both the seed loader (validation) and the service (check resolution + skeleton build): `entry_cells(start_row, start_col, direction, length) -> list[(r,c)]`, `walk_entry(grid, start, direction, length) -> str`, `validate_seeded_entry(grid, answer, start, direction) -> bool`, `validate_grid_consistency(grid, entries) -> None` (raises on coverage / intersection mismatch), `build_skeleton(grid, entries) -> cells + numbering`. Unit tests for both modules pass.
4. **Seed** — `leap/seeds/data/crossword.json` with the launch puzzle: a 12×12 solution matrix (uppercase A–Z, `null` for blocked cells) and an `entries` array of the 10 entries listed in the parent (each with `number`, `direction`, `start_row`, `start_col`, `answer`, `clue`). Coordinates and the matrix are transcribed from `docs/final_game_content/crossword.png`. Seed loader is idempotent (`ON CONFLICT DO NOTHING / DO UPDATE`) and runs `grid.validate_seeded_entry` on every entry AND `grid.validate_grid_consistency` on the whole puzzle at startup, raising and preventing boot on mismatch.
5. **Backend** — DAOs: `CrosswordPuzzleDAO` and `CrosswordEntryDAO` (read-only; `get_all_with_entries` / `get_for_puzzle`; abstract methods stubbed with `raise NotImplementedError`), `CrosswordSolveDAO` (`create`, `get_for_session`, `count_for_session`). Internal types in `leap/types/crossword.py`: `CrosswordPuzzleDTO` (includes its entries), `CrosswordEntryDTO`, `CrosswordSolveDTO`, `CrosswordPuzzleStateDTO`, `CrosswordResultDTO`, `CrosswordPlayPayload`, `CrosswordCheckPayload`, `CrosswordSolvedEntryDTO`.
6. **Service** (`leap/games/crossword/service.py`) — `CrosswordService` warms a puzzle cache from the DB at startup via `initialize(session)` from app lifespan, mirroring `WordHuntService`. Three methods:
   - `play(player_id)` — idempotent: creates the `game_sessions` row (keyed `(player_id, "crossword")`) on first call, otherwise returns existing state. Returns the blank skeleton (open/blocked layout + corner numbers, **no letters**) + clues (no answer text for unsolved entries; answer + cell coordinates + letters for already-solved entries) + running score (`solved_count * 100`).
   - `submit_check(player_id, payload)` — validates that `entry_id` belongs to the session's puzzle and that `len(letters)` equals the entry's answer length; if not, returns `correct=false` (a miss — never a 4xx). Otherwise compares `letters` case-insensitively against the entry's seeded `answer`; on a match: creates a `crossword_solves` row, recomputes `session_score = solved_count * 100`, and if `solved_count == total_entries` marks the session `completed` and persists `game_sessions.score`. Re-submitting an already-solved entry is a no-op (`correct=false`, no duplicate row). Returns `correct`, the solved entry (when correct), updated session score, and the result payload when the session just completed.
   - `submit(player_id)` — finalises the session as `completed`, persists `game_sessions.score = solved_count * 100` (no time bonus in this slice), returns the `ResultSchema`. Raises `CrosswordSessionAlreadyCompletedException` if already `completed`.
7. **Errors** — `leap/config/errors.py`: add `NO_CROSSWORD_PUZZLE_AVAILABLE` (3xxx) and `CROSSWORD_SESSION_ALREADY_COMPLETED` (2xxx). Service exceptions in `leap/service/exceptions.py` subclass `BaseServiceException`.
8. **Routes** (`leap/api/routes/games/crossword.py`) — `POST /play`, `POST /check`, `POST /submit`. Schema models in `leap/api/schema/crossword.py`. The response shape for every endpoint **must never** include the `answer` text or any letter of an unsolved Crossword Entry. Mounted at prefix `/games/crossword` in `leap/api/main.py`. Wired into `ServiceContainer`.
9. **Frontend** — replace the placeholder route at `app/(games)/crossword/page.tsx` with a real game shell. Components for this slice: a `CrosswordGrid` that renders open vs blocked cells with corner numbers, lets the player click a cell and type a letter into it (advance-on-type and direction toggle deferred to Sub-2 — for this slice a minimal "click cell, type letter, cursor stays or moves right by default" is acceptable), detects when an entry's cells are all filled and fires `POST /check` for it, and highlights solved entries' cells with a solid background. A plain two-section clue list (`Across` / `Down`, unstyled). A minimal inline result block on game end (`solved_count / total_entries` + total score + "Back to Lobby"). Typed API client wrappers in `frontend/src/lib/api/crossword.ts`. React Query hooks for `play`, `check`, `submit`. A visible Submit button that calls `/submit`. Auto-complete: when a `/check` response carries `session_status="completed"`, transition to the result block.

API contracts for this slice (subset of the final PRD contract; `time_bonus` / `base_score` / `started_at` fields absent until Sub-3):

```
POST /games/crossword/play
  → 200 PlayResponse { session_status, session_score, puzzle: PuzzleState | null, result: ResultSchema | null }

POST /games/crossword/check
  body: { entry_id: UUID, letters: str }
  → 200 CheckResponse { correct: bool, entry: SolvedEntry | null, session_status, session_score, result: ResultSchema | null }

POST /games/crossword/submit
  → 200 SubmitResponse { result: ResultSchema }
```

`PuzzleState` for this slice: `{ puzzle_id, rows, cols, cells, clues, solved_count, total_entries }` — no `started_at` (deferred to Sub-3).
`cells`: `rows × cols`, each entry `null` (blocked) or `{ row, col, number | null, letter | null }` where `letter` is populated **only** for cells belonging to a solved entry.
`clues[*]`: `{ entry_id, number, direction, clue, length, start_row, start_col, solved, answer | null, cells | null }` — `answer` / `cells` populated iff `solved == true`.
`ResultSchema` for this slice: `{ score, solved_count, total_entries, solved_entries: [{ entry_id, number, direction, clue, answer, cells }] }` — no `base_score` / `time_bonus` / `time_elapsed_ms` (added in Sub-3).

## Technical nuances (must get right)

- **No-letter-leak skeleton.** The initial `PuzzleState` carries ZERO letters. The only letters that ever appear in any response are those of entries the player has already solved. `validate` this in tests by string-searching the `play` payload for any unsolved answer text → 0 hits.
- **Intersection validation at startup.** `validate_grid_consistency` must reject: (a) any entry whose cells don't spell its answer, (b) any entry cell that is `null` in the matrix, (c) any non-`null` matrix cell not covered by at least one entry, (d) a shared cell whose Across and Down answers disagree on the letter. App must refuse to boot on any of these.
- **Shared-cell numbering.** Two entries that start at the same cell share a `number` (e.g. 1-Across MICROSERVICE and 1-Down MOCK). `build_skeleton` derives the corner number from the entries; a cell can be the start of both an Across and a Down entry but shows a single number.
- **`check` is letter-length-gated and entry-scoped.** A wrong `entry_id` (not in this puzzle) or a `letters` length ≠ the entry length returns `correct=false` — a graceful miss, never a 4xx, never leaking which part was wrong.
- **Duplicate-solve guard.** `(session_id, entry_id)` UNIQUE plus a service-level check; re-checking a solved entry is a silent no-op.
- **Case-insensitivity.** Answers are stored uppercase; comparison normalises both sides. The matrix is the source of truth; `entries[*].answer` must agree with it (enforced by validation).
- **Auto-complete is server-detected** inside `submit_check` when `solved_count == total_entries`; the same `/check` response carries the `result`.
- **Session key** is `(player_id, "crossword")` — one session per player per game, identical to every other game.

## Acceptance criteria

- [ ] Migration creates `crossword_puzzles`, `crossword_entries`, `crossword_solves` with the columns, FKs, and constraints described in the PRD; `(session_id, entry_id)` UNIQUE on solves; `direction` CHECK in (`across`,`down`); `game_sessions.game_id` CHECK accepts `crossword`
- [ ] `GAMES` registry contains `crossword`; lobby exposes the "Crossword" tile; the placeholder route no longer renders
- [ ] `crossword.json` seed loads at startup; idempotent re-runs do not duplicate; every entry passes `grid.validate_seeded_entry` and the puzzle passes `grid.validate_grid_consistency`; a deliberately broken seed (entry coords don't spell the answer, an inconsistent intersection, or an uncovered cell) prevents app boot with a clear error
- [ ] `grid.py` correctly builds entry cells, walks across/down entries, and produces a skeleton with correct open/blocked layout and corner numbering carrying no letters
- [ ] `scoring.compute_base_score` returns `solved_count * 100`
- [ ] `POST /games/crossword/play` for a new player creates a session, returns `PuzzleState` with `solved_count = 0`, every `clues[*].solved = false`, no `answer`/`cells` on any clue, and zero letters in `cells`
- [ ] `POST /games/crossword/play` on an active session with prior solves returns the same skeleton, marks solved clues `solved=true` with `answer` + `cells`, and populates `letter` on exactly those solved cells
- [ ] `POST /games/crossword/check` with correct letters for an unsolved entry returns `correct=true`, the solved entry + its cells, `session_score` increments by 100, a `crossword_solves` row exists
- [ ] `POST /games/crossword/check` with wrong letters, a wrong-length `letters`, or an `entry_id` not in the puzzle returns `correct=false`, score unchanged, no row created
- [ ] `POST /games/crossword/check` against an already-solved entry returns `correct=false` (no duplicate row)
- [ ] A single fill that completes both the Across and the Down entry through a shared cell credits both via two independent `/check` calls
- [ ] `POST /games/crossword/check` solving the final entry auto-completes: response carries `session_status="completed"`, `result` populated, `game_sessions.score` persisted as `solved_count * 100`
- [ ] `POST /games/crossword/submit` on an active session marks it `completed` and persists `game_sessions.score = solved_count * 100`; on an already-`completed` session raises `CrosswordSessionAlreadyCompletedException`
- [ ] No response body in any endpoint contains the `answer` text or any letter of an unsolved Crossword Entry
- [ ] Frontend Crossword page no longer renders a placeholder; player can type into cells, watch a completed correct entry stay highlighted, hit Submit (or solve them all) and see a basic result block
- [ ] Unit tests for `scoring.py`, `grid.py`, and `CrosswordService` happy + miss paths pass; tests use hand-written DAO fakes (no `MagicMock`) per project convention

## Blocked by

None — can start immediately.
