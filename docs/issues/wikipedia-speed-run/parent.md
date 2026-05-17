# Wikipedia Speed Run

**Status:** done

## What to build

Implement Wikipedia Speed Run as the second playable LEAP mini-game. Players work through all 5 Wiki Puzzles in fixed order, navigate rewritten Wikipedia article HTML through backend-recorded Navigation Steps, and receive a final score out of 1000 based on click efficiency and time bonus.

**PRD:** `docs/plans/2026-05-17-wikipedia-speed-run-prd.md`

## Execution plan

```
Batch 1 (done):              Sub-1 — Start First Wiki Puzzle
Batch 2 (done):              Sub-2 — Complete One Puzzle By Navigation
Batch 3 (done):              Sub-3 — Progress Through All 5 Puzzles
Batch 4 (done):              Sub-4 — Server-Authoritative Timeout And Resume ┐
                              Sub-5 — Back Button And Abandon Flow            ├─ parallel
Batch 5 (done):              Sub-6 — Wikipedia Rendering Hardening            ┘
```

**Sub-1:** done — `docs/issues/wikipedia-speed-run/sub-1-start-first-wiki-puzzle.md`

**Sub-2:** done — `docs/issues/wikipedia-speed-run/sub-2-complete-one-puzzle-by-navigation.md`

**Sub-3:** done — `docs/issues/wikipedia-speed-run/sub-3-progress-through-all-5-puzzles.md`

**Sub-4:** done — `docs/issues/wikipedia-speed-run/sub-4-server-authoritative-timeout-and-resume.md`

**Sub-5:** done — `docs/issues/wikipedia-speed-run/sub-5-back-button-and-abandon-flow.md`

**Sub-6:** done — `docs/issues/wikipedia-speed-run/sub-6-wikipedia-rendering-hardening.md`

## Overall acceptance criteria

- [x] All 5 Wiki Rounds are seeded idempotently with clue, start/target titles, optimal click count, solution path, and time limit
- [x] `POST /games/wiki/play` starts/resumes a server-authoritative timed puzzle attempt
- [x] `POST /games/wiki/navigate` records one Navigation Step, rewrites/returns article HTML, and completes a puzzle on target reach
- [x] Timeout scores 0 and advances to the next puzzle
- [x] Completing all 5 puzzles writes the final wiki score to `game_sessions`
- [x] E2E tests use captured real Wikimedia fixtures for an optimal-path happy journey
- [x] Frontend renders split-panel gameplay with clue, timer, progress, breadcrumb, loading overlay, per-puzzle result, and final result
