# ADR-0002: Catch-All Next.js Route Handler as FastAPI Proxy

**Status:** Accepted  
**Date:** 2026-05-16

## Context

The browser must call FastAPI endpoints without CORS issues and with the Session Token attached. The token lives in an `httpOnly` cookie (see ADR-0001), so the browser cannot read it and manually add an `Authorization` header.

## Decision

All `/api/*` requests from the browser are handled by a single catch-all Route Handler at `app/api/[...path]/route.ts`. This handler:

1. Reads the `token` httpOnly cookie from the incoming request
2. Constructs an `Authorization: Bearer <token>` header
3. Forwards the request (method, body, other headers) to `http://fastapi:8000/api/<path>`
4. Streams the FastAPI response back to the browser

The login endpoint (`app/api/auth/login/route.ts`) is a separate explicit handler that sets the cookie and is excluded from the catch-all's auth injection logic.

## Consequences

- **FastAPI is unchanged** — no cookie-reading logic added to Python; `Authorization: Bearer` stays as-is
- **Single auth seam** — cookie → header transformation lives in exactly one file; deleting it breaks auth for all game calls
- **Slightly more code than rewrites** — ~50 lines of proxy boilerplate vs zero config lines; justified by the auth injection requirement
- **No `next.config.mjs` rewrites needed** — the catch-all handler replaces them entirely

## Alternatives Rejected

- **`next.config.mjs` rewrites**: zero-code but cannot inject headers from cookies; requires either FastAPI to read JWTs from cookies (changes FastAPI) or middleware header mutation (unsupported for rewrite destinations in Next.js)
- **Per-endpoint Route Handlers**: verbose, requires a new file per FastAPI route; not maintainable
