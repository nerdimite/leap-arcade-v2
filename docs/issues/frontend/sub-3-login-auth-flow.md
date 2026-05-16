# Sub-3: Login page — end-to-end auth flow

**Status:** Done  
**Blocked by:** None  
**Blocks:** Sub-4 (Lobby), Sub-6 (Rapid Fire core)

## Parent

`docs/issues/frontend/parent.md`

## What to build

A complete login flow from form submission to authenticated lobby redirect. Covers the Zod schema, API fetch wrapper, React Query mutation hook, Route Handler that sets the httpOnly cookie, the login page UI, and tests.

**Login Route Handler (`app/api/auth/login/route.ts`)**  
Receives `{ corp_id, event_code }` from the browser. Forwards to `POST http://fastapi:8000/auth/login`. On success, extracts `access_token` from the FastAPI JSON response (`LoginResponse`; OAuth-style, not named `token`) and sets it as an httpOnly cookie named `token` (`SameSite=Strict`, `Path=/`, `HttpOnly`). Returns `{ ok: true }` to the browser. On failure, passes through the FastAPI error status and body. See ADR-0001.

**Service layer**  
- `src/lib/api/auth.ts` — typed fetch wrapper for `POST /api/auth/login`
- `src/services/auth/schema.ts` — Zod schemas for `LoginRequest` and `LoginResponse`
- `src/services/auth/hooks.ts` — `useLoginMutation` (React Query `useMutation`)

**Login page UI (`app/(auth)/login/page.tsx`)**  
Form with corp ID and event code fields. On submit, calls `useLoginMutation`. On success, `router.replace('/lobby')`. On error (401), renders an inline error message ("Invalid corp ID or event code"). No registration link, no "forgot password" — players are pre-seeded.

Also: if `proxy.ts` determines the user is already authenticated when they visit `/login`, redirect them to `/lobby` immediately (already-authenticated redirect).

## Acceptance criteria

- [x] Submitting valid credentials sets the `token` httpOnly cookie and redirects to `/lobby`
- [x] Submitting invalid credentials shows an error message, no redirect
- [x] The `token` cookie is `HttpOnly`, `SameSite=Strict`, `Path=/`
- [x] JWT from FastAPI (`access_token` in the JSON body) is never exposed on the browser-facing JSON — the route returns only `{ ok: true }` while the JWT is copied into the httpOnly `token` cookie
- [x] Authenticated users visiting `/login` are redirected to `/lobby`
- [x] `useLoginMutation` is pending-guarded — submit button is disabled while the request is in flight
- [x] Test: login form calls `useLoginMutation` with correct `corp_id` and `event_code` values
- [x] Test: login form renders error message on `401` response (msw mock)
- [x] `LoginRequest` Zod schema rejects a payload missing `corp_id` or `event_code`
