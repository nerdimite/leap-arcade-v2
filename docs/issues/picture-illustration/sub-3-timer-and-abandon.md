# Sub-3: Global Session Timer + Abandon + Time Bonus

**Type:** AFK
**Status:** ready-for-agent
**Depends on:** Sub-1
**Blocks:** Sub-4, Sub-5

## Parent

`docs/issues/picture-illustration/parent.md`

## What to build

Introduce the global Session Timer — a single 5-minute countdown that runs across the entire Picture Illustration session. The timer is the speed-scoring mechanism: time remaining at game end produces a 1-pt-per-second bonus added to the accuracy score. Timer expiry ends the game immediately. The same `POST /games/picture/abandon` endpoint also handles intentional player abandon (navigation guard) — both paths end the session as `completed`.

End-to-end behaviour delivered:

1. **Configuration** — `PICTURE_TIME_LIMIT_MS = 300_000` added to `leap/config/constants.py` (or wherever game-specific timing constants live, alongside any Rapid Fire equivalents).
2. **Scoring module** — add `compute_time_bonus(started_at, ended_at, time_limit_ms)` returning the integer time bonus (1 pt per whole second remaining; 0 if the session has already exceeded the time limit). Add `compute_total_score` that combines accuracy score + time bonus.
3. **Service** — `submit_answer` on the resolution of the final puzzle now computes the final score as `accuracy_score + time_bonus`, where `time_bonus` is computed from `session.started_at` to `now`, clamped to the `time_limit_ms` budget. The service also enforces the time limit on the server side: if a submit arrives after the budget has elapsed, the answer is recorded but `time_bonus` is 0 and the session is closed as `completed` with whatever has been resolved so far (remaining puzzles get `not_reached`).
4. **Abandon endpoint** — `POST /games/picture/abandon`:
   - 404 `SessionNotFoundException` when no session exists for this player
   - 409 `SessionAlreadyCompletedException` when session is already `completed`
   - On success, marks session `completed` (NOT `abandoned`), computes final score from resolved puzzles only (time bonus = 0 since the player ran out of time or quit early), persists score on `game_sessions.score`, returns `AbandonResponse { result }`
   - Same endpoint is called by both the navigation guard AND the client-side timer-expiry handler — the server does not distinguish
5. **Result schema enrichment** — `ResultSchema` now also includes `accuracy_score`, `time_bonus`, `time_remaining_seconds`. Per-puzzle items in `result.puzzles` may now include status `not_reached` for puzzles that were never resolved before time ran out / abandon.
6. **Frontend** — `SessionTimer` component:
   - Always visible in the game header during active play
   - Starts from `time_limit_ms` (received from `play` response, OR the constant — define this at implementation time; recommend the response carries the absolute `session_started_at` so the client can compute time remaining authoritatively across refreshes)
   - Turns red and pulses when remaining time is under 60s
   - When countdown reaches 0, calls `POST /games/picture/abandon`, awaits the result, and renders the result screen
7. **Navigation guard** — arms when the picture session enters `active` (mirrors the pattern from Rapid Fire's `setIsDirty(true)` / `setIsDirty(false)`). On nav-away or beforeunload, the guard intercepts and calls `POST /games/picture/abandon` before allowing navigation. Disarms on `completed`.
8. **Resume handling** — on `play` for a mid-game session, the `play` response includes `session_started_at` so the client can rebuild the SessionTimer with the correct remaining time. If the server detects the session has already exceeded the time limit at `play` time, it ends the session immediately and returns the result block.

## Acceptance criteria

- [ ] `PICTURE_TIME_LIMIT_MS` constant exists and defaults to `300_000`
- [ ] `compute_time_bonus` returns floor of seconds remaining; clamped to 0 when elapsed exceeds time limit
- [ ] `submit_answer` on the final puzzle resolution stores `score = accuracy_score + time_bonus` on `game_sessions.score`
- [ ] `POST /games/picture/abandon` ends an active session as `completed`, persists score with time bonus = 0, returns the result block
- [ ] `POST /games/picture/abandon` on a completed session returns 409
- [ ] `POST /games/picture/abandon` with no session returns 404
- [ ] `play` response for an active session carries `session_started_at` (or equivalent) sufficient for the client to compute remaining time after a page refresh
- [ ] If the server receives a `submit_answer` after the time limit has elapsed, the session is closed as `completed` with `time_bonus=0`; the response is the result block
- [ ] Frontend `SessionTimer` renders the countdown, transitions to red+pulse under 60s, and triggers `/abandon` on reaching zero
- [ ] Frontend navigation guard arms on session start and calls `/abandon` on nav-away / beforeunload, then permits navigation
- [ ] On a page refresh during an active session, the timer correctly resumes with the remaining time (computed server-side, not from local state)
- [ ] `ResultSchema` exposes `accuracy_score`, `time_bonus`, and `time_remaining_seconds` separately from `score`
- [ ] Per-puzzle entries in `result.puzzles` include the `not_reached` status for puzzles never resolved
- [ ] Service-level unit tests cover: time bonus computation; submit-after-expiry behaviour; abandon; abandon-then-replay returns 409

## Blocked by

Sub-1 — the answer endpoint, session lifecycle, and frontend shell must exist before timer + abandon layer can hook into them.
