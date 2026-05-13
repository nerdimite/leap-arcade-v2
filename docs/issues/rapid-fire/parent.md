# Rapid Fire Game — Full Implementation

## Intent

Player plays a 15-question time-based MCQ quiz. Server is the source of truth for session state. A single `POST /games/rapid-fire/play` endpoint handles new game, resume, and completed-game result. `POST /games/rapid-fire/answer` records each submission and returns the next question inline. `POST /games/rapid-fire/abandon` forfeits the session with a partial result.

## Overall Acceptance Criteria

- `POST /play` returns an active question for new and mid-game players, and a result block for completed/abandoned players
- `POST /answer` correctly evaluates answers, computes time-based score (50–100 per correct), advances to next question, and closes the session with an inline result on the last question
- `POST /abandon` returns the partial result and marks the session abandoned
- All 15 real questions load from seed at startup; question cache is populated in `RapidFireService._questions` before the first request
- No question is served twice in the same session; replay of the same `question_id` returns 409
- `correct_option_index` is **1-indexed** throughout: DB, seed data, and service comparison all align on this convention
- No negative marks — wrong and skipped answers both score 0
- All unit acceptance tests across all layers pass

## Execution Plan

```
Batch 1 (parallel): Sub-1 (model + migration), Sub-2 (seed data)
Batch 2 (after Batch 1): Sub-3 (types + DAOs + scoring)
Batch 3 (after Batch 2): Sub-4 (service + container)
Batch 4 (after Batch 3): Sub-5 (routes + schemas)
```

## References

- Design spec: `docs/design/rapid-fire.meridian.yaml`
- Real question bank (raw format): `docs/rapid-fire.json`
- Entry points: `POST /games/rapid-fire/play`, `POST /games/rapid-fire/answer`, `POST /games/rapid-fire/abandon`
- Routes stub: `leap/api/routes/games/rapid_fire.py`
