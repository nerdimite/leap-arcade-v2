# Four Pics, One Lie — Full Implementation

**Status:** done

## Intent

Player plays a visual odd-one-out game where each question shows four images and the player taps the single image that does not belong to the same category as the other three — with no text prompt or category hint. Every seeded question is played in a randomised order per session. Speed is rewarded via a per-question time bonus that decays from the moment the question is served (`max(0, ⌊50 × (1 − ms / 30_000)⌋)`) on top of a 100-pt base score for a correct tap. Wrong taps earn 0 pts with no answer reveal. One tap per question — no retry, no skip — and the question advances automatically after a 2-second result overlay. The game is fully server-authoritative: question state, selection validation, and scoring are owned by the backend; images are served as static assets from the frontend.

## Overall Acceptance Criteria

- [x] `POST /games/four-pics/play` returns the next unattempted question for new and mid-game players (idempotent for a given active attempt), and the result block for completed players
- [x] `POST /games/four-pics/answer` validates `selected_index` (0–3), records the attempt with server-clamped `time_ms`, computes `score` (base + time bonus on correct, 0 on wrong), and returns the next question inline (or the result block on the final question)
- [x] `POST /games/four-pics/abandon` ends the session as `abandoned`, closes any active attempt as `wrong` with score 0, and surfaces unattempted questions as `not_reached` in the result
- [x] Per-question scoring is `100 + max(0, ⌊50 × (1 − ms / 30_000)⌋)` on correct, `0` on wrong; final session score is the sum of per-question scores
- [x] All seeded questions are dynamically shuffled per session — no shuffle order is stored; the service picks uniformly at random from unattempted questions on each `play` advance
- [x] `odd_one_out_index` is never included in any API response (defensive: enforced by API schema, not relying on serializer omission)
- [x] The per-question stopwatch is server-authoritative — `started_at` is set when the question is first served and never reset; refreshes resume from the server timestamp
- [x] Session is locked once `completed` or `abandoned` — no replay, no re-entry
- [x] Lobby tile reflects `not_started` / `in_progress` / `completed` / `abandoned` via the existing `GET /players/me/sessions` integration
- [x] Frontend `(games)/four-pics/page.tsx` no longer renders the placeholder; player can play through the full game with a polished overlay UX, live stopwatch, and result screen
- [x] All e2e API journey and lifecycle tests pass

## Execution Plan

```
Batch 1 (solo):     Sub-1 (happy-path tracer bullet) ✓
Batch 2 (parallel): Sub-2 (abandon + navigation guard) ✓ ∥ Sub-3 (overlay + stopwatch + result polish) ✓
Batch 3 (solo):     Sub-4 (e2e API tests) ✓
```

Batch 2 issues are disjoint: Sub-2 lives mostly in the backend (`abandon` route + service + nav-guard wiring at the shared game shell level), while Sub-3 lives entirely in the Four Pics frontend components. Sub-4 lands last because its lifecycle journey test asserts the abandon flow shipped in Sub-2.

## References

- PRD: `docs/plans/2026-05-17-four-pics-one-lie-prd.md`
- Domain glossary: `CONTEXT.md` (will gain Four Pics terms during Sub-1)
- Reference implementation pattern: `leap/games/rapid_fire/` (service + cache shape), `leap/api/routes/games/rapid_fire.py` (route layer), `docs/issues/picture-illustration/` (slice cadence)
- Example question images: `docs/games-examples/Fourpics/round 1/` (4 images; `3.png` is the odd one out — not a wearable)
- Image asset destination: `frontend/public/images/four-pics/<question_slug>/`
- Entry points: `POST /games/four-pics/play`, `POST /games/four-pics/answer`, `POST /games/four-pics/abandon`
