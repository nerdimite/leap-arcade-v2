# Sub-4: Abandon Endpoint + Navigation Guard

**Type:** AFK
**Status:** done
**Depends on:** Sub-1
**Blocks:** Sub-5

## Parent

`docs/issues/pinpoint/parent.md`

## What to build

Wire Pinpoint into the platform's abandon lifecycle so that mid-game navigations cannot leave the session orphaned. The navigation guard already exists for Rapid Fire and Wiki — this slice extends it to Pinpoint and adds the matching backend endpoint.

End-to-end behaviour delivered:

1. **Backend route** — `POST /games/pinpoint/abandon`. Delegates to `PinpointService.abandon(player_id)`.
2. **Service lifecycle** — `abandon` raises `SessionNotFoundException` if no Pinpoint session exists for the player, and `SessionAlreadyCompletedException` if the session is already terminal. Otherwise: any `pinpoint_puzzle_attempt` currently in `status = active` is closed as `failed` with `score = 0` and `time_bonus = NULL`. The session status flips to `abandoned` and `game_sessions.score` is persisted. Puzzles that have no attempt row at all are left untouched in the DB but surfaced in the result as `not_reached`.
3. **Result schema enrichment** — `ResultSchema` gains a `puzzles_not_reached` count and `puzzles[].status` accepts `not_reached`. `not_reached` rows have `clues_used: null`, `score: 0`, `time_bonus: 0`. The result schema must be consistent across `play` (when session is `abandoned`), `guess` (when the abandon was triggered server-side — n/a for this slice), and `abandon` itself.
4. **Frontend navigation guard** — extend the existing navigation-guard mechanism (browser back / popstate / beforeunload) to recognise the Pinpoint route and call `POST /games/pinpoint/abandon` on confirmed abandon. Arms when the Pinpoint session goes `active`; disarms on `completed` or confirmed `abandoned`.
5. **Lobby tile** — the existing `GET /players/me/sessions` integration already drives lobby tile state from `game_sessions.status`. Verify that `abandoned` flips the Pinpoint tile to its locked/abandoned state with no extra wiring needed (the Picture and Rapid Fire tiles are the prior art).
6. **Replay protection** — calling `POST /games/pinpoint/play` after the session is `completed` or `abandoned` returns the result block, never a new puzzle. Calling `POST /games/pinpoint/guess` after a terminal session returns 4xx (e.g. `SessionAlreadyCompletedException`).

## Acceptance criteria

- [x] `POST /games/pinpoint/abandon` exists and is reachable through the proxy
- [x] Abandoning an active session flips `game_sessions.status` to `abandoned`, closes any `active` attempt as `failed` with `score = 0` and `time_bonus = NULL`, and persists the partial `game_sessions.score`
- [x] The result schema returned by abandon includes `puzzles_not_reached` and `not_reached` rows for puzzles with no attempt — those rows have `clues_used: null`, `score: 0`, `time_bonus: 0`
- [x] No response payload from any Pinpoint endpoint contains canonical `answer` or `answer_aliases`, including the abandon result
- [x] `abandon` on a non-existent session returns 4xx (`SessionNotFoundException`); on an already-terminal session returns 4xx (`SessionAlreadyCompletedException`)
- [x] After `abandon`, subsequent `play` calls return the result block (not a new puzzle); subsequent `guess` calls return 4xx
- [x] Frontend navigation guard intercepts back / refresh / unload while a Pinpoint puzzle is active and triggers the abandon flow; the guard disarms cleanly on `completed` or `abandoned`
- [x] Lobby tile for Pinpoint reflects `abandoned` after the flow completes (locked, no re-entry)
- [x] Service tests cover: abandon active mid-puzzle → puzzle `failed` 0pts, session `abandoned`, unattempted puzzles `not_reached`; abandon already-completed → exception; abandon no-session → exception

## Blocked by

Sub-1 — session creation, attempt persistence, and the basic guess loop must exist before abandon can layer on.
