# Word Hunt Game — Full Implementation

## Intent

Implement Word Hunt end-to-end: a server-authoritative riddle-driven word-search game. The player sees a single seeded Letter Grid alongside a panel of Riddle Cards. Each riddle's answer is a Hidden Word lying along a straight line in any of the eight directions (horizontal, vertical, both diagonals, forwards or reverse). The player drags across cells to perform a Word Trace; the server derives the traced string from the submitted start/end coordinates and credits a Find if it matches an unsolved Hidden Word. Scoring is `100 × found_count + time_bonus`, where the time bonus is a single session-level value that decays from session start. The game ends when every word is found, when the player presses Submit, or when the navigation guard fires — all three terminal paths are scored identically. There is no abandon endpoint and no resume after leaving. The internal `game_id` is `word_hunt`, replacing the placeholder `crossword`.

## Overall Acceptance Criteria

- `crossword` is fully retired across the platform — replaced by `word_hunt` in the `GAMES` registry, the `game_sessions.game_id` CHECK constraint, the frontend route, lobby tile metadata, and all related stories/constants
- `POST /games/word-hunt/play` is idempotent: returns the current grid + clues + already-found words on resume, returns the result payload once the session is `completed`
- `POST /games/word-hunt/find` derives the traced string server-side from `{start_row, start_col, end_row, end_col}`, matches it against unsolved Hidden Words, records the Find, and recomputes the running score; auto-completes the session when the last word is found
- `POST /games/word-hunt/submit` finalises the session as `completed`, computes `score = found_count × 100 + time_bonus`, and returns a `ResultSchema` listing only found words
- The navigation guard on the Word Hunt frontend route calls `POST /submit` on confirmed exit — there is no separate abandon endpoint and no `abandoned` status for Word Hunt sessions
- The answer text of an unfound Hidden Word is never included in any API response — on `play`, on `find` (miss), or on the result screen
- The grid is neutral throughout play — no hints, no active-clue highlighting; the only highlights are persistent on found cells and a transient red flash on a miss
- The time bonus is `max(0, floor(500 × (1 - elapsed_ms / 600_000)))` against `game_sessions.started_at`; floors at 0, never negative; the session has no hard timeout
- Seed data is a hand-edited JSON file containing a 2-D letter matrix plus per-word `{word, clue, start, end}`; the seed loader validates every word's coordinates against the grid at startup and refuses to boot on validation failure
- Grid dimensions (`rows`, `cols`) come from the seed; no hard-coded grid size
- Same answer string appearing in multiple grid locations is supported — any valid trace credits the find while the word is unsolved
- Session is locked once `completed` — no replay, no re-entry into gameplay; the lobby tile then surfaces the result screen
- Lobby tile reflects `not_started` / `in_progress` / `completed` via the existing `GET /players/me/sessions` integration
- All unit, service, and e2e API tests across happy path, partial-submit, refresh-resume, navigation-guard-submit, and cheating-attempt rejection pass

## Execution Plan

```
Batch 1 (solo):     Sub-1 (happy-path tracer)
Batch 2 (parallel): Sub-2 (drag UX polish) ∥ Sub-3 (time bonus + stopwatch) ∥ Sub-4 (nav guard + polished result screen)
Batch 3 (solo):     Sub-5 (e2e api journey tests)
```

## References

- PRD: `docs/plans/2026-05-17-word-hunt-prd.md`
- Domain glossary: `CONTEXT.md` (Word Hunt, Letter Grid, Hidden Word, Riddle Card, Word Trace, Find, Word Hunt Result)
- Reference implementation pattern: `leap/games/rapid_fire/` and `leap/games/pinpoint/` (service shape, cache-warm-at-startup, scoring layout), `leap/api/routes/games/pinpoint.py` (route layer)
- Reference puzzle visual: `docs/games-examples/crossword.jpeg` (15×15 grid; tech-themed words like KUBERNETES, DEVOPS, EMBEDDINGS, ANGULAR, COPILOT, SPRING, CLOUD, AGENTS)
- Entry points: `POST /games/word-hunt/play`, `POST /games/word-hunt/find`, `POST /games/word-hunt/submit`
