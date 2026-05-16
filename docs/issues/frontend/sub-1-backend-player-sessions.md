# Sub-1: Backend — `GET /players/me/sessions` endpoint

**Status:** Done  
**Blocked by:** None — can start immediately  
**Blocks:** Sub-4 (Lobby game tiles)

## Parent

`docs/issues/frontend/parent.md`

## What to build

Add a new endpoint `GET /players/me/sessions` to the backend. It returns all game sessions for the authenticated player as a list of `{ game_id, status, score }` objects. The Lobby server component calls this to determine which game tiles are locked, in-progress, or untouched.

The endpoint follows the existing backend pattern: route → service method → DAO query. The player identity comes from the JWT via the existing `get_current_player` dependency — no new auth logic needed. Returns an empty list (not 404) if the player has no sessions yet.

This is a backend-only change — no frontend work in this slice.

## Acceptance criteria

- [x] `GET /players/me/sessions` returns `200` with a list of `{ game_id, status, score }` for the authenticated player
- [x] Returns an empty list when the player has no game sessions yet
- [x] `score` is `null` while a session is `active`
- [x] Returns `401` when the JWT is missing or invalid
- [x] All five game IDs can appear in the response if the player has played all games
- [x] Unit test covers the happy path (sessions returned) and the empty case
