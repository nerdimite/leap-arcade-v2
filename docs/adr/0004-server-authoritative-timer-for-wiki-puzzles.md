# ADR-0004 — Server-Authoritative Timer for Wiki Puzzle Attempts

**Date:** 2026-05-17  
**Status:** Accepted

## Context

ADR-0003 accepted that the Rapid Fire question timer resets on page refresh, because the server stores no per-question `started_at` timestamp. Exploiting this by refreshing is tolerated given the LAN/corporate event threat model.

Wikipedia Speed Run puzzles have a different shape: each puzzle can take up to 3 minutes, and the `wiki_puzzle_attempts` table stores a `started_at` timestamp at the moment the clue is shown (which is when the timer begins). This makes it possible — at no extra cost — to enforce the remaining time on the server.

## Decision

Wiki puzzle timers are **server-authoritative**.

- `started_at` is written to `wiki_puzzle_attempts` when the `play` endpoint creates the attempt row (i.e., when the clue screen loads).
- On resume (`POST /games/wiki/play` for an in-progress session), the response includes `time_remaining_ms = max(0, time_limit_ms − (now − started_at))`. The client initialises its countdown from this value, not from `time_limit_ms`.
- If `time_remaining_ms == 0` on `play`, the server auto-advances the timed-out puzzle (scores 0) and returns the next puzzle state.
- When a player completes a puzzle via `navigate`, the server computes `time_ms = now() − started_at` for scoring. The client does not send `time_ms`.

## Consequences

- Refreshing the page does **not** reset the wiki puzzle timer, unlike Rapid Fire.
- The refresh-to-extend-time exploit present in Rapid Fire (accepted by ADR-0003) is closed for wiki puzzles.
- The client timer may drift slightly from the server's elapsed time over a long session; this is cosmetic only — scoring and timeout enforcement use the server's `started_at`.
