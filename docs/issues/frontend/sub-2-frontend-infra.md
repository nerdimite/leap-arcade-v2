# Sub-2: Frontend infra — `proxy.ts` + catch-all Route Handler + Vitest setup

Amended: 2026-05-16 — The catch-all Next.js route stays at `/api/*`, but when forwarding to FastAPI it must strip that browser-only prefix and call the live FastAPI route path directly (for example, `/api/players/me/sessions` -> `http://fastapi:8000/players/me/sessions`).

**Status:** Done  
**Blocked by:** None — can start immediately  
**Blocks:** Sub-3, Sub-4, Sub-5, Sub-6, Sub-7

## Parent

`docs/issues/frontend/parent.md`

## What to build

Lay the foundational infrastructure that every other frontend slice depends on. Three distinct deliverables in one slice:

**1. `proxy.ts` (auth guard)**  
Next.js 16 auth guard at the project root. Reads the `token` httpOnly cookie; redirects unauthenticated requests to `/login`. Protected routes: everything except `/(auth)/login` and static assets (`_next/`, `favicon`). Uses the `matcher` config to scope correctly. See ADR-0001, ADR-0002.

**2. Catch-all Route Handler (`app/api/[...path]/route.ts`)**  
Forwards all `/api/*` browser requests to FastAPI while stripping the browser-only `/api` prefix (for example, `/api/players/me/sessions` -> `http://fastapi:8000/players/me/sessions`). Reads the `token` httpOnly cookie from the incoming request, adds `Authorization: Bearer <token>`, forwards the original method, headers, and body, and streams the FastAPI response back. Returns `401` if the cookie is absent (failsafe — `proxy.ts` should have already redirected, but the Route Handler is the last line). The login path (`/api/auth/login`) is excluded from token injection and handled separately in Sub-3.

**3. `src/lib/constants.ts`**  
All game timing constants in one place:
- `FEEDBACK_DURATION_MS = 1500`
- `QUESTION_START_DELAY_MS = 500`
- `LEADERBOARD_POLL_INTERVAL_MS = 5000`

**4. Vitest + RTL + msw test setup**  
Install and configure Vitest, `@testing-library/react`, `@testing-library/user-event`, and `msw`. Add `vitest.config.ts` and a `src/test/setup.ts` that boots the msw server for all tests. Add a `bun run test` script to `package.json`.

## Acceptance criteria

- [x] `proxy.ts` redirects an unauthenticated request to `/lobby` → `/login`
- [x] `proxy.ts` allows an authenticated request (valid `token` cookie) to pass through
- [x] `proxy.ts` does not run on `_next/static` and `_next/image` paths
- [x] Catch-all Route Handler forwards a GET request to FastAPI with correct `Authorization` header
- [x] Catch-all Route Handler forwards a POST request with body intact
- [x] Catch-all Route Handler returns `401` when `token` cookie is absent
- [x] `FEEDBACK_DURATION_MS`, `QUESTION_START_DELAY_MS`, `LEADERBOARD_POLL_INTERVAL_MS` exported from `src/lib/constants.ts`
- [x] `bun run test` runs Vitest and exits cleanly with a passing smoke-test (e.g. `1 + 1 === 2`)
- [x] msw server is initialised in test setup and intercepts fetch calls
