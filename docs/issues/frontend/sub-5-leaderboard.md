# Sub-5: Leaderboard — full page + lobby sidebar

**Status:** Done  
**Blocked by:** —  
**Blocks:** None

## Parent

`docs/issues/frontend/parent.md`

## What to build

Two leaderboard surfaces sharing one service layer: the full `/leaderboard` page and the mini leaderboard sidebar added to the Lobby.

**Service layer**  
- `src/lib/api/leaderboard.ts` — typed fetch wrapper for `GET /api/leaderboard`
- `src/services/leaderboard/schema.ts` — Zod schemas for `LeaderboardEntry` (`{ rank, corp_id, display_name, total_score, games_completed }`) and `LeaderboardResponse`
- `src/services/leaderboard/hooks.ts` — `useLeaderboard` with `refetchInterval: LEADERBOARD_POLL_INTERVAL_MS` (5000ms from constants)

**Full leaderboard page (`app/leaderboard/page.tsx`)**  
Server component shell with initial fetch + `HydrationBoundary`. Client component renders all players in rank order. Columns: rank, name, score, games completed. Tiebreaker (earliest completion) is resolved server-side — the frontend renders the order as received. Polls every 5 seconds via `refetchInterval`.

**Lobby mini leaderboard sidebar**  
Added to `LobbyClient`. Calls `useLeaderboard` (same hook, same poll interval). Renders the top 10 rows. If the current player is not in the top 10, their row is appended below a separator showing their actual rank and score. Current player row is visually highlighted. `corp_id` for highlighting comes from JWT claim `sub`, read on the server from the httpOnly session cookie and passed as `currentCorpId` (see implementation notes).

## Acceptance criteria

- [x] Full leaderboard page shows all players sorted by total score descending
- [x] Full leaderboard polls and re-renders every 5 seconds without a page refresh
- [x] Lobby sidebar shows the top 10 players
- [x] If the current player is outside the top 10, their row is pinned below a separator
- [x] Current player row is visually highlighted in the sidebar
- [x] `LeaderboardEntry` Zod schema parses a valid entry and rejects missing `total_score`
- [x] `useLeaderboard` test: returns ranked list from msw mock; `refetchInterval` is set to `LEADERBOARD_POLL_INTERVAL_MS`
- [x] Leaderboard page server-fetches on initial render; no loading spinner flash

## Implementation notes

- Session cookie is **httpOnly**, so the lobby resolves `corp_id` from JWT `sub` on the **server** (`cookies()` + `decodeJwtSub`) and passes `currentCorpId` into `LobbyClient`. Browser JS never reads the token.
