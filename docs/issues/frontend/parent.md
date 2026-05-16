# Frontend: Login, Lobby, Rapid Fire, Leaderboard

**Status:** Done

## What to build

Full frontend for the in-scope LEAP screens: Login, Lobby, Rapid Fire game, and Leaderboard. Includes a new backend endpoint (`GET /players/me/sessions`) required by the Lobby, and a complete frontend service layer (typed fetch wrappers, Zod schemas, React Query hooks) before any UI is built on top.

**PRD:** `docs/plans/2026-05-16-frontend-prd.md`

## Execution plan

```
Batch A — parallel, no blockers
  Sub-1: Backend /players/me/sessions endpoint
  Sub-2: Frontend infra (proxy.ts + catch-all Route Handler + Vitest setup)

Batch B — needs Sub-2
  Sub-3: Login page (end-to-end auth flow)

Batch C — parallel; Sub-4 needs Sub-1 + Sub-3; Sub-6 needs Sub-2 + Sub-3
  Sub-4: Lobby game tiles + player session status
  Sub-6: Rapid Fire core play loop

Batch D — parallel; Sub-5 needs Sub-4; Sub-7 needs Sub-6
  Sub-5: Leaderboard (full page + lobby sidebar)
  Sub-7: Rapid Fire abandon + navigation guard + timer expiry
```

## Overall acceptance criteria

- [x] Player can log in with corp ID + event code and land on the Lobby
- [x] Lobby shows all five game tiles with correct status (not started / in progress / completed / abandoned)
- [x] Lobby sidebar shows top 10 players + current player's rank, updating every 5 seconds
- [x] Player can start Rapid Fire, answer all 15 questions, and see a result screen
- [x] Rapid Fire question timer counts down and auto-submits a skip on expiry
- [x] Rapid Fire feedback phase shows correct/wrong and auto-advances after 1.5s
- [x] Navigating away mid-game shows a warning and calls `/abandon` on confirm
- [x] Full leaderboard page shows all players with 5s polling
- [x] `proxy.ts` redirects unauthenticated requests to `/login`
- [x] All catch-all proxy requests carry `Authorization: Bearer` from httpOnly cookie
- [x] Reducer state transitions, Zod schemas, and API fetch wrappers are covered by Vitest tests
