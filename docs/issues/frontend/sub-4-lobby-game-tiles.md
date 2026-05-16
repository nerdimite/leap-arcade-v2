# Sub-4: Lobby — game tiles + player session status

**Status:** Done  
**Blocked by:** Sub-1 (backend endpoint), Sub-3 (login auth flow)  
**Blocks:** Sub-5 (Leaderboard)

## Parent

`docs/issues/frontend/parent.md`

## What to build

The Lobby page: a server component shell that fetches the player's session statuses on load, passes them as initial data to a client component, and renders five game tiles. The mini leaderboard sidebar is added in Sub-5 — this slice delivers the tile grid only.

**Service layer**  
- `src/lib/api/players.ts` — typed fetch wrapper for `GET /api/players/me/sessions`
- `src/services/players/schema.ts` — Zod schema for `PlayerSession` (`{ game_id, status, score | null }`) and `PlayerSessionsResponse`
- `src/services/players/hooks.ts` — `usePlayerSessions` React Query hook

**Lobby server component (`app/lobby/page.tsx`)**  
Server component. Fetches player sessions via `GET /api/players/me/sessions` server-side (using the session cookie from the incoming request headers). Wraps the result in a React Query `HydrationBoundary` and passes it as `dehydratedState` to the client component. If the fetch fails (e.g. cookie missing), redirect to `/login`.

**Lobby client component (`app/lobby/_components/LobbyClient.tsx`)**  
Renders five game tiles in a grid. Calls `usePlayerSessions` (which picks up the server-hydrated data). Each tile shows: game name, description, max points available, and status badge. Completed and abandoned tiles are visually locked — clicking them does nothing. Not-started and in-progress tiles link to the game route.

**Game tile static data**  
The five games are static constants (name, description, route, max points) — only status is dynamic. Max points per game comes from a constants file, not the backend.

## Acceptance criteria

- [x] Lobby renders five game tiles with correct name, description, and points for each game
- [x] A tile whose session status is `completed` or `abandoned` is visually distinct and non-clickable
- [x] A tile with no session shows `not started` state
- [x] A tile with `active` session shows `in progress` state
- [x] Page server-fetches sessions; client hydrates without a loading spinner flash
- [x] `PlayerSession` Zod schema parses `{ game_id, status, score: null }` and `{ game_id, status, score: 350 }` correctly
- [x] `usePlayerSessions` test: returns correct session data from msw mock
- [x] Navigating to `/lobby` without a valid cookie redirects to `/login` (covered by `src/proxy.test.ts` auth guard)
