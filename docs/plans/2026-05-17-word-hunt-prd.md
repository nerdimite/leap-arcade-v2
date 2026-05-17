# Word Hunt — Full Implementation PRD

---

## Problem Statement

The LEAP platform reserves a fifth lobby tile under the internal identifier `crossword`, but the implementation does not exist beyond a frontend route stub, a `GAMES` registry entry, and a `game_sessions.game_id` CHECK constraint. Players who reach this tile encounter a placeholder page and cannot play. No backend routes, services, DAOs, DB tables, seed data, or interactive frontend exist for it. Additionally, the registered identifier (`crossword`) and the actual game design (a riddle-driven word search) are mismatched in product language.

---

## Solution

Rename the game to **Word Hunt** end-to-end (internal id `word_hunt`, player-facing name "Word Hunt") and implement it: a server-authoritative riddle-driven word-search puzzle. The player sees a single seeded letter grid alongside a panel of riddles. Each riddle's answer is a word hidden somewhere in the grid in any of the eight linear directions (horizontal, vertical, both diagonals, forwards or reverse). The player drags across grid cells to trace a word; the server derives the traced string from the submitted start/end coordinates, matches it against the unsolved answer pool, and credits the find. Scoring is a fixed base per word plus a single session-level time bonus that decays from session start. The game ends when every word is found, when the player presses "Submit", or when the navigation guard fires — all three terminal paths are scored identically. There is no abandon and no resume after leaving.

---

## User Stories

1. As a player, I want to start a Word Hunt session from the Lobby tile, so that my game session is created and the grid plus riddle panel are shown immediately.
2. As a player, I want to see the full letter grid on the left and all riddles listed in a panel on the right, so that I always have the complete puzzle in view.
3. As a player, I want all riddles visible at once, so that I can tackle them in any order rather than being forced into a fixed sequence.
4. As a player, I want to click-and-drag (or touch-and-drag on mobile) across grid cells to trace a candidate word, so that the interaction feels tactile and matches the word-search idiom.
5. As a player, I want my drag to be constrained to one of eight straight directions (horizontal, vertical, both diagonals), so that the act of selecting a word matches how words are hidden in the grid.
6. As a player, I want to drag in either direction along a line, so that words hidden in reverse are just as natural to find as forward words.
7. As a player, I want the server to determine which word I found from my drag coordinates, so that I cannot accidentally claim a word I did not actually trace.
8. As a player, I want a successful find to permanently highlight the traced cells in the grid, so that I can see at a glance which areas are already solved.
9. As a player, I want a successful find to flip the corresponding riddle card to reveal the answer word with a checkmark, so that the win is satisfyingly visible in both the grid and the riddle panel.
10. As a player, I want the riddle panel to never reveal an unfound word's answer, so that the riddles remain meaningful and unsolved words cannot be inspected via the network.
11. As a player, I want an unsuccessful drag (a traced string that matches no unsolved word) to briefly flash red on the selected cells before clearing, so that I get clear non-punishing feedback that the trace did not match.
12. As a player, I want the grid to stay visually neutral with no hints about word locations, so that the hunt itself remains the challenge.
13. As a player, I want my game stopwatch to be visible during play, so that I can feel the time-bonus pressure.
14. As a player, I want the same word to be findable even if multiple identical letter sequences exist elsewhere in the grid, because the server matches the traced string against the answer pool — any valid trace of an unsolved word counts.
15. As a player, I want to keep playing for the base score even after my time bonus has fully decayed, so that taking my time on a hard puzzle still earns meaningful points.
16. As a player, I want a "Submit" button visible throughout play, so that I can voluntarily end the session at any time and bank the score I have plus whatever time bonus remains.
17. As a player, I want the game to auto-complete the moment I find the last word, so that I am not forced to also tap Submit when the puzzle is solved.
18. As a player who navigates away mid-game, I want the navigation guard to intercept and submit my session automatically (same effect as the Submit button), so that I do not silently lose the score for the words I already found.
19. As a player, I want the result screen to show my total score broken down into per-word base score and the time bonus, so that I understand exactly how the number was built.
20. As a player, I want the result screen to show each found word and its clue, so that I can savour the words I solved.
21. As a player, I want the result screen to **not** reveal words I did not find, so that I cannot leak unsolved answers to players still in the game.
22. As a player, I want a "Back to Lobby" button on the result screen, so that I can return and check the leaderboard.
23. As a player, I want my Word Hunt session to be locked once it ends (via finding all words, Submit, or navigation guard), so that I cannot replay the game and inflate my score.
24. As a player, I want the Lobby tile for Word Hunt to reflect my session status (not started / in progress / completed), so that I see my progress at a glance.
25. As a player who refreshes the page mid-session, I want to be returned to the same grid with my already-found words still highlighted and their riddle cards flipped, so that a refresh is not destructive while I am still in the game.
26. As an event organiser, I want the puzzle (grid + words + clues + coordinates) to be defined in a hand-written seed JSON file using a literal 2-D letter matrix, so that the content team can read and edit it without tooling.
27. As an event organiser, I want grid dimensions (`rows`, `cols`) to come from the seed rather than constants, so that we can ship grids of any size without code changes.
28. As an event organiser, I want each seeded word's coordinates to be validated against the grid at startup (i.e. the traced cells from `start` to `end` must spell the declared word), so that bad seed data is caught before the event begins.
29. As an event organiser, I want the time-bonus decay parameters and per-word base score to live as code constants, so that they are reviewable but not casually editable by the content team.
30. As an event organiser, I want the API to never include the answer text of an unfound word in any response, so that a determined player cannot inspect network traffic to bypass the riddles.

---

## Implementation Decisions

### Naming and Game Registry

- Replace the existing `crossword` identifier across the platform with `word_hunt`. The original entry was a placeholder; no production data depends on it.
- Update `GAMES` in `leap/config/constants.py`: `{"id": "word_hunt", "display_name": "Word Hunt", ...}`.
- New Alembic migration: drop `"crossword"` from the `game_sessions.game_id` CHECK constraint and add `"word_hunt"`. The existing initial-schema migration is left intact; the change is applied as a follow-up migration.
- Update the frontend stub route from `(games)/crossword/` to `(games)/word-hunt/`. Update `game-tiles.ts`, lobby constants, and stories.

### Scoring Model

- **Per-word base score:** `WORD_HUNT_BASE_PER_WORD = 100` pts for every word the player has found at session end.
- **Session time bonus** (applied once at end, regardless of which terminal path):

  ```
  time_bonus = max(0, floor(WORD_HUNT_TIME_BONUS_MAX * (1 - elapsed_ms / WORD_HUNT_TIME_DECAY_MS)))
  ```

  with `WORD_HUNT_TIME_BONUS_MAX = 500` and `WORD_HUNT_TIME_DECAY_MS = 600_000` (10 minutes). `elapsed_ms` is computed server-side from `game_sessions.started_at` to the moment the session terminates.
- **Final session score** = `found_count * 100 + time_bonus`. Stored in `game_sessions.score` when the session ends.
- **Max possible:** `N * 100 + 500` where `N` is the number of seeded words.
- **No negative marking.** A failed drag (miss) costs nothing. The time bonus floors at zero — never negative.
- **No hard timeout.** The session stays `active` indefinitely; the time bonus just decays to zero after 10 minutes.

### Puzzle Mechanic

- One seeded puzzle for the whole event. Every player sees the same grid and the same words.
- Grid dimensions come entirely from the seed (`rows`, `cols`). No hard-coded grid size.
- Each hidden word lies along a straight line in one of the eight cardinal/diagonal directions. The seed declares `start_row`, `start_col`, `end_row`, `end_col` for each word. Direction is derived from `sign(end_row - start_row)` and `sign(end_col - start_col)`.
- A player's drag is reported to the server as a `{start_row, start_col, end_row, end_col}` quad. The server validates:
  - All four coordinates are in bounds.
  - The drag is along one of the eight allowed straight lines (i.e. the deltas are either zero or have equal magnitudes for diagonals; horizontal/vertical require one delta of zero).
  - The traced length matches an unsolved word's length.
- The server walks the cells from `start` to `end` in the derived direction, builds the traced string from `grid[r][c]`, and compares case-insensitively to the answer text of each unsolved word. The first match credits the find. If no unsolved word matches, the response is a miss.
- The same answer string may appear in more than one location in the grid (incidental collision); any valid trace of that string while the word is unsolved counts. After it is solved, subsequent traces of the same string are misses.
- Duplicate-found protection: each word can be found at most once. Re-tracing an already-found word's cells returns a miss.

### Session Lifecycle and Terminal Paths

- One `game_sessions` row per `(player_id, "word_hunt")`, identical to every other game.
- Mid-session refresh / re-entry from the lobby tile while session is `active`: `play` returns the grid, all clues, the list of already-found words (each with answer text + traced coordinates), and the running score.
- Three terminal paths, all scored identically (`found_count * 100 + time_bonus`):
  - **Auto-complete:** triggered server-side inside the `find` handler when the find that just occurred makes `found_count == total_words`. The same response that confirms the find also carries the result payload.
  - **Submit:** explicit `POST /games/word-hunt/submit`. Finalises score, marks session `completed`.
  - **Navigation guard:** the frontend's existing navigation guard fires `POST /games/word-hunt/submit` (the same endpoint), so leaving the page is functionally a deliberate submit. There is no separate `abandon` endpoint and no `abandoned` status for Word Hunt sessions.
- After termination the session is `completed` (never `abandoned`). The Lobby tile is locked and re-entry returns the result screen, not the puzzle.

### DB Schema

Three new tables.

**`word_hunt_puzzles`** (seed data; expected to be a single row in practice, but the schema does not enforce that — future events can swap puzzles)

- `id` UUID PK
- `rows` SMALLINT NOT NULL
- `cols` SMALLINT NOT NULL
- `grid` JSONB NOT NULL — 2-D array of single-character uppercase letters, dimensions `rows × cols`
- `created_at` TIMESTAMPTZ NOT NULL

**`word_hunt_words`** (seed data; one row per hidden word per puzzle)

- `id` UUID PK
- `puzzle_id` UUID FK → `word_hunt_puzzles.id`
- `word` TEXT NOT NULL — canonical uppercase answer text; server-side comparison is case-insensitive
- `clue` TEXT NOT NULL — the riddle shown in the panel
- `start_row` SMALLINT NOT NULL
- `start_col` SMALLINT NOT NULL
- `end_row` SMALLINT NOT NULL
- `end_col` SMALLINT NOT NULL

**`word_hunt_finds`** (one row per successful find by a player)

- `id` UUID PK
- `session_id` TEXT FK → `game_sessions.id`
- `word_id` UUID FK → `word_hunt_words.id`
- `start_row`, `start_col`, `end_row`, `end_col` SMALLINT NOT NULL — the player's actual traced cells (may differ from the seeded coordinates if the word appears in multiple places)
- `found_at` TIMESTAMPTZ NOT NULL
- UNIQUE `(session_id, word_id)`

Final session score is stored on `game_sessions.score`, consistent with all other games. No score is denormalised onto `word_hunt_finds`.

### Seed Data Format

`backend/leap/seeds/data/word_hunt.json` — single object, hand-edited matrix:

```json
{
  "puzzle": {
    "rows": 15,
    "cols": 15,
    "grid": [
      ["U","S","W","A","J","D","P","B","H","D","E","V","O","P","S"],
      ["J","C","I","O","E","X","K","R","J","D","J","F","J","P","N"]
    ]
  },
  "words": [
    {
      "word": "KUBERNETES",
      "clue": "I orchestrate your containers but I'm not a conductor.",
      "start_row": 1,
      "start_col": 4,
      "end_row": 1,
      "end_col": 13
    }
  ]
}
```

Seed loader behaviour:
- Loader is idempotent (`ON CONFLICT DO NOTHING` / `DO UPDATE`) per platform contract.
- On every startup, the loader **validates** each word: walks the grid cells from `start` to `end` and asserts the resulting string (case-insensitive) equals `word`. Validation failures raise at startup and prevent the app from booting.

### Game Registry and Frontend Stub

- `GAMES` registry: replace the existing `crossword` entry with `word_hunt`, sorted alphabetically among existing entries per the registry's convention.
- Migration: drop `"crossword"` and add `"word_hunt"` to the `game_sessions.game_id` CHECK constraint.
- Frontend stub directory rename from `crossword/` to `word-hunt/`. Tile metadata, lobby constants, story files, and game-tile constants updated to match.
- `GET /players/me/sessions` and lobby tile logic already key on `game_id` — no aggregation code changes needed beyond the constant rename.

### API Contract

```
POST /games/word-hunt/play
  → 200 PlayResponse {
      session_status: "active" | "completed",
      session_score: int,                # 0 while active, final on completed
      puzzle: PuzzleState | null,        # null when session is completed
      result: ResultSchema | null        # populated when session is completed
    }

POST /games/word-hunt/find
  body: { start_row: int, start_col: int, end_row: int, end_col: int }
  → 200 FindResponse {
      matched: bool,
      word: FoundWord | null,            # populated only on matched=true
      session_status: "active" | "completed",
      session_score: int,
      result: ResultSchema | null        # populated only when this find auto-completed the session
    }

POST /games/word-hunt/submit
  → 200 SubmitResponse { result: ResultSchema }
```

`PuzzleState`:

```
{
  puzzle_id: UUID,
  rows: int,
  cols: int,
  grid: List[List[str]],                 # the literal letter matrix
  clues: List[{
    word_id: UUID,
    clue: str,
    found: bool,
    word: str | null,                    # populated iff found == true
    coordinates: {
      start_row: int, start_col: int,
      end_row: int, end_col: int
    } | null                             # populated iff found == true
  }],
  found_count: int,
  total_words: int,
  started_at: ISO8601                    # server-authoritative for client stopwatch
}
```

`FoundWord`:

```
{
  word_id: UUID,
  word: str,
  clue: str,
  coordinates: { start_row, start_col, end_row, end_col }
}
```

`ResultSchema`:

```
{
  score: int,                            # session total
  base_score: int,                       # found_count * 100
  time_bonus: int,
  found_count: int,
  total_words: int,
  time_elapsed_ms: int,
  found_words: List[{
    word_id: UUID,
    word: str,
    clue: str,
    coordinates: { start_row, start_col, end_row, end_col }
  }]
  # Unfound words are deliberately omitted; their `word` text never leaves the server.
}
```

`PlayResponse` is **idempotent**: repeated calls with no intervening find return the same `PuzzleState` snapshot. The grid never changes; only the `clues[*].found` flags and `found_count` advance.

### Validation and Server-Authoritative Anti-Cheat

- All `find` coordinates are validated against the seeded `rows`/`cols`.
- The drag direction must satisfy: `(dr == 0) XOR (dc == 0) XOR (abs(dr) == abs(dc))` where `dr = end_row - start_row`, `dc = end_col - start_col`. Reject otherwise as a malformed drag (treated as a miss, not a 4xx — the UI surfaces this as a normal failed trace).
- The traced string is built server-side from the seeded grid; the client never sends the word text. This closes the obvious cheat of submitting an answer string without ever finding it in the grid.
- The answer text of unfound words is never emitted in any response.

### Module Breakdown

- **`leap/games/word_hunt/scoring.py`** — pure functions: `compute_base_score(found_count)`, `compute_time_bonus(elapsed_ms)`, `compute_final_score(found_count, elapsed_ms)`. No I/O — deepest testable unit.
- **`leap/games/word_hunt/grid.py`** — pure functions: `direction_of(start, end)`, `walk_cells(grid, start, end) -> str`, `validate_trace(rows, cols, start, end) -> bool`, `validate_seeded_word(grid, word, start, end) -> bool`. Used by both the seed loader (validation) and the service (find resolution). Pure — no DB, no DTOs.
- **`leap/games/word_hunt/service.py`** — `WordHuntService` owns session lifecycle: `play`, `submit_find`, `submit`. Warms a puzzle cache from DB at startup (mirrors `RapidFireService` and `PinpointService`). Owns the DB session via `async with self.ctx.session() as session`. Responsibilities: session create/resume, find resolution via `grid.walk_cells`, duplicate-find rejection, auto-complete detection, score computation, terminal-state transitions, result construction.
- **`leap/dao/word_hunt_puzzle_dao.py`** — read-only; `get_all_with_words` for cache warm at startup. Stubs `_to_orm` / `_apply_filters` with `raise NotImplementedError` per AGENTS.md rule.
- **`leap/dao/word_hunt_word_dao.py`** — read-only; `get_for_puzzle`. Stubs `_to_orm` / `_apply_filters`.
- **`leap/dao/word_hunt_find_dao.py`** — `create`, `get_for_session`, `count_for_session`.
- **ORM models** — `WordHuntPuzzleModel`, `WordHuntWordModel`, `WordHuntFindModel` in `leap/dao/models/`, registered in `leap/dao/models/__init__.py`.
- **Types** (`leap/types/word_hunt.py`) — `WordHuntPuzzleDTO` (includes its words), `WordHuntWordDTO`, `WordHuntFindDTO`, `WordHuntPuzzleStateDTO`, `WordHuntResultDTO`, `WordHuntPlayPayload`, `WordHuntFindPayload`, `WordHuntFoundWordDTO`. All subclass `BaseLeapModel`.
- **API schema** (`leap/api/schema/word_hunt.py`) — request/response Pydantic models per the API Contract above.
- **API routes** (`leap/api/routes/games/word_hunt.py`) — three handlers; each delegates to `WordHuntService` and maps DTOs to API schemas. Mounted at prefix `/games/word-hunt` in `leap/api/main.py`.
- **ServiceContainer** — wires `WordHuntService` alongside other game services; `initialize(session)` called at startup to warm the puzzle cache.
- **Seed data** (`leap/seeds/data/word_hunt.json`) — single object as described above. Seed loader validates every word's coordinates against the grid before inserting.
- **Alembic migration** — adds three new tables and updates the `game_sessions.game_id` CHECK constraint (`crossword` → `word_hunt`).
- **Errors** (`leap/config/errors.py`) — additions: `NO_WORD_HUNT_PUZZLE_AVAILABLE` (3xxx range), `WORD_HUNT_SESSION_ALREADY_COMPLETED` (2xxx range). Service exceptions in `leap/service/exceptions.py` subclass `BaseServiceException` and map to these.
- **Frontend** — replaces the placeholder route at `app/(games)/word-hunt/`. Components: `WordHuntGame` shell, `LetterGrid` (pointer-driven drag selection that constrains to 8 directions and emits start/end cell coords), `ClueListPanel` (cards with flip-to-reveal-on-found), `Stopwatch`, `SubmitButton`, `ResultView`. Typed API client wrappers in `lib/api/word-hunt.ts`. React Query hooks for `play`, `find`, `submit`. Wired into the existing navigation guard with `submit` as the guard handler.

### Constants

In `leap/games/word_hunt/scoring.py` (or a dedicated `constants.py`):

- `WORD_HUNT_BASE_PER_WORD = 100`
- `WORD_HUNT_TIME_BONUS_MAX = 500`
- `WORD_HUNT_TIME_DECAY_MS = 600_000`

### Frontend UX Decisions

- Two-pane layout: letter grid on the left, scrollable clue list panel on the right. On narrow viewports the panel stacks below the grid.
- Grid cells are square, evenly sized to fit the viewport. Pointer-down begins a trace from a cell; pointer-move snaps the selection to the nearest valid straight line (horizontal, vertical, or diagonal) from the start cell; pointer-up commits the trace.
- The committed trace fires `POST /find` with `{start_row, start_col, end_row, end_col}`.
- **Miss feedback:** the selected cells flash red briefly (~250 ms) then clear.
- **Hit feedback:** the traced cells lock into a persistent highlight colour; the corresponding clue card flips with a brief animation to reveal `word + ✓`; a "+100" score increment animates near the stopwatch.
- Clue list: each card shows `clue` only while unsolved; flips on find to show `word + ✓` and is visually de-emphasised (struck or faded) so the player's attention goes to remaining clues.
- Grid is **neutral** — no hint highlights for the active or hovered clue. Selecting a clue card does nothing.
- Stopwatch is rendered client-side from `started_at` returned by `play`, but the score and time bonus are always computed server-side from the server's `started_at`.
- Submit button visible throughout play. Pressing it calls `POST /submit` and transitions to the result screen.
- Result screen mirrors the platform pattern: total score with `base + time_bonus` breakdown, `found_count / total_words`, time elapsed, and a list of found words (clue + answer). Unfound words are not displayed. "Back to Lobby" button.
- Navigation guard calls `POST /submit` on confirmed exit (back button, route change, tab close attempt), then disarms and lets the navigation proceed.

---

## Testing Decisions

Good tests for this game test **external behaviour** — what the service returns given specific sequences of calls — not internal helpers like cache structure or query construction. Tests use hand-written DAO fakes (not `MagicMock`) per project convention. DAO tests that require real SQL execution are integration tests — mark with a TODO comment per AGENTS.md.

### Modules to test

**`scoring.py` — unit tests (highest priority)**

- `compute_base_score`: `0 → 0`, `1 → 100`, `10 → 1000`.
- `compute_time_bonus`: `0ms → 500`, `300_000ms → 250`, `600_000ms → 0`, `900_000ms → 0` (clamped), boundary at exactly `600_000` is 0.
- `compute_final_score`: composition correctness across representative `(found_count, elapsed_ms)` pairs.

**`grid.py` — unit tests (highest priority)**

- `direction_of`: each of the eight cardinal/diagonal directions returns the expected `(dr, dc)` unit vector. Same start/end raises.
- `validate_trace`: in-bounds horizontal, vertical, both diagonals — accept. Out-of-bounds — reject. L-shaped (non-zero unequal deltas) — reject. Length 1 (start == end) — reject.
- `walk_cells`: builds the expected string for each of the eight directions including reverse diagonals; raises on invalid trace; uppercase-normalises the result.
- `validate_seeded_word`: accepts a correctly-placed seed; rejects when the traced string does not match `word`; rejects when the trace is malformed.

**`WordHuntService` — service-level acceptance tests with hand-written DAO fakes**

- `play` with no existing session → creates session, returns `PuzzleState` with `found_count=0`, all clues `found=false`, no answers leaked.
- `play` while session is `active` with prior finds → returns the same grid and clues; the found clues show `word` + `coordinates`; unfound clues do not.
- `submit_find` matching an unsolved word → records find, returns `matched=true` with the found word + coordinates, `session_score` increments by 100.
- `submit_find` matching the final unsolved word → auto-completes session, response includes `result`, `session_status="completed"`, score includes the time bonus.
- `submit_find` against a word already found → `matched=false`, score unchanged (idempotent on the client side, no duplicate row).
- `submit_find` with a trace whose string does not match any unsolved word → `matched=false`, score unchanged.
- `submit_find` with out-of-bounds coordinates → `matched=false` (treated as a miss, not raised) — confirms the server gracefully handles a malformed client without leaking info.
- `submit_find` with a non-linear trace (e.g. `dr=1, dc=2`) → `matched=false`.
- `submit_find` reverse-direction trace of a forward-seeded word → `matched=true` if and only if the reversed string matches an unsolved answer (collision case).
- `submit_find` collision case: the answer string appears in two grid locations; tracing either location credits the find; tracing the other location after the find is a miss.
- `submit` while `active` with partial finds → session `completed`, score = `found_count * 100 + time_bonus`, result lists only found words.
- `submit` immediately at start with zero finds → session `completed`, score = `time_bonus` only (which itself will be near `WORD_HUNT_TIME_BONUS_MAX` at `elapsed_ms ≈ 0`).
- `submit` on an already-completed session → `WordHuntSessionAlreadyCompletedException`.
- `play` on a `completed` session → returns `puzzle=null`, `result` populated with the original final state.
- Time bonus integration: a session that completes at simulated `elapsed_ms = 300_000` returns `time_bonus = floor(500 * (1 - 300/600)) = 250`. Service uses an injectable clock (not `datetime.utcnow` directly) so tests can advance time deterministically — same pattern as Wiki and Pinpoint time-bonus tests.

**Seed loader — unit test**

- Loading a seed whose word coordinates spell the declared word succeeds.
- Loading a seed where the word does not match the traced cells raises at startup before any DB writes for that puzzle.
- Loading the same seed twice is idempotent (no duplicate rows; updates apply).

**Prior art:** `backend/tests/unit/services/test_rapid_fire_service.py`, `test_pinpoint_service.py` (same fake-DAO style, same session-lifecycle assertions). Route-layer tests follow `backend/tests/unit/api/rapid_fire/` (auth, play, find, submit split files).

### E2E tests

Add a Word Hunt journey to `backend/tests/e2e/`:

- **`test_word_hunt_journey.py`** — full playthrough: login → start → find every word in order → assert session `completed`, final score equals `N * 100 + time_bonus`, lobby tile flips to `completed`, leaderboard reflects the score.
- **`test_word_hunt_lifecycle_journeys.py`** —
  - Partial-find then explicit Submit → session `completed`, score equals `found_count * 100 + time_bonus`, result lists only found words and never the unfound `word` text.
  - Mid-game refresh → second `play` returns same grid, the already-found words marked `found=true` with their coordinates and answer text, unfound words still hidden.
  - Navigation-guard submit (POST `/submit` directly with partial finds) → same outcome as the explicit Submit path.
  - Cheating attempts: `find` with out-of-bounds coords, non-linear trace, and a correctly-shaped trace through letters that do not spell any unsolved word — all return `matched=false` and never appear in `word_hunt_finds`.

### Frontend tests

- Reducer / hook tests for the Word Hunt client state machine (analogous to existing `rapid-fire` reducer tests): drag start, drag move (direction snapping), drag commit, miss/hit handling, submit transition.
- Direction-snapping logic for `LetterGrid`: pointer paths that wander off-axis snap to the nearest of the 8 lines from the drag origin.
- API client wrapper tests (`lib/api/word-hunt.test.ts`) following the Rapid Fire pattern.
- Navigation guard integration: confirmed exit triggers `POST /submit` and transitions through the result screen before completing the navigation.

---

## Out of Scope

- An "abandon" endpoint or `abandoned` status for Word Hunt sessions (the navigation guard submits instead).
- Multiple sequential grids / rounds per session — Word Hunt is a single grid, single session.
- Per-word time tracking or per-word time bonuses — time bonus is computed once, session-wide.
- Active-clue highlighting in the grid (no hints about where a word lives).
- Revealing unfound words on the result screen or at any point post-game.
- A hint system of any kind.
- Negative scoring for failed drags.
- A hard session timeout — the stopwatch runs indefinitely.
- Per-cell click selection (UX is drag-only; tap-tap-to-select is intentionally not supported in the first version).
- Admin tooling for live puzzle editing during the event; puzzles are seeded once at startup.
- Multi-puzzle support in a single event — the schema permits more than one `word_hunt_puzzles` row, but the loader and service assume a single active puzzle for the event.
- Any logic for Wikipedia Speed Run, Picture Illustration, Four Pics One Lie, Pinpoint, or Rapid Fire.

---

## Further Notes

- The `word_hunt` game id must be added to `leap/config/constants.py` `GAMES` and to the `game_sessions.game_id` CHECK constraint via a new Alembic migration **before** any code paths reference it. The same migration drops the obsolete `crossword` value.
- The literal letter matrix in the seed must be uppercase A–Z only; the loader normalises to uppercase but is strict about non-letter characters (e.g. spaces, digits) and will fail validation if any are present.
- The injectable clock pattern used for Wiki / Pinpoint time-bonus tests should be reused here so that `compute_time_bonus` and the service-level time-bonus assertions are deterministic.
- A Meridian design YAML (`docs/design/word-hunt.meridian.yaml`) should be authored before implementation, walking the call graph top-down route → service → DAO → model, mirroring the existing Rapid Fire design.
- The reference grid in `docs/games-examples/crossword.jpeg` (a 15×15 grid with words like KUBERNETES, DEVOPS, EMBEDDINGS, ANGULAR, COPILOT, SPRING, CLOUD, AGENTS, GENERATIVE AI) is a good starting point for the seed content. "GENERATIVE AI" contains a space — for seed purposes it would need to be a single token (`GENERATIVEAI`) or split into two separate hidden words; the content team will decide per puzzle.
- `CONTEXT.md` is updated as part of this PRD with the new domain terms: **Word Hunt**, **Letter Grid**, **Hidden Word**, **Riddle Card**, **Word Trace**, **Find**, **Word Hunt Result**.
