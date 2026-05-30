# Sub-3: Time Bonus and Stopwatch

**Type:** AFK
**Status:** todo
**Depends on:** Sub-1
**Blocks:** Sub-5 (e2e tests assert on time-bonus values)

## Parent

`docs/issues/crossword/parent.md`

## What to build

Layer the session-wide time bonus onto Sub-1's barebones scoring, plus the live stopwatch on the frontend. Adds the time-bonus contribution to every terminal path (auto-complete via `check`, explicit `submit`). Runs in parallel with Sub-2 and Sub-4.

End-to-end behaviour delivered:

1. **Scoring module additions** (`leap/games/crossword/scoring.py`) — add `CROSSWORD_TIME_BONUS_MAX = 500` and `CROSSWORD_TIME_DECAY_MS = 600_000`. Add `compute_time_bonus(elapsed_ms: int) -> int` = `max(0, floor(CROSSWORD_TIME_BONUS_MAX * (1 - elapsed_ms / CROSSWORD_TIME_DECAY_MS)))`. Add `compute_final_score(solved_count: int, elapsed_ms: int) -> int` = `compute_base_score(solved_count) + compute_time_bonus(elapsed_ms)`. Unit tests at boundaries: `0ms → 500`, `300_000ms → 250`, `600_000ms → 0`, `900_000ms → 0`, exact `600_000ms` boundary returns 0.
2. **Injectable clock** — `CrosswordService` takes a clock dependency (function returning current UTC datetime, defaulting to `utc_now`) so service-level time-bonus tests can advance time deterministically. Mirrors the pattern used in Word Hunt / Wiki / Pinpoint.
3. **Service: time-bonus integration** — both terminal paths now compute the final score as `compute_final_score(solved_count, elapsed_ms)` where `elapsed_ms = (now - game_session.started_at).total_seconds() * 1000`. The auto-complete path inside `submit_check` and the explicit `submit` path both use this. `game_sessions.score` stores the combined total.
4. **DTO / schema additions** — `CrosswordResultDTO` and `ResultSchema` gain three fields: `base_score: int`, `time_bonus: int`, `time_elapsed_ms: int`. `CrosswordPuzzleStateDTO` and `PuzzleState` gain `started_at: datetime` (ISO8601 in the API response).
5. **Frontend `Stopwatch` component** — reads `started_at` from the latest `play` response and renders an elapsed `mm:ss` counter that ticks once per second client-side. Source of truth is always the server's `started_at`; a refresh does not reset the displayed elapsed time. No warning-colour change (kept minimal — server-authoritative, no hard timeout).
6. **Frontend score display update** — the inline running score reflects `session_score` from the latest `play` / `check` response (still just `solved_count × 100` while active — the time bonus only applies at termination). When the session terminates, the score transitions to the final total (base + time bonus); the breakdown is shown on the result screen per Sub-4 (this slice exposes the raw fields in the response — the result-screen redesign is Sub-4's job).

This slice does NOT touch the navigation guard, the polished result-screen layout, or any UI polish beyond the stopwatch — those are Sub-4 and Sub-2.

## Technical nuances (must get right)

- **Time bonus is terminal-only.** While the session is `active`, `session_score` is exactly `solved_count × 100` — the time bonus is NOT folded into the running score. It is computed once, at the moment of termination, from the server's `started_at`. Do not show a decaying running total.
- **Server-authoritative elapsed time.** `elapsed_ms` is always `now − game_sessions.started_at` on the server. The client stopwatch is display-only and must resume from the server's `started_at` after a refresh (never reset to 0).
- **Injectable clock everywhere time is read.** Both the auto-complete branch inside `submit_check` and `submit` must read `now` through the injected clock so e2e/service tests can assert exact bonus values (e.g. `elapsed_ms = 300_000 → time_bonus = 250`).
- **Floor + clamp.** `compute_time_bonus` uses `floor` and clamps at 0 — it never returns a negative number, and the exact `600_000ms` boundary returns 0 (not 1).

## Acceptance criteria

- [ ] `compute_time_bonus` returns the listed boundary values; never negative
- [ ] `compute_final_score` is correct across a representative set of `(solved_count, elapsed_ms)` pairs
- [ ] `CrosswordService` accepts an injectable clock; service tests using a fake clock assert `time_bonus` exactly (session completing at simulated `elapsed_ms = 300_000` → `time_bonus = 250`)
- [ ] Auto-complete via `submit_check` finalises `game_sessions.score` to `solved_count * 100 + time_bonus`
- [ ] Explicit `submit` finalises `game_sessions.score` to `solved_count * 100 + time_bonus`
- [ ] `play` response includes `started_at` as ISO8601
- [ ] Result payload (from auto-complete `check`, from `submit`, and from `play` on a `completed` session) includes `base_score`, `time_bonus`, `time_elapsed_ms`
- [ ] While `active`, `session_score` equals `solved_count * 100` (no decaying running total)
- [ ] Frontend renders a live `mm:ss` stopwatch that resumes from the server's `started_at` on refresh
- [ ] Existing Sub-1 happy-path behaviour still works end-to-end

## Blocked by

Sub-1 (the service, route, and DB-backed session must exist).
