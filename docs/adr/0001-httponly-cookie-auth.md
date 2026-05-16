# ADR-0001: httpOnly Cookie for Session Token, Set by Next.js

**Status:** Accepted  
**Date:** 2026-05-16

## Context

The backend issues a JWT on login (returned in JSON response body). The frontend needs to store this token and attach it to every subsequent API request. The platform runs on a LAN VM with no external exposure, but security defaults should still be correct.

## Decision

The Session Token is stored as an `httpOnly` cookie set by the Next.js login Route Handler — not by FastAPI, and not in `localStorage` or `sessionStorage`.

Flow:
1. Browser POSTs credentials to `app/api/auth/login/route.ts`
2. Next.js Route Handler calls FastAPI, receives `{ token: "..." }`
3. Route Handler sets `Set-Cookie: token=<jwt>; HttpOnly; Path=/; SameSite=Strict` on the browser response
4. Browser attaches the cookie automatically to all subsequent same-origin requests

## Consequences

- **FastAPI unchanged** — still reads `Authorization: Bearer` from headers; the Proxy Route Handler injects this header from the cookie on every forwarded call
- **XSS cannot read the token** — `httpOnly` prevents JavaScript access
- **Next.js `proxy.ts` can read the cookie** for auth guard redirects without a round-trip to FastAPI
- **FastAPI does not set cookies** — FastAPI remains a pure API server; cookie mechanics are a frontend concern

## Alternatives Rejected

- **`localStorage`**: simpler but XSS-readable; wrong default even on a LAN VM
- **FastAPI sets the cookie**: couples cookie mechanics to the Python service; requires CORS headers for the Set-Cookie to work across origins before the proxy is in place
