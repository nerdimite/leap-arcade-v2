# Back Button And Abandon Flow

**Status:** done

## Parent

`docs/issues/wikipedia-speed-run/parent.md`

## What to build

Add the optional in-game Wiki Back Button and the abandon flow. The back button should be controlled by configuration, count as a Navigation Step, preserve the full click path including backtracking, and never rely on browser history. The Navigation Guard should abandon the overall wiki game consistently with Rapid Fire.

## Acceptance criteria

- [x] `POST /games/wiki/back` is available only when the back feature flag is enabled
- [x] Back is rejected when there is no previous page in the active attempt's click path
- [x] A back action counts as exactly one Navigation Step
- [x] Back updates `current_title` and returns rewritten article HTML for the previous page
- [x] The full click path remains auditable and includes backtracking rather than deleting history
- [x] Browser back remains handled by the Navigation Guard, not by wiki navigation
- [x] `POST /games/wiki/abandon` marks the active game session `abandoned`
- [x] Abandon preserves completed puzzle scores and treats active/untouched puzzles as 0 for final display
- [x] Abandoned wiki sessions lock the Lobby tile and cannot be replayed
- [x] Tests cover enabled/disabled back, no-previous-page back, abandon status, and lobby locking

## Blocked by

- `docs/issues/wikipedia-speed-run/sub-2-complete-one-puzzle-by-navigation.md`
