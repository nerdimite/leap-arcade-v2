# Progress Through All 5 Puzzles

**Status:** done

## Parent

`docs/issues/wikipedia-speed-run/parent.md`

## What to build

Extend the one-puzzle flow into the full 5-puzzle Wikipedia Speed Run. After each completed puzzle, the player should intentionally continue to the next fixed-order Wiki Round. Completing the fifth puzzle should complete the overall game session, write the total score, update lobby/session status, and make the player visible on the leaderboard.

## Acceptance criteria

- [x] Completing a non-final puzzle returns a result state and indicates that another puzzle is available
- [x] The next action creates or returns the next fixed-order Wiki Puzzle Attempt
- [x] The frontend shows "Puzzle N of 5" and a compact progress indicator
- [x] The frontend shows a click-path breadcrumb for the active puzzle
- [x] Completing the fifth puzzle marks `game_sessions.status='completed'`
- [x] `game_sessions.score` stores the aggregate score across all 5 puzzles
- [x] Final result screen shows total score and 5 per-puzzle breakdowns with target-title reveal
- [x] Lobby/session summary reflects completed wiki status and score without special casing beyond existing game-session rules
- [x] Leaderboard includes completed wiki score in the player's total
- [x] Tests cover multi-puzzle progression and final completion

## Blocked by

- `docs/issues/wikipedia-speed-run/sub-2-complete-one-puzzle-by-navigation.md`
