# Server-Authoritative Timeout And Resume

**Status:** done

## Parent

`docs/issues/wikipedia-speed-run/parent.md`

## What to build

Implement the ADR-0004 timer behaviour for Wikipedia Speed Run. Puzzle time must be computed from the server-side `started_at`, refresh must not reset the timer, stale active attempts must auto-timeout on resume, and client timeout events must be corrected by the server.

## Acceptance criteria

- [x] `POST /games/wiki/play` resumes active attempts with `time_remaining_ms = max(0, time_limit_ms - elapsed)`
- [x] Refreshing or re-calling `play` does not reset a Wiki Puzzle Attempt timer
- [x] `play` auto-marks expired active attempts as `timed_out`, scores them 0, and advances to the next puzzle or final result
- [x] `POST /games/wiki/timeout` marks the attempt timed out only when the server timer has actually expired
- [x] Early client timeout events return corrected active puzzle state and remaining time
- [x] Timeout on a non-final puzzle advances to the next puzzle
- [x] Timeout on the fifth puzzle completes the overall game session
- [x] Frontend timer initializes from `time_remaining_ms` and keeps ticking while article navigation loads
- [x] Tests cover resume/no-reset, stale resume auto-timeout, early timeout correction, and final-puzzle timeout completion

## Blocked by

- `docs/issues/wikipedia-speed-run/sub-2-complete-one-puzzle-by-navigation.md`
