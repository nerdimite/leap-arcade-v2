# Sub-2: Abandon Endpoint + Navigation Guard

**Type:** AFK
**Status:** done
**Depends on:** Sub-1
**Blocks:** Sub-4

## Parent

`docs/issues/four-pics-one-lie/parent.md`

## What to build

Add the `abandon` endpoint and wire the existing navigation guard so a player who navigates away mid-game has their session cleanly closed with a partial score recorded, mirroring the Rapid Fire and Pinpoint patterns.

End-to-end behaviour delivered:

1. **API** — `POST /games/four-pics/abandon` returning `{ result: ResultSchema }`. Mounted under the existing `/games/four-pics` router.
2. **Service** — `FourPicsService.abandon(player_id)`:
   - With an `active` session: marks the session `abandoned`. If a question attempt is currently `active`, closes it with `status = "wrong"`, `score = 0`, `time_bonus = 0`, `selected_index = null`, `completed_at = now`. Unattempted questions surface in the result with `status = "not_reached"`. Persists final session score on `game_sessions.score`.
   - With an already `completed` or `abandoned` session: raises `SessionAlreadyCompletedException` (or the existing equivalent) → 409.
   - With no session at all: raises `SessionNotFoundException` → 404.
3. **Result schema extension** — `ResultSchema.questions_not_reached` becomes meaningfully nonzero when reached via abandon. `questions: List[{ question_id, status: "correct" | "wrong" | "not_reached", score, time_bonus }]` now includes `not_reached` rows.
4. **Frontend** — wire Four Pics into the existing navigation guard (the same mechanism used by Rapid Fire / Pinpoint via the shared `setIsDirty` / `pushState` / `popstate` / `beforeunload` plumbing). When the guard fires, the client calls `POST /games/four-pics/abandon`, displays the abandon-flavoured result screen briefly, and redirects to the Lobby. The guard arms when the game session becomes `active` and disarms on `completed` / confirmed `abandoned`.
5. **Unit tests** — service-level: abandon-active (active question closed as wrong, unattempted as not_reached), abandon-completed (raises), abandon-no-session (raises). API-route test asserts response shape.

## Acceptance criteria

- [x] `POST /games/four-pics/abandon` with an active session returns `{ result }` where `result.score` is the sum of completed-attempt scores, `result.questions_not_reached` equals the count of unattempted questions, and `result.questions` includes one row per seeded question with the correct status (`correct` / `wrong` / `not_reached`)
- [x] After abandon, the `game_sessions` row is `status = "abandoned"` with `score` set to the final summed score
- [x] If a question attempt was `active` at abandon time, the corresponding row becomes `status = "wrong"`, `score = 0`, `time_bonus = 0`, `selected_index = null`, `completed_at = now`
- [x] `POST /games/four-pics/abandon` on a `completed` or already-`abandoned` session returns 409
- [x] `POST /games/four-pics/abandon` with no Four Pics session for the player returns 404
- [x] Frontend: navigating back, refreshing-then-leaving, or closing the tab mid-game triggers the navigation guard, which calls `abandon` before the navigation completes; on success the player is redirected to the Lobby
- [x] After abandon, the Lobby tile reflects `abandoned` via `GET /players/me/sessions`; the tile is locked and cannot be re-entered
- [x] Service-level unit tests cover all three abandon paths (active / already-terminal / not-found) using hand-written DAO fakes

## Blocked by

Sub-1 — the session, attempt persistence, and route plumbing must exist before abandon can be layered on.
