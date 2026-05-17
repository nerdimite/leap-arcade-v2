# Picture Illustration Game — Full Implementation

## Intent

Player plays a rebus-puzzle game where each puzzle is one image encoding a tech/corporate concept. All seeded puzzles are played within a single global Session Timer (5 min, configurable). Free-text answers are accepted and matched against a pre-normalised list of variations stored in seed data. Per-puzzle scoring (200/150/100/50 by attempt count) plus a time bonus (1 pt per second remaining) compose the final score. Maximum theoretical score is 1300 pts (5 puzzles × 200 + 300 time bonus). The single `POST /games/picture/abandon` endpoint handles both intentional abandon (navigation guard) and timer expiry, ending the session as `completed` in both cases.

## Overall Acceptance Criteria

- `POST /games/picture/play` returns the next unresolved puzzle for new and mid-game players, and the result block for completed players
- `POST /games/picture/answer` evaluates submitted answers via the normalisation pipeline (lowercase, strip punctuation, collapse whitespace), returns wrong feedback without advancing on incorrect attempts, and returns the next puzzle (or inline result on game over) on correct/skip resolution
- `POST /games/picture/abandon` ends the session as `completed`, computes final score with time bonus = 0, and works for both navigation-guard abandon and client-side timer expiry
- Per-puzzle scoring is 200/150/100/50 by attempt count at resolution; skipped/not-reached scores 0
- Time bonus is 1 pt per second remaining at game end; clamped to 0 if session has exceeded `PICTURE_TIME_LIMIT_MS`
- All seeded puzzles are dynamically shuffled per session — no shuffle order is stored, the service picks randomly from unresolved puzzles on each call
- Canonical answers are never revealed to the frontend, even on the result screen
- Session is locked once completed — no replay, no re-entry
- Lobby tile reflects `not_started` / `in_progress` / `completed` via the existing `GET /players/me/sessions` integration
- All e2e API acceptance tests across the happy path, skip, abandon, timer-expiry, normalisation, and resume scenarios pass

## Execution Plan

```
Batch 1 (solo):     Sub-1 (happy-path tracer bullet)
Batch 2 (parallel): Sub-2 (skip) ∥ Sub-3 (timer + abandon + time bonus)
Batch 3 (parallel): Sub-4 (result screen + lobby tile) ∥ Sub-5 (e2e api tests)
```

## References

- PRD: `docs/plans/2026-05-17-picture-illustration-prd.md`
- Domain glossary: `CONTEXT.md` (Picture Illustration, Picture Puzzle, Picture Puzzle Attempt, Session Timer, Picture Session Score)
- Reference implementation pattern: `leap/games/rapid_fire/` (service shape), `leap/api/routes/games/rapid_fire.py` (route layer)
- Example puzzle images: `docs/games-examples/picture-illustration/` (3 of 5 puzzles)
- Image asset destination: `frontend/public/games/picture/`
- Entry points: `POST /games/picture/play`, `POST /games/picture/answer`, `POST /games/picture/abandon`
