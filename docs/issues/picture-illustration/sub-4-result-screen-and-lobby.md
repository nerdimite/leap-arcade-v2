# Sub-4: Result Screen Polish + Lobby Tile Integration

**Type:** AFK
**Status:** ready-for-agent
**Depends on:** Sub-3
**Blocks:** nothing

## Parent

`docs/issues/picture-illustration/parent.md`

## What to build

Replace the minimal result block from Sub-1 with a polished Result Screen for Picture Illustration, and verify the Lobby tile correctly reflects session state via the existing generic plumbing.

End-to-end behaviour delivered:

1. **Result Screen** — replaces the inline result block on the same page (mirrors the Rapid Fire pattern):
   - Total score in a prominent treatment
   - Accuracy score and time bonus shown separately, so the player understands how their score was built
   - Time remaining at completion, formatted (e.g. "2m 14s left on the clock — +134 pts")
   - Per-puzzle breakdown: a list of all 5 puzzles, each row showing the image thumbnail and a status pill (`Correct` / `Wrong` / `Skipped` / `Not reached`). Canonical answers are NOT displayed.
   - A "Back to Lobby" button at the bottom
2. **Wrong-answer UX polish (carry-over from Sub-1)** — input field shakes briefly on wrong answer, displays "Incorrect, try again." in red below the field, then auto-clears after ~1 second so the player can immediately type the next attempt.
3. **Lobby tile integration** — verify (do not necessarily build) that the existing `GET /players/me/sessions` plumbing correctly surfaces the picture session status to the Lobby Game Tile. The tile should show `not_started` before the player starts, `in_progress` during play, and `completed` after the result screen is reached. If the existing generic Lobby code does not already handle the picture game id, wire it in.
4. **Session-locked enforcement** — once `completed`, the Lobby tile is locked (no re-entry). `POST /games/picture/play` for a completed session returns the result block (player can re-view their result screen but cannot replay).

## Acceptance criteria

- [ ] Result Screen renders the polished layout with total score, separated accuracy + time bonus, and time remaining
- [ ] Per-puzzle list shows image thumbnails and status pills; canonical answers do NOT appear anywhere in the rendered DOM
- [ ] "Back to Lobby" navigation works from the Result Screen
- [ ] Wrong-answer feedback shakes the input, displays the inline error, and auto-clears the input
- [ ] Lobby tile for Picture Illustration shows `not_started` before play, `in_progress` during an active session, and `completed` after the result screen has been seen — verified end-to-end
- [ ] Clicking the Lobby tile while completed navigates to the picture page where the Result Screen is displayed (no replay)
- [ ] `POST /games/picture/play` for a completed session returns the result block (no session_started_at, no puzzle)

## Blocked by

Sub-3 — the result schema enrichment (`accuracy_score`, `time_bonus`, `time_remaining_seconds`, `not_reached` status) and the abandon path must exist before the polished result screen can render them.
