# Start First Wiki Puzzle

**Status:** done

## Parent

`docs/issues/wikipedia-speed-run/parent.md`

## What to build

Create the first playable tracer bullet for Wikipedia Speed Run: seeded Wiki Rounds, persistent Wiki Puzzle Attempts, `POST /games/wiki/play`, and a minimal frontend page that starts or resumes Puzzle 1 with the Puzzle Clue, timer shell, and rewritten start article HTML.

This slice should establish the route → service → DAO → model shape for the game without implementing forward navigation yet.

## Acceptance criteria

- [x] `wiki_rounds` and `wiki_puzzle_attempts` are added through an Alembic migration using the PRD-approved model shape
- [x] All 5 Wiki Rounds are seeded idempotently with `clue`, start/target titles and URLs, `optimal_click_count`, `solution_path`, and `time_limit_ms`
- [x] Seed data renames the design artifact's `hint` concept to `clue`
- [x] `POST /games/wiki/play` creates or resumes a `game_sessions` row with `game_id='wiki'`
- [x] `POST /games/wiki/play` creates the first active Wiki Puzzle Attempt and returns Puzzle 1 metadata plus rewritten start article HTML
- [x] The response includes `time_remaining_ms` computed from server-side `started_at`
- [x] A minimal frontend wiki page can call `play` and render Puzzle 1 clue, timer shell, progress label, and article content
- [x] Tests cover the initial play/resume path through the service and API surface

## Blocked by

None - can start immediately
