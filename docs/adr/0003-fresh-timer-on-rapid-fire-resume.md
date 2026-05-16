# ADR-0003: Fresh Per-Question Timer on Page Refresh (Rapid Fire)

**Status:** Accepted  
**Date:** 2026-05-16

## Context

When a player refreshes mid-game in Rapid Fire, the session is resumed via `POST /play` which returns the next unanswered question. The per-question countdown timer (rendered client-side from `time_limit_ms`) needs a start reference. The backend has no record of when a specific question was displayed — only the session's `started_at` exists server-side.

## Decision

On page refresh, the per-question timer resets to the full `time_limit_ms` for the resumed question. No `sessionStorage` or server-side timestamp is used to reconstruct elapsed per-question time.

## Consequences

- **Timer exploit possible**: a player could refresh to reset a question's countdown. Accepted — this is a one-day intern event on a LAN VM; the exploit requires deliberate effort and the scoring impact (50–100 pts per question) is not worth the complexity to prevent
- **Implementation stays simple**: no `sessionStorage` reads/writes on the hot path; no server-side per-question timestamp column
- **`time_ms` is still clamped server-side**: even with a fresh timer, `time_ms` is bounded to `max(500, min(time_ms, time_limit_ms))` on the server — no infinite-time exploit

## Alternatives Rejected

- **`sessionStorage` tracking**: write `{ questionId, shownAt }` on question display; restore elapsed time on resume. Prevents the refresh exploit but adds complexity for a threat model that doesn't justify it
- **Server-side per-question timestamp**: add a `shown_at` column to `rapid_fire_answers` or a separate table. Over-engineered; changes the backend data model for a client-display concern
