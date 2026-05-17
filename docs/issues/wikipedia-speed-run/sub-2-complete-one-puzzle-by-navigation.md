# Complete One Puzzle By Navigation

**Status:** done

## Parent

`docs/issues/wikipedia-speed-run/parent.md`

## What to build

Make a single Wiki Puzzle completable through backend-recorded Navigation Steps. Internal article links should post to `POST /games/wiki/navigate`, increment `steps_taken`, follow redirects as one step, detect the target page, compute the puzzle score, and return a per-puzzle result.

This slice should also establish the deep modules for scoring, Wikipedia fetching, and HTML rewriting with realistic fixture-backed tests.

## Acceptance criteria

- [x] `POST /games/wiki/navigate` records exactly one Navigation Step for a forward article click
- [x] Redirects count as one step and store the canonical landed title
- [x] `click_path`, `current_title`, and `steps_taken` are updated server-side
- [x] Reaching the target page marks the Wiki Puzzle Attempt `completed`
- [x] Puzzle score uses the approved 125-point steps score plus 75-point time bonus formula
- [x] The client receives `state='puzzle_completed'` with steps, time, score, target reveal, and total score so far
- [x] The frontend intercepts rewritten internal article links and calls `navigate`
- [x] A per-puzzle result screen appears after completion with a deliberate next action placeholder
- [x] Unit tests cover scoring and HTML rewriting policy
- [x] API e2e test uses captured Wikimedia fixture HTML for the first round's optimal path from the PRD

## Blocked by

- `docs/issues/wikipedia-speed-run/sub-1-start-first-wiki-puzzle.md`
