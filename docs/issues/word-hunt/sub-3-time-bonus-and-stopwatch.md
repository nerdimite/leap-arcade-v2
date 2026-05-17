# Sub-3: Time Bonus and Stopwatch

**Type:** AFK
**Status:** ready-for-agent
**Depends on:** Sub-1
**Blocks:** Sub-5 (e2e tests assert on time-bonus values)

## Parent

`docs/issues/word-hunt/parent.md`

## What to build

Layer the session-wide time bonus onto Sub-1's barebones scoring, plus the live stopwatch on the frontend. Adds the time-bonus contribution to every terminal path (auto-complete, explicit submit). Runs in parallel with Sub-2 and Sub-4.

End-to-end behaviour delivered:

1. **Scoring module additions** (`leap/games/word_hunt/scoring.py`) — add `WORD_HUNT_TIME_BONUS_MAX = 500` and `WORD_HUNT_TIME_DECAY_MS = 600_000` constants. Add `compute_time_bonus(elapsed_ms: int) -> int` = `max(0, floor(WORD_HUNT_TIME_BONUS_MAX * (1 - elapsed_ms / WORD_HUNT_TIME_DECAY_MS)))`. Add `compute_final_score(found_count: int, elapsed_ms: int) -> int` = `compute_base_score(found_count) + compute_time_bonus(elapsed_ms)`. Unit tests at boundaries: `0ms → 500`, `300_000ms → 250`, `600_000ms → 0`, `900_000ms → 0`, exact `600_000ms` boundary returns 0.
2. **Injectable clock** — `WordHuntService` takes a clock dependency (function returning current UTC datetime, defaulting to `utc_now`) so service-level time-bonus tests can advance time deterministically. Mirrors the pattern used in Wiki and Pinpoint.
3. **Service: time-bonus integration** — both terminal paths now compute the final score as `compute_final_score(found_count, elapsed_ms)` where `elapsed_ms = (now - game_session.started_at).total_seconds() * 1000`. Auto-complete path inside `submit_find` and explicit `submit` path both use this. `game_sessions.score` stores the combined total.
4. **DTO / schema additions** — `WordHuntResultDTO` and `ResultSchema` gain three fields: `base_score: int`, `time_bonus: int`, `time_elapsed_ms: int`. `WordHuntPuzzleStateDTO` and `PuzzleState` gain `started_at: datetime` (ISO8601 in the API response).
5. **Frontend `Stopwatch` component** — reads `started_at` from the latest `play` response and renders an elapsed `mm:ss` counter that ticks once per second client-side. Source of truth is always the server's `started_at`; refresh does not reset the displayed elapsed time. No "warning" colour change in this slice (kept minimal — server-authoritative).
6. **Frontend score display update** — the inline running score now reflects `session_score` returned by the latest `play` / `find` response (which is still just `found_count × 100` while active — the time bonus is only applied at termination). When the session terminates, the score chip transitions to the final total (base + time bonus); the breakdown is shown on the result screen per Sub-4 (this slice exposes the raw fields in the response — the result-screen redesign is Sub-4's job).

This slice does NOT touch the navigation guard, the polished result screen layout, or any UI polish beyond what's needed for the stopwatch — those are Sub-4 and Sub-2 respectively.

## Acceptance criteria

- [ ] `compute_time_bonus` returns the values listed above at all boundaries; never returns a negative number
- [ ] `compute_final_score` is correct across a representative set of `(found_count, elapsed_ms)` pairs
- [ ] `WordHuntService` accepts an injectable clock; service-level tests using a fake clock can assert `time_bonus` values exactly (e.g. a session that completes at simulated `elapsed_ms = 300_000` returns `time_bonus = 250`)
- [ ] Auto-complete via `submit_find` finalises `game_sessions.score` to `found_count * 100 + time_bonus`
- [ ] Explicit `submit` finalises `game_sessions.score` to `found_count * 100 + time_bonus`
- [ ] `play` response includes `started_at` as ISO8601
- [ ] Result payload (returned by auto-complete `find`, by `submit`, and by `play` on a `completed` session) includes `base_score`, `time_bonus`, `time_elapsed_ms`
- [ ] Frontend renders a live `mm:ss` stopwatch that resumes from the server's `started_at` on refresh
- [ ] Existing Sub-1 happy-path behaviour still works end-to-end

## Blocked by

Sub-1 (the service, route, and DB-backed session must exist).
