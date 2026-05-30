# Crossword Game — Full Implementation

**Status:** done

## Intent

Implement Crossword end-to-end as the seventh game (`game_id: crossword`, player-facing name "Crossword"): a server-authoritative classic intersecting-word puzzle. The player sees a blank Crossword Grid (open and blocked cells, corner numbers) alongside a two-section Across/Down clue panel. The grid starts completely blank — no letters are pre-revealed. The player clicks a cell and types from the keyboard; each open cell belongs to one Across and/or one Down Crossword Entry. The instant an entry's cells are all filled, the client auto-checks it against the server: a correct entry locks green and scores, a wrong entry flashes red, keeps the player's letters, and stays editable. Scoring is `100 × solved_count + time_bonus`, where the time bonus is a single session-level value that decays from session start. The game ends when every entry is solved, when the player presses Submit, or when the navigation guard fires — all three terminal paths are scored identically. There is no abandon endpoint and no resume of in-progress (unsolved) letters; only solved entries survive a refresh. The solution never leaves the server: the client only ever receives letters for entries the player has already solved.

This game reuses the `crossword` identifier that Word Hunt vacated. It mirrors Word Hunt structurally in nearly every respect; the divergence is the interaction model (keyboard cell-entry instead of drag) and the cell-sharing intersection logic unique to crosswords.

## Overall Acceptance Criteria

- `crossword` is added to the `GAMES` registry and the `game_sessions.game_id` CHECK constraint; the placeholder frontend route at `(games)/crossword/` is replaced with the real game; lobby tile metadata and constants reflect "Crossword"
- `POST /games/crossword/play` is idempotent: returns the blank skeleton + clues + already-solved entries (with their letters/cells) on resume, returns the result payload once the session is `completed`
- `POST /games/crossword/check` compares the submitted entry letters server-side against the seeded answer, records a Crossword Solve on a match, recomputes the running score, and auto-completes the session when the last entry is solved
- `POST /games/crossword/submit` finalises the session as `completed`, computes `score = solved_count × 100 + time_bonus`, and returns a `ResultSchema` listing only solved entries
- The navigation guard on the Crossword frontend route calls `POST /submit` on confirmed exit — there is no separate abandon endpoint and no `abandoned` status for Crossword sessions
- The answer text and unsolved letters of an unsolved Crossword Entry are never included in any API response — on `play`, on `check` (miss), or on the result screen; the initial skeleton carries no letters at all
- A wrong completed entry costs nothing: it flashes red, keeps the player's typed letters, and stays editable; locked-correct letters from solved crossing entries are never disturbed
- The time bonus is `max(0, floor(500 × (1 - elapsed_ms / 600_000)))` against `game_sessions.started_at`; floors at 0, never negative; the session has no hard timeout
- Seed data is a hand-edited JSON file containing a 2-D solution matrix (uppercase letters or `null` for blocked cells) plus per-entry `{number, direction, start_row, start_col, answer, clue}`; the seed loader validates every entry's spelling against the matrix AND every intersection's consistency at startup, refusing to boot on failure
- Grid dimensions (`rows`, `cols`) and blocked-cell layout come from the seed; no hard-coded grid size
- A single shared cell that completes both its Across and its Down entry credits both independently
- Session is locked once `completed` — no replay, no re-entry into gameplay; the lobby tile then surfaces the result screen
- Lobby tile reflects `not_started` / `in_progress` / `completed` via the existing `GET /players/me/sessions` integration
- All unit, service, and e2e API tests across happy path, wrong-entry rejection, partial-submit, refresh-resume, navigation-guard-submit, and cheating-attempt rejection pass

## Execution Plan

```
Batch 1 (solo):     Sub-1 (happy-path tracer) ✓
Batch 2 (parallel): Sub-2 (keyboard UX polish) ✓ ∥ Sub-3 (time bonus + stopwatch) ✓ ∥ Sub-4 (nav guard + result screen) ✓
Batch 3 (solo):     Sub-5 (e2e api journey tests) ✓
```

## Puzzle Content (launch seed)

12×12 grid, 10 entries (from `docs/final_game_content/crossword.png` / `crossword.md`). Exact cell coordinates and the literal matrix must be transcribed from the image; the seed loader's startup validation is the safety net.

| # | Dir | Answer | Len | Clue |
|---|-----|--------|-----|------|
| 1 | across | MICROSERVICE | 12 | Small, independently deployable unit in modern cloud architecture |
| 4 | across | KUBERNETES | 10 | Container orchestration platform originally built at Google |
| 7 | across | ATOMICITY | 10 | ACID property that ensures a transaction is all-or-nothing |
| 9 | across | PIPELINE | 8 | Automated workflow from code commit to deployment |
| 1 | down | MOCK | 4 | Simulated object used in testing to replace a real dependency |
| 2 | down | EVENTDRIVEN | 11 | Communication style where services interact through events rather than direct calls |
| 3 | down | DNS | 3 | Protocol that assigns a readable name to a numerical server address |
| 5 | down | GITOPS | 6 | Philosophy of treating infrastructure setup the same way as application code |
| 6 | down | CACHING | 7 | Technique of storing frequently accessed data closer to the user for faster retrieval |
| 8 | down | DRIFT | 5 | When a deployed model's accuracy degrades over time |

## References

- PRD: `docs/prds/2026-05-30-crossword-prd.md`
- Domain glossary: `CONTEXT.md` (Crossword, Crossword Grid, Crossword Entry, Crossword Solve, Crossword Result)
- Reference implementation pattern: `leap/games/word_hunt/` (service shape, cache-warm-at-startup, `grid.py` / `scoring.py` layout, seed-loader validation), `leap/api/routes/games/word_hunt.py` (route layer), `docs/issues/word-hunt/` (issue structure)
- Puzzle content: `docs/final_game_content/crossword.png`, `docs/final_game_content/crossword.md`
- Entry points: `POST /games/crossword/play`, `POST /games/crossword/check`, `POST /games/crossword/submit`
