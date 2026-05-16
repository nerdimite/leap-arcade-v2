# PRD: LEAP Frontend — Login, Lobby, Rapid Fire, Leaderboard

**Date:** 2026-05-16  
**Status:** Ready for implementation

---

## Problem Statement

The LEAP backend is complete and covered by unit and e2e tests. The frontend has route stubs only — no real UI, no API wiring, no auth flow. Players have no way to log in, play Rapid Fire, or see the leaderboard. The platform cannot be used until the frontend is built.

---

## Solution

Build the complete frontend for the in-scope screens: Login, Lobby, Rapid Fire game, and Leaderboard. Wire every screen to the backend via a Next.js catch-all Route Handler proxy that injects the player's Session Token from an httpOnly cookie. Establish a testable service layer (typed fetch wrappers + React Query hooks + Zod schemas) and a tested Rapid Fire game reducer before building the UI on top.

---

## User Stories

1. As a player, I want to enter my corp ID and event code on a login screen, so that I can authenticate and access the platform.
2. As a player, I want to be redirected to the lobby automatically after successful login, so that I don't have to navigate manually.
3. As a player, I want an invalid corp ID or event code to show a clear error message on the login screen, so that I know what went wrong.
4. As a player, I want my session to persist across page refreshes, so that I don't have to log in again during the event.
5. As an unauthenticated user, I want any protected route to redirect me to the login page, so that I cannot access game content without logging in.
6. As a player, I want to see five game tiles on the lobby, each showing the game name, description, and available points, so that I can decide which game to play next.
7. As a player, I want each game tile to reflect my current status (not started / in progress / completed / abandoned), so that I know what I've already played.
8. As a player, I want completed and abandoned game tiles to be visually locked, so that I cannot accidentally re-enter a finished game.
9. As a player, I want to see a mini leaderboard in the lobby sidebar showing the top 10 players and my own rank, so that I can track my position during the event.
10. As a player, I want the mini leaderboard to update every 5 seconds without a page refresh, so that I see live score changes as other players complete games.
11. As a player, I want to click a game tile to start that game, so that I can begin playing.
12. As a player, I want to start Rapid Fire and immediately see the first question, so that I can begin answering without delay.
13. As a player, I want to see the question text, four answer options, a countdown timer, my current score, and my progress (e.g. question 3 of 15) during a Rapid Fire session, so that I have all the context I need to play.
14. As a player, I want the countdown timer to start after a brief get-ready pause, so that I'm not caught off-guard by the timer on the first render.
15. As a player, I want clicking an answer option to immediately lock all options and submit my answer, so that I cannot change my mind after selecting.
16. As a player, I want to see feedback after each answer showing whether I was correct, what the right answer was, and my updated score, so that I can learn as I play.
17. As a player, I want the game to auto-advance to the next question after the feedback phase ends, so that I don't have to tap "Next" manually.
18. As a player, I want the countdown timer to auto-submit a skip if I don't answer in time, so that the game keeps moving even if I freeze.
19. As a player, I want my progress to be preserved if I accidentally refresh the page, so that I resume on the next unanswered question without losing my session.
20. As a player, I want the per-question timer to restart at its full duration when I resume after a refresh, so that I have a fair shot at the resumed question.
21. As a player, I want a warning dialog if I try to navigate away mid-game, so that I understand I will receive only a partial score if I leave.
22. As a player, I want my partial score to be recorded if I confirm navigation away mid-game, so that my progress is not silently discarded.
23. As a player, I want to see my final score, correct count, wrong count, skipped count, and time taken at the end of Rapid Fire, so that I understand how I performed.
24. As a player, I want a "Back to Lobby" button on the result screen, so that I can return and play other games.
25. As a player, I want the completed Rapid Fire tile in the lobby to show my score, so that I can see my result at a glance.
26. As a player, I want to view a full leaderboard page showing all players ranked by total score, so that I can see the complete standings.
27. As a player, I want the full leaderboard to update every 5 seconds, so that I see score changes in real time.
28. As a player, I want ties broken by earliest completion time on the leaderboard, so that the ranking is always deterministic.
29. As a facilitator, I want the platform to work correctly across all players simultaneously on a LAN VM, so that the event runs without issues.

---

## Implementation Decisions

### Backend addition: `GET /players/me/sessions`

A new endpoint is needed to support lobby tile status display. It returns all game sessions for the authenticated player: `[{ game_id, status, score }]`. The lobby server component fetches this on render to determine tile states. This endpoint follows the existing pattern: route → service → DAO.

### Auth: httpOnly cookie set by Next.js login Route Handler

The backend returns the JWT in the login response body. A Next.js Route Handler (`POST /api/auth/login`) receives this token, sets an httpOnly cookie (`token`, `SameSite=Strict`, `Path=/`), and returns `{ ok: true }` to the browser. The browser never reads the token directly. See ADR-0001.

### Proxy: catch-all Route Handler

All `/api/*` browser requests are forwarded to FastAPI via a single catch-all Next.js Route Handler. It reads the `token` cookie, adds `Authorization: Bearer <token>`, and streams the request/response through. The Next.js route prefix is stripped before proxying, so `/api/players/me/sessions` in the browser forwards to `http://fastapi:8000/players/me/sessions`. The login Route Handler is the only exception — it handles cookie setting before forwarding. See ADR-0002.

### Auth guard: `proxy.ts`

Next.js 16 uses `proxy.ts` (not `middleware.ts`) with `export function proxy(request: NextRequest)`. The proxy reads the `token` cookie; if absent on any protected route, it redirects to `/login`. Login and static assets are excluded from the matcher.

### Rapid Fire game state machine (`useRapidFireReducer`)

The game client is a pure reducer. The state shape and transitions:

```
States:   idle | loading | question | submitting | feedback | result | error
Actions:  START | PLAY_SUCCESS | PLAY_ERROR
          SUBMIT_ANSWER | ANSWER_SUCCESS | ANSWER_ERROR
          TIMER_EXPIRE | FEEDBACK_COMPLETE
          RESULT_SHOWN
```

Key invariants:
- `submitting` state disables all option buttons (prevents double-submit)
- `TIMER_EXPIRE` dispatches `SUBMIT_ANSWER` with `selected_option: null`
- `FEEDBACK_COMPLETE` fires after the 1.5s feedback phase; transitions to `question` (next question) or `result` (game over)
- The reducer never holds a `setTimeout` reference — timing is managed by hook side-effects watching derived state

### Timing constants

All timing values live in `src/lib/constants.ts`:

```ts
FEEDBACK_DURATION_MS = 1500
QUESTION_START_DELAY_MS = 500
LEADERBOARD_POLL_INTERVAL_MS = 5000
```

### Service layer structure

```
src/lib/api/
  auth.ts       — POST /api/auth/login (no token injection, sets cookie)
  rapid_fire.ts — POST /play, /answer, /abandon
  leaderboard.ts — GET /leaderboard
  players.ts    — GET /players/me/sessions

src/services/
  auth/
    schema.ts   — LoginRequest, LoginResponse (Zod)
    hooks.ts    — useLoginMutation
  rapid_fire/
    schema.ts   — PlayResponse, AnswerRequest, AnswerResponse, AbandonResponse (Zod)
    hooks.ts    — usePlay, useSubmitAnswer, useAbandon
  leaderboard/
    schema.ts   — LeaderboardEntry, LeaderboardResponse (Zod)
    hooks.ts    — useLeaderboard (refetchInterval: LEADERBOARD_POLL_INTERVAL_MS)
  players/
    schema.ts   — PlayerSession (Zod)
    hooks.ts    — usePlayerSessions
```

TypeScript types are derived via `z.infer<>` from Zod schemas — no separate `types/` folder.

### Server vs client component boundary

- `proxy.ts` — auth guard, Node.js runtime
- `app/(auth)/login/page.tsx` — client component (form interaction)
- `app/lobby/page.tsx` — server component shell; fetches player sessions server-side; passes initial data to client `<LobbyClient>` via React Query `HydrationBoundary`
- `app/(games)/rapid-fire/page.tsx` — server component shell; calls `POST /play` server-side to rehydrate session; passes initial state to client `<RapidFireClient>`
- `app/leaderboard/page.tsx` — server component shell; initial leaderboard fetch; passes to client `<LeaderboardClient>`
- All game UIs, timers, answer interactions — client components

### Lobby leaderboard sidebar

Displays top 10 players. If the current player is outside the top 10, their rank is pinned as an additional row at the bottom with a visual separator. Data comes from `useLeaderboard` with 5s polling. The full list (all players) is fetched; the component slices the top 10 and finds the current player's position by `corp_id`.

### Navigation guard and abandon

The `(games)` layout already mounts `NavigationGuardProvider` and `GameNavigationGuardDialog`. Rapid Fire sets `setIsDirty(true)` on session start and `setIsDirty(false)` on completion. On confirmed navigation, the dialog calls `POST /api/games/rapid-fire/abandon` before allowing the route change. There is no explicit abandon button on the game screen.

### Game result display

On the last answer (`next_question: null` in `AnswerResponse`), the reducer transitions to `result` state. The question UI is replaced inline by a result card showing score, correct/wrong/skipped counts, and time taken. A "Back to Lobby" button navigates to `/lobby` (navigation guard is disarmed by this point).

---

## Testing Decisions

**What makes a good frontend test:** tests verify observable behaviour through public interfaces — reducer `(state, action) → state`, schema `parse(input)`, API function response shape — not React internals, not implementation details. A good test survives a component rename or internal refactor.

**Test stack:** Vitest + React Testing Library + msw (Mock Service Worker for fetch interception).

**Modules to test:**

| Module | What to test | How |
|--------|-------------|-----|
| `useRapidFireReducer` | All state transitions: idle→loading, question→submitting→feedback→question, timer expire→submit, last question→result, error states | Vitest pure reducer tests — no rendering needed |
| Zod schemas (`rapid_fire/schema.ts`, `leaderboard/schema.ts`) | Valid API shapes parse correctly; required fields reject when absent; discriminated union branches resolve correctly | Vitest unit tests |
| `src/lib/api/rapid_fire.ts` | Correct URL construction, Authorization header present, request body serialised correctly, error responses throw | Vitest + msw |
| `src/lib/api/auth.ts` | Login sends correct body; 401 surfaces as error | Vitest + msw |
| Login form (`(auth)/login/page.tsx`) | Submit calls mutation with correct values; error state renders error message | RTL |

**Prior art:** backend unit tests (`tests/unit/api/`) use `httpx.AsyncClient` + `ASGITransport` — analogous to msw intercepting fetch at the network boundary. Same principle: test through the HTTP surface, not internal service state.

**Not tested at this stage:** server component rendering, leaderboard polling timer, visual layout, animation timing.

---

## Out of Scope

- Wiki, Picture Illustration, Four Pics One Lie, Crossword game UIs — stubs remain as-is
- Admin facilitator view — stub remains as-is
- Playwright browser-level e2e tests — deferred (aligned with e2e PRD)
- Frontend Docker Compose service — deferred until this PRD is implemented (aligned with e2e PRD)
- Load / performance testing
- Dark mode / theme toggle
- Mobile responsive layout — not a stated requirement for the LAN VM event context

---

## Further Notes

- The `GET /players/me/sessions` backend endpoint is a dependency for the lobby — it must be implemented before or in parallel with the lobby page
- The existing `GameNavigationGuardDialog` and `useNavigationGuard` hooks are complete and should not be modified — Rapid Fire only needs to call `setIsDirty`
- `next.config.mjs` rewrites are NOT used — the catch-all Route Handler replaces them entirely; `next.config.mjs` stays as the empty default
- Bun is the package manager — use `bun add` for new dependencies, `bunx shadcn@latest add` for shadcn components
- All timing constants (`FEEDBACK_DURATION_MS`, `QUESTION_START_DELAY_MS`, `LEADERBOARD_POLL_INTERVAL_MS`) must be sourced from `src/lib/constants.ts` — no magic numbers in components
- Architectural decisions are recorded in `docs/adr/0001`, `0002`, `0003` — do not re-litigate them
