# Pinpoint Game — Full Implementation

## Intent

Implement Pinpoint end-to-end: a server-authoritative word-association game inspired by LinkedIn Pinpoint. Each puzzle hides a category behind 5 thematic clue words; the player sees one clue at a time and types a guess. Each wrong guess unconditionally reveals the next clue. With at most 5 guesses per puzzle, scoring rewards both fewer clues used and faster solves. The player works through every seeded puzzle in a random order per session. Answer matching is exact-after-normalisation against a curated alias list — never fuzzy. The canonical answer is never revealed to the client, even on failure.

## Overall Acceptance Criteria

- `POST /games/pinpoint/play` is idempotent: returns the current active puzzle on resume, advances to the next random unattempted puzzle after a terminal puzzle, returns the final result when all puzzles are done
- `POST /games/pinpoint/guess` validates guesses via normalisation (`strip().lower()`) and membership against `{answer} ∪ answer_aliases`; on a wrong guess increments `clues_revealed`, appends the guess to `guesses`, and reveals the next clue; on the 5th wrong guess marks the puzzle `failed` with score 0
- `POST /games/pinpoint/abandon` ends the session as `abandoned`, closes any active puzzle attempt as `failed` with score 0, and surfaces unattempted puzzles in the result as `not_reached`
- Per-puzzle base score is 500 / 400 / 300 / 200 / 100 by clues used at solve time; failed puzzles score 0
- Per-puzzle time bonus on solve is `max(0, floor(100 * (1 - elapsed_ms / 90_000)))`; failed puzzles get 0 bonus
- Maximum per puzzle is 600 pts; max session score is 600 × pool size; no negative scoring
- All seeded puzzles are dynamically randomised per session — order is not stored, the service picks uniformly from unattempted puzzles on each advance
- The canonical `answer` and `answer_aliases` are never sent to the frontend — not on solve, not on failure, not on the result screen
- Stopwatch runs indefinitely with no hard timeout — the time bonus simply floors at 0 after 90 seconds
- Session is locked once `completed` or `abandoned` — no replay, no re-entry
- Lobby tile reflects `not_started` / `in_progress` / `completed` / `abandoned` via the existing `GET /players/me/sessions` integration
- All unit, service, and e2e API tests across happy path, failure path, abandon, refresh-resume, and time-bonus scenarios pass

## Execution Plan

```
Batch 1 (solo):     Sub-1 (happy-path tracer)
Batch 2 (parallel): Sub-2 (failure path + 5-card UI) ∥ Sub-3 (time bonus + stopwatch) ∥ Sub-4 (abandon + nav guard)
Batch 3 (solo):     Sub-5 (e2e api journey tests)
```

## References

- PRD: `docs/plans/2026-05-17-pinpoint-prd.md`
- Domain glossary: `CONTEXT.md` (Pinpoint, Pinpoint Puzzle, Pinpoint Puzzle Attempt, Clue Reveal, Pinpoint Time Bonus)
- Reference implementation pattern: `leap/games/rapid_fire/` (service shape, scoring layout), `leap/api/routes/games/rapid_fire.py` (route layer)
- Example seed shape: `docs/games-examples/pinpoint.json` (per-puzzle shape; production seed must add `answer_aliases`)
- Entry points: `POST /games/pinpoint/play`, `POST /games/pinpoint/guess`, `POST /games/pinpoint/abandon`
