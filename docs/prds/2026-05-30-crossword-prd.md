# Crossword — Full Implementation PRD

---

## Problem Statement

The LEAP platform's game roster now has six implemented mini-games (`wiki`, `rapid_fire`, `pinpoint`, `picture`, `four_pics`, `word_hunt`). The original `crossword` lobby identifier was repurposed: Word Hunt took over that slot and renamed itself, leaving `crossword` free and the frontend route `(games)/crossword/` an empty stub. There is now a genuine, separate crossword puzzle to ship — a classic intersecting-word grid with numbered Across/Down clues (see `docs/final_game_content/crossword.png` and `crossword.md`) — but no backend module, DB schema, seed data, or interactive frontend exists for it. Players who reach this tile encounter a placeholder page and cannot play.

---

## Solution

Implement **Crossword** end-to-end as the seventh game (`game_id: crossword`, player-facing name "Crossword"): a server-authoritative classic crossword. The player sees a blank grid of open and blocked cells with corner numbers, alongside a two-section clue panel (Across / Down). The grid starts **completely empty** — no letters are pre-revealed. The player clicks a cell and types letters from the keyboard; each open cell belongs to one Across and/or one Down **Crossword Entry**. The moment all cells of an entry are filled, the client auto-checks that entry against the server. A correct entry locks green and scores; a wrong entry flashes red, keeps the player's typed letters, and stays editable. Scoring is a flat base per solved entry plus a single session-wide time bonus that decays from session start. The game ends when every entry is solved, when the player presses **Submit**, or when the navigation guard fires — all three terminal paths are scored identically. There is no abandon and no resume of in-progress (unsolved) letters; only solved entries survive a refresh. The solution never leaves the server: the client only ever receives letters for entries the player has already solved.

This mirrors **Word Hunt** in nearly every structural respect (server-authoritative grid, seed JSON with a solution matrix validated at startup, flat per-word base score + one decaying session time bonus, three identically-scored terminal paths, no abandon status, solved-only refresh resume, pure `grid.py`/`scoring.py` modules, fake-DAO service tests). The divergence is the interaction model — keyboard cell-entry instead of drag — and the cell-sharing intersection logic unique to crosswords.

---

## User Stories

1. As a player, I want to start a Crossword session from the Lobby tile, so that my game session is created and the blank grid plus clue panel are shown immediately.
2. As a player, I want to see the full grid on the left and all clues listed in an Across/Down panel on the right, so that I always have the complete puzzle in view.
3. As a player, I want every open cell rendered as an empty box with the entry-start number in its corner, so that I can map clue numbers to grid positions exactly like a printed crossword.
4. As a player, I want blocked cells rendered distinctly (solid/dark) and non-interactive, so that the shape of the grid is unambiguous.
5. As a player, I want all Across and Down clues visible at once in two labelled sections, so that I can tackle them in any order.
6. As a player, I want to click a cell to select it and start typing, so that filling in letters feels like a normal crossword.
7. As a player, I want typing a letter to fill the selected cell and auto-advance the cursor along the active direction, so that I can enter a word fluently.
8. As a player, I want to toggle the active direction (across ↔ down) by clicking the already-selected cell (or pressing Tab/Space), so that I can switch between the two entries that share a cell.
9. As a player, I want arrow keys to move the cursor around the grid, so that navigation is quick.
10. As a player, I want Backspace to clear the current cell (or retreat and clear the previous one) along the active direction, so that fixing mistakes is natural.
11. As a player, I want clicking a clue in the panel to jump the cursor to that entry's first open cell and set the active direction, so that I can navigate from clue to grid.
12. As a player, I want selecting a cell to highlight its active entry in the grid and highlight the matching clue in the panel, so that I always know which word I am filling.
13. As a player, I want my entry to be auto-checked the instant all its cells are filled, so that I get immediate feedback without pressing a button.
14. As a player, I want a correctly-completed entry to lock with a persistent highlight (green) and become read-only, so that I can see at a glance which words are solved.
15. As a player, I want a correctly-completed entry to flip/mark its corresponding clue as solved with a checkmark, so that the win is visible in both the grid and the clue panel.
16. As a player, I want a wrong completed entry to flash red briefly while keeping the letters I typed, so that I can find and fix the single wrong cell rather than re-entering the whole word.
17. As a player, I want letters that are locked-correct from an already-solved crossing entry to be untouched when a crossing entry checks wrong, so that solving never destroys confirmed progress.
18. As a player, I want a wrong entry to re-check automatically once I edit a cell and the entry is full again, so that I do not need to re-trigger validation manually.
19. As a player, I want the grid to start completely blank with no pre-revealed letters, so that the puzzle is a genuine challenge.
20. As a player, I want the clue panel to never reveal the answer of an unsolved entry, so that the clues remain meaningful and unsolved answers cannot be inspected via the network.
21. As a player, I want my game stopwatch to be visible during play, so that I can feel the time-bonus pressure.
22. As a player, I want to keep playing for the base score even after my time bonus has fully decayed, so that taking my time on a hard puzzle still earns meaningful points.
23. As a player, I want a "Submit" button visible throughout play, so that I can voluntarily end the session at any time and bank the score I have plus whatever time bonus remains.
24. As a player, I want the game to auto-complete the moment I solve the last entry, so that I am not forced to also tap Submit when the puzzle is fully solved.
25. As a player who navigates away mid-game, I want the navigation guard to intercept and submit my session automatically (same effect as the Submit button), so that I do not silently lose the score for the entries I already solved.
26. As a player, I want the result screen to show my total score broken into per-entry base score and the time bonus, so that I understand exactly how the number was built.
27. As a player, I want the result screen to show each solved entry with its clue and answer, so that I can savour the words I solved.
28. As a player, I want the result screen to **not** reveal entries I did not solve, so that I cannot leak unsolved answers to players still in the game.
29. As a player, I want a "Back to Lobby" button on the result screen, so that I can return and check the leaderboard.
30. As a player, I want my Crossword session to be locked once it ends (via solving everything, Submit, or navigation guard), so that I cannot replay the game and inflate my score.
31. As a player, I want the Lobby tile for Crossword to reflect my session status (not started / in progress / completed), so that I see my progress at a glance.
32. As a player who refreshes the page mid-session, I want to be returned to the same grid with my already-solved entries filled in and locked green, so that a refresh does not destroy confirmed progress (in-progress tentative letters are not restored).
33. As an event organiser, I want the puzzle (solution grid + entries + clues + coordinates) to be defined in a hand-written seed JSON file using a literal 2-D letter matrix, so that the content team can read and edit it without tooling.
34. As an event organiser, I want grid dimensions (`rows`, `cols`) and the blocked-cell layout to come from the seed rather than constants, so that we can ship grids of any size without code changes.
35. As an event organiser, I want each entry's coordinates and answer to be validated against the grid at startup (the cells from the start in the declared direction must spell the answer), so that bad seed data is caught before the event begins.
36. As an event organiser, I want every shared (intersection) cell validated at startup to ensure the crossing Across and Down answers agree on that letter, so that an inconsistent puzzle cannot ship.
37. As an event organiser, I want the time-bonus decay parameters and per-entry base score to live as code constants, so that they are reviewable but not casually editable by the content team.
38. As an event organiser, I want the API to never include the answer text or unsolved letters of an unsolved entry in any response, so that a determined player cannot inspect network traffic to bypass the puzzle.

---

## Implementation Decisions

### Naming and Game Registry

- Crossword is a **new seventh game**, reusing the now-free `crossword` identifier that Word Hunt vacated. No production data depends on it.
- Update `GAMES` in `leap/config/constants.py`: append `{"id": "crossword", "display_name": "Crossword"}`.
- New Alembic migration: add `"crossword"` to the `game_sessions.game_id` CHECK constraint.
- Replace the placeholder frontend route at `(games)/crossword/` with the real implementation. Update `game-tiles.ts`, lobby constants, and stories.

### Check Model (Auto-Check on Entry Completion)

- The player fills letters by typing. As soon as **all cells of an entry are filled**, the client fires `POST /games/crossword/check` for that entry. When filling a single shared cell completes both its Across and its Down entry at once, the client fires one check per just-completed entry (at most two).
- The server compares the submitted letters against the entry's seeded answer (case-insensitive). A match records a **Crossword Solve** and scores it; a mismatch is a no-op (no row written, no score).
- Auto-check leaks correctness (a 3-letter entry like `DNS` is in principle brute-forceable via repeated checks). This is an **accepted, documented risk**: crossing letters from solved entries shrink the search space, the event is a friendly timed tournament, and there is no rate-limiting. See Out of Scope.

### Scoring Model

- **Per-entry base score:** `CROSSWORD_BASE_PER_ENTRY = 100` pts for every entry solved at session end (flat, regardless of word length).
- **Session time bonus** (applied once at end, regardless of which terminal path):

  ```
  time_bonus = max(0, floor(CROSSWORD_TIME_BONUS_MAX * (1 - elapsed_ms / CROSSWORD_TIME_DECAY_MS)))
  ```

  with `CROSSWORD_TIME_BONUS_MAX = 500` and `CROSSWORD_TIME_DECAY_MS = 600_000` (10 minutes). `elapsed_ms` is computed server-side from `game_sessions.started_at` to the moment the session terminates.
- **Final session score** = `solved_count * 100 + time_bonus`. Stored in `game_sessions.score` when the session ends.
- **Max possible:** `N * 100 + 500` where `N` is the number of seeded entries (10 in the launch puzzle → max **1500**).
- **No negative marking.** A wrong completed entry costs nothing — it flashes red, keeps its letters, and stays editable. The time bonus floors at zero, never negative.
- **No hard timeout.** The session stays `active` indefinitely; the time bonus decays to zero after 10 minutes.

### Puzzle Mechanic

- One seeded puzzle for the whole event. Every player sees the same grid and the same clues.
- Grid dimensions and blocked-cell layout come entirely from the seed. No hard-coded grid size.
- The seed stores the **full solution** as a 2-D matrix of uppercase letters with `null` for blocked cells. This matrix is the server-side source of truth.
- Each **Crossword Entry** is declared with `number`, `direction` (`across` | `down`), `start_row`, `start_col`, `answer`, and `clue`. The entry's occupied cells are the `len(answer)` cells starting at `(start_row, start_col)` walking right (across) or down (down).
- Open cells are shared between a crossing Across and Down entry. A shared cell's letter must be consistent in both answers.
- The grid starts **fully blank**. The only letters ever sent to the client are those of entries the player has already solved (in the solved entry's payload and on refresh re-hydration). Unsolved cells' letters never leave the server.
- Duplicate-solve protection: each entry can be solved at most once. Re-submitting an already-solved entry is a no-op.

### Session Lifecycle and Terminal Paths

- One `game_sessions` row per `(player_id, "crossword")`, identical to every other game.
- Mid-session refresh / re-entry from the lobby tile while session is `active`: `play` returns the blank skeleton plus the list of already-solved entries (each with answer letters + coordinates) and the running score. In-progress letters of unsolved entries are **not** persisted and return blank.
- Three terminal paths, all scored identically (`solved_count * 100 + time_bonus`):
  - **Auto-complete:** triggered server-side inside the `check` handler when the solve that just occurred makes `solved_count == total_entries`. The same response that confirms the solve also carries the result payload.
  - **Submit:** explicit `POST /games/crossword/submit`. Finalises score, marks session `completed`.
  - **Navigation guard:** the frontend's existing navigation guard fires `POST /games/crossword/submit` (the same endpoint), so leaving the page is functionally a deliberate submit. There is no separate `abandon` endpoint and no `abandoned` status for Crossword sessions.
- After termination the session is `completed` (never `abandoned`). The Lobby tile is locked and re-entry returns the result screen, not the puzzle.

### DB Schema

Three new tables (mirroring Word Hunt's puzzle / word / find triad).

**`crossword_puzzles`** (seed data; expected to be a single row in practice, schema does not enforce that)

- `id` UUID PK
- `rows` SMALLINT NOT NULL
- `cols` SMALLINT NOT NULL
- `grid` JSONB NOT NULL — 2-D array, dimensions `rows × cols`; each cell is a single uppercase letter or `null` for a blocked cell
- `created_at` TIMESTAMPTZ NOT NULL

**`crossword_entries`** (seed data; one row per Across/Down entry per puzzle)

- `id` UUID PK
- `puzzle_id` UUID FK → `crossword_puzzles.id`
- `number` SMALLINT NOT NULL — the printed clue number (shared between an Across and a Down entry that start at the same cell)
- `direction` TEXT NOT NULL CHECK in (`across`, `down`)
- `start_row` SMALLINT NOT NULL
- `start_col` SMALLINT NOT NULL
- `answer` TEXT NOT NULL — canonical uppercase answer; server-side comparison is case-insensitive
- `clue` TEXT NOT NULL — the clue shown in the panel

**`crossword_solves`** (one row per entry solved by a player)

- `id` UUID PK
- `session_id` TEXT FK → `game_sessions.id`
- `entry_id` UUID FK → `crossword_entries.id`
- `solved_at` TIMESTAMPTZ NOT NULL
- UNIQUE `(session_id, entry_id)`

Final session score is stored on `game_sessions.score`, consistent with all other games. No score is denormalised onto `crossword_solves`.

### Seed Data Format

`backend/leap/seeds/data/crossword.json` — single object, hand-edited matrix plus entries:

```json
{
  "puzzle": {
    "rows": 12,
    "cols": 12,
    "grid": [
      ["M","I","C","R","O","S","E","R","V","I","C","E"],
      ["O",null,null,null,null,null,null,null,"V",null,null,null]
    ]
  },
  "entries": [
    {
      "number": 1,
      "direction": "across",
      "start_row": 0,
      "start_col": 0,
      "answer": "MICROSERVICE",
      "clue": "Small, independently deployable unit in modern cloud architecture (12)"
    },
    {
      "number": 1,
      "direction": "down",
      "start_row": 0,
      "start_col": 0,
      "answer": "MOCK",
      "clue": "Simulated object used in testing to replace a real dependency (4)"
    }
  ]
}
```

Launch content (from `docs/final_game_content/crossword.md`): Across — MICROSERVICE(12), KUBERNETES(10), ATOMICITY(10), PIPELINE(8); Down — MOCK(4), EVENTDRIVEN(11), DNS(3), GITOPS(6), CACHING(7), DRIFT(5).

Seed loader behaviour:
- Loader is idempotent (`ON CONFLICT DO NOTHING` / `DO UPDATE`) per platform contract.
- On every startup, the loader **validates** each entry: walks the grid cells from `(start_row, start_col)` in the declared direction for `len(answer)` cells and asserts the resulting string (case-insensitive) equals `answer`.
- The loader also validates **intersection consistency**: every open (non-`null`) cell covered by both an Across and a Down entry must carry the same letter in both answers (guaranteed transitively if every entry matches the shared matrix, so validating each entry against the matrix is sufficient; the loader additionally asserts every non-`null` matrix cell is covered by at least one entry and every entry cell is non-`null`).
- Validation failures raise at startup and prevent the app from booting.

### API Contract

```
POST /games/crossword/play
  → 200 PlayResponse {
      session_status: "active" | "completed",
      session_score: int,                # 0 while active, final on completed
      puzzle: PuzzleState | null,        # null when session is completed
      result: ResultSchema | null        # populated when session is completed
    }

POST /games/crossword/check
  body: { entry_id: UUID, letters: str }
  → 200 CheckResponse {
      correct: bool,
      entry: SolvedEntry | null,         # populated only on correct=true
      session_status: "active" | "completed",
      session_score: int,
      result: ResultSchema | null        # populated only when this solve auto-completed the session
    }

POST /games/crossword/submit
  → 200 SubmitResponse { result: ResultSchema }
```

`PuzzleState`:

```
{
  puzzle_id: UUID,
  rows: int,
  cols: int,
  cells: List[List[CellSkeleton | null]],   # null = blocked; CellSkeleton = open cell
  clues: List[{
    entry_id: UUID,
    number: int,
    direction: "across" | "down",
    clue: str,
    length: int,
    start_row: int, start_col: int,
    solved: bool,
    answer: str | null,                      # populated iff solved == true
    cells: [{ row, col }] | null             # populated iff solved == true
  }],
  solved_count: int,
  total_entries: int,
  started_at: ISO8601                        # server-authoritative for client stopwatch
}
```

`CellSkeleton` (open cells only; never carries a letter unless that cell belongs to a solved entry):

```
{
  row: int,
  col: int,
  number: int | null,                        # the corner label iff an entry starts here
  letter: str | null                         # populated iff this cell belongs to a solved entry
}
```

`SolvedEntry`:

```
{
  entry_id: UUID,
  number: int,
  direction: "across" | "down",
  clue: str,
  answer: str,
  cells: [{ row, col }]
}
```

`ResultSchema`:

```
{
  score: int,                                # session total
  base_score: int,                           # solved_count * 100
  time_bonus: int,
  solved_count: int,
  total_entries: int,
  time_elapsed_ms: int,
  solved_entries: List[{
    entry_id: UUID,
    number: int,
    direction: "across" | "down",
    clue: str,
    answer: str,
    cells: [{ row, col }]
  }]
  # Unsolved entries are deliberately omitted; their answer text never leaves the server.
}
```

`PlayResponse` is **idempotent**: repeated calls with no intervening solve return the same `PuzzleState` snapshot. The skeleton never changes; only `clues[*].solved`, the solved cells' `letter`, and `solved_count` advance.

### Validation and Server-Authoritative Anti-Cheat

- `check` validates that `entry_id` belongs to the session's puzzle and that `letters` length equals the entry's answer length; otherwise `correct=false` (treated as a miss, not a 4xx).
- The letters comparison is case-insensitive against the seeded `answer`.
- The answer text and unsolved letters of any unsolved entry are never emitted in any response. The initial `PuzzleState` carries no letters at all.
- Short-word auto-check brute-force is an accepted risk (see Out of Scope) — no rate-limiting in the launch version.

### Module Breakdown

- **`leap/games/crossword/scoring.py`** — pure functions: `compute_base_score(solved_count)`, `compute_time_bonus(elapsed_ms)`, `compute_final_score(solved_count, elapsed_ms)`. No I/O — deepest testable unit. Mirrors `word_hunt/scoring.py`.
- **`leap/games/crossword/grid.py`** — pure functions: `entry_cells(start_row, start_col, direction, length) -> List[(r,c)]`, `walk_entry(grid, start, direction, length) -> str`, `validate_seeded_entry(grid, answer, start, direction) -> bool`, `validate_grid_consistency(grid, entries) -> None` (raises on coverage/intersection mismatch), `build_skeleton(grid, entries) -> cells+numbering`. Used by both the seed loader (validation) and the service (check resolution + skeleton build). Pure — no DB, no DTOs.
- **`leap/games/crossword/service.py`** — `CrosswordService` owns session lifecycle: `play`, `submit_check`, `submit`. Warms a puzzle cache from DB at startup (mirrors `WordHuntService`). Owns the DB session via `async with self.ctx.session() as session`. Responsibilities: session create/resume, check resolution via `grid.walk_entry`, duplicate-solve rejection, auto-complete detection, score computation, terminal-state transitions, result construction, skeleton build with solved-cell letters hydrated.
- **`leap/dao/crossword_puzzle_dao.py`** — read-only; `get_all_with_entries` for cache warm at startup. Stubs `_to_orm` / `_apply_filters` with `raise NotImplementedError` per AGENTS.md rule.
- **`leap/dao/crossword_entry_dao.py`** — read-only; `get_for_puzzle`. Stubs `_to_orm` / `_apply_filters`.
- **`leap/dao/crossword_solve_dao.py`** — `create`, `get_for_session`, `count_for_session`.
- **ORM models** — `CrosswordPuzzleModel`, `CrosswordEntryModel`, `CrosswordSolveModel` in `leap/dao/models/`, registered in `leap/dao/models/__init__.py`.
- **Types** (`leap/types/crossword.py`) — `CrosswordPuzzleDTO` (includes its entries), `CrosswordEntryDTO`, `CrosswordSolveDTO`, `CrosswordPuzzleStateDTO`, `CrosswordResultDTO`, `CrosswordPlayPayload`, `CrosswordCheckPayload`, `CrosswordSolvedEntryDTO`. All subclass `BaseLeapModel`.
- **API schema** (`leap/api/schema/crossword.py`) — request/response Pydantic models per the API Contract above.
- **API routes** (`leap/api/routes/games/crossword.py`) — three handlers; each delegates to `CrosswordService` and maps DTOs to API schemas. Mounted at prefix `/games/crossword` in `leap/api/main.py`.
- **ServiceContainer** — wires `CrosswordService` alongside other game services; `initialize(session)` called at startup to warm the puzzle cache.
- **Seed data** (`leap/seeds/data/crossword.json`) — single object as described above. Seed loader validates every entry and grid consistency before inserting.
- **Alembic migration** — adds three new tables and adds `"crossword"` to the `game_sessions.game_id` CHECK constraint.
- **Errors** (`leap/config/errors.py`) — additions: `NO_CROSSWORD_PUZZLE_AVAILABLE` (3xxx range), `CROSSWORD_SESSION_ALREADY_COMPLETED` (2xxx range). Service exceptions in `leap/service/exceptions.py` subclass `BaseServiceException` and map to these.
- **Frontend** — replaces the placeholder route at `app/(games)/crossword/`. Components: `CrosswordGame` shell, `CrosswordGrid` (keyboard-driven cell entry with cursor, direction toggle, arrow nav, auto-check on entry completion, locked/green solved cells, red-flash on wrong), `ClueListPanel` (Across/Down sections, active-clue highlight, solved checkmark), `Stopwatch`, `SubmitButton`, `ResultView`. Typed API client wrappers in `lib/api/crossword.ts`. React Query hooks for `play`, `check`, `submit`. Wired into the existing navigation guard with `submit` as the guard handler.

### Constants

In `leap/games/crossword/scoring.py` (or a dedicated `constants.py`):

- `CROSSWORD_BASE_PER_ENTRY = 100`
- `CROSSWORD_TIME_BONUS_MAX = 500`
- `CROSSWORD_TIME_DECAY_MS = 600_000`

### Frontend UX Decisions

- Two-pane layout: grid on the left, clue panel (Across section then Down section) on the right. On narrow viewports the panel stacks below the grid (or collapses to a current-clue bar with prev/next — content-team/UX discretion).
- Grid cells are square and evenly sized to fit the viewport. Blocked cells render solid/dark and are non-interactive. Open cells render as empty boxes with a small corner number where an entry starts.
- **Selection & typing:** click a cell to select; typing a letter fills it and advances the cursor along the active direction. Clicking the already-selected cell — or pressing Tab/Space — toggles the active direction (across ↔ down) when the cell belongs to both. Arrow keys move the cursor; Backspace clears the current cell or retreats and clears the previous one along the active direction.
- **Active-entry highlight:** selecting a cell highlights its active entry's cells in the grid and highlights the matching clue in the panel. Clicking a clue jumps the cursor to that entry's first open cell and sets the direction.
- **Auto-check:** when an entry's cells are all filled, the client fires `POST /check` for it (one call per just-completed entry).
- **Hit feedback:** the solved entry's cells lock into a persistent green highlight and become read-only; the clue is marked solved with `✓`; a "+100" score increment animates near the stopwatch.
- **Miss feedback:** the entry's cells flash red briefly (~250 ms); the typed letters are **kept** (locked crossing letters untouched) so the player can fix the wrong cell; the entry re-checks automatically once it is full again after an edit.
- Stopwatch is rendered client-side from `started_at` returned by `play`, but the score and time bonus are always computed server-side from the server's `started_at`.
- Submit button visible throughout play. Pressing it calls `POST /submit` and transitions to the result screen.
- Result screen mirrors the platform pattern: total score with `base + time_bonus` breakdown, `solved_count / total_entries`, time elapsed, and a list of solved entries (clue + answer). Unsolved entries are not displayed. "Back to Lobby" button.
- Navigation guard calls `POST /submit` on confirmed exit (back button, route change, tab close attempt), then disarms and lets the navigation proceed.
- **Mobile:** tapping a cell focuses a hidden text input to summon the native keyboard; the rest of the typing/selection model is unchanged.

---

## Testing Decisions

Good tests for this game test **external behaviour** — what the service returns given specific sequences of calls — not internal helpers like cache structure or query construction. Tests use hand-written DAO fakes (not `MagicMock`) per project convention. DAO tests that require real SQL execution are integration tests — mark with a TODO comment per AGENTS.md. The injectable-clock pattern used for Word Hunt / Wiki / Pinpoint time-bonus tests is reused so time-bonus assertions are deterministic.

### Modules to test

**`scoring.py` — unit tests (highest priority)**

- `compute_base_score`: `0 → 0`, `1 → 100`, `10 → 1000`.
- `compute_time_bonus`: `0ms → 500`, `300_000ms → 250`, `600_000ms → 0`, `900_000ms → 0` (clamped), boundary at exactly `600_000` is 0.
- `compute_final_score`: composition correctness across representative `(solved_count, elapsed_ms)` pairs.

**`grid.py` — unit tests (highest priority)**

- `entry_cells`: across and down entries produce the expected coordinate lists for the given length.
- `walk_entry`: builds the expected string for an across entry and a down entry; uppercase-normalises.
- `validate_seeded_entry`: accepts a correctly-placed seed entry; rejects when the traced cells do not spell `answer`; rejects when an entry runs off the grid or onto a `null` cell.
- `validate_grid_consistency`: accepts a consistent grid; rejects when a shared intersection cell disagrees between its Across and Down answers; rejects when a non-`null` matrix cell is not covered by any entry; rejects when an entry cell is `null`.
- `build_skeleton`: produces correct open/blocked layout and corner numbering; carries no letters for unsolved cells.

**`CrosswordService` — service-level acceptance tests with hand-written DAO fakes**

- `play` with no existing session → creates session, returns `PuzzleState` with `solved_count=0`, all clues `solved=false`, no answers/letters leaked.
- `play` while session is `active` with prior solves → returns the same skeleton; solved clues show `answer` + `cells` and their cells carry letters; unsolved clues/cells do not.
- `submit_check` with correct letters for an unsolved entry → records solve, returns `correct=true` with the solved entry + cells, `session_score` increments by 100.
- `submit_check` that solves the final unsolved entry → auto-completes session, response includes `result`, `session_status="completed"`, score includes the time bonus.
- `submit_check` against an entry already solved → `correct=false` (or no-op), score unchanged, no duplicate row.
- `submit_check` with wrong letters → `correct=false`, score unchanged, no row.
- `submit_check` with a `letters` length not equal to the entry length → `correct=false` (treated as a miss, not raised).
- `submit_check` with an `entry_id` not belonging to the puzzle → `correct=false` (no info leak).
- `submit_check` on a shared cell completing both crossing entries → two checks, both credited independently.
- `submit` while `active` with partial solves → session `completed`, score = `solved_count * 100 + time_bonus`, result lists only solved entries.
- `submit` immediately at start with zero solves → session `completed`, score = `time_bonus` only (near `CROSSWORD_TIME_BONUS_MAX` at `elapsed_ms ≈ 0`).
- `submit` on an already-completed session → `CrosswordSessionAlreadyCompletedException`.
- `play` on a `completed` session → returns `puzzle=null`, `result` populated with the original final state.
- Time bonus integration: a session that completes at simulated `elapsed_ms = 300_000` returns `time_bonus = floor(500 * (1 - 300/600)) = 250`, using the injectable clock.

**Seed loader — unit test**

- Loading a seed whose entries match the matrix and whose intersections agree succeeds.
- Loading a seed where an entry does not match the traced cells raises at startup before any DB writes for that puzzle.
- Loading a seed with an inconsistent intersection (or an uncovered non-`null` cell) raises at startup.
- Loading the same seed twice is idempotent (no duplicate rows; updates apply).

**Prior art:** `backend/tests/unit/services/test_word_hunt_service.py`, `test_pinpoint_service.py` (same fake-DAO style, same session-lifecycle assertions). Route-layer tests follow `backend/tests/unit/api/word_hunt/` (auth, play, check, submit split files).

### E2E tests

Add a Crossword journey to `backend/tests/e2e/`:

- **`test_crossword_journey.py`** — full playthrough: login → start → solve every entry → assert session `completed`, final score equals `N * 100 + time_bonus`, lobby tile flips to `completed`, leaderboard reflects the score.
- **`test_crossword_lifecycle_journeys.py`** —
  - Partial-solve then explicit Submit → session `completed`, score equals `solved_count * 100 + time_bonus`, result lists only solved entries and never the unsolved answer text.
  - Mid-game refresh → second `play` returns the same skeleton, the already-solved entries marked `solved=true` with their cells/letters/answer, unsolved entries still blank/hidden.
  - Navigation-guard submit (POST `/submit` directly with partial solves) → same outcome as the explicit Submit path.
  - Cheating attempts: `check` with a wrong `entry_id`, a wrong-length `letters`, and wrong letters → all return `correct=false` and never appear in `crossword_solves`.

### Frontend tests

- Reducer / hook tests for the Crossword client state machine: cursor placement, type-and-advance, direction toggle on shared cells, arrow-key navigation, Backspace clear/retreat, entry-completion detection (which fires a check), hit (lock green) vs miss (red flash, keep letters) handling, submit transition.
- Active-entry highlight logic: selecting a cell resolves the correct active entry and matching clue; clicking a clue jumps to its first open cell.
- API client wrapper tests (`lib/api/crossword.test.ts`) following the Word Hunt pattern.
- Navigation guard integration: confirmed exit triggers `POST /submit` and transitions through the result screen before completing the navigation.

---

## Out of Scope

- Pre-revealed / "given" starter letters — the grid starts fully blank (this was explicitly decided against).
- Persisting in-progress (unsolved) tentative letters across a refresh — only solved entries survive.
- An "abandon" endpoint or `abandoned` status (the navigation guard submits instead).
- Rate-limiting or other mitigation of short-word auto-check brute-forcing — accepted as a negligible risk for a friendly timed event.
- Length-weighted scoring — base score is a flat 100 per solved entry.
- A "reveal letter" / "check letter" / hint system of any kind.
- Negative scoring for wrong completed entries.
- A hard session timeout — the stopwatch runs indefinitely.
- Revealing unsolved entries' answers on the result screen or at any point post-game.
- Multiple sequential grids / rounds per session — Crossword is a single grid, single session.
- Per-entry time tracking or per-entry time bonuses — time bonus is computed once, session-wide.
- Admin tooling for live puzzle editing during the event; puzzles are seeded once at startup.
- Multi-puzzle support in a single event — the schema permits more than one `crossword_puzzles` row, but the loader and service assume a single active puzzle.
- Any logic for Wikipedia Speed Run, Picture Illustration, Four Pics One Lie, Pinpoint, Rapid Fire, or Word Hunt.

---

## Further Notes

- The `crossword` game id must be added to `leap/config/constants.py` `GAMES` and to the `game_sessions.game_id` CHECK constraint via a new Alembic migration **before** any code paths reference it.
- The literal letter matrix in the seed must be uppercase A–Z (or `null`) only; the loader is strict about non-letter, non-`null` cells and will fail validation if any are present.
- Two entries that start at the same cell share a `number` (e.g. 1-Across MICROSERVICE and 1-Down MOCK) — this is normal crossword numbering and the schema allows it.
- The launch puzzle is a 12×12 grid with 10 entries, sourced from `docs/final_game_content/crossword.png` / `crossword.md`.
- The injectable clock pattern used for Word Hunt / Wiki / Pinpoint time-bonus tests should be reused so that `compute_time_bonus` and the service-level time-bonus assertions are deterministic.
- A Meridian design YAML (`docs/design/crossword.meridian.yaml`) should be authored before implementation, walking the call graph top-down route → service → DAO → model, mirroring the existing Word Hunt design.
- `CONTEXT.md` is updated as part of this PRD with the new domain terms: **Crossword**, **Crossword Grid**, **Crossword Entry**, **Crossword Solve**, **Crossword Result**.
- Unrelated drift to fix in a separate pass: the `Lobby` and `Game Tile` glossary entries still say "five Game Tiles" — stale now that the roster is seven games.
