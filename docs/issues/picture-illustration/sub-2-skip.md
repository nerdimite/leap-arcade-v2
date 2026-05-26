# Sub-2: Skip Support

**Type:** AFK
**Status:** done
**Depends on:** Sub-1
**Blocks:** nothing

## Parent

`docs/issues/picture-illustration/parent.md`

## What to build

Allow the player to skip a puzzle they cannot decode, without ending the game. Skip is the only escape hatch for puzzles the player cannot solve.

End-to-end behaviour delivered:

1. **API contract change** — `submitted_answer` becomes `Optional[str]`. A `null` value is interpreted by the service as a skip.
2. **Service** — `submit_answer` treats `submitted_answer is None` as a skip: creates a `picture_puzzle_attempts` row with `correct=false, skipped=true, submitted_answer=null`, awards 0 pts for that puzzle, advances to the next unresolved puzzle (or the result block if it was the final puzzle).
3. **Schema validation** — explicit `Optional[str]` typing on the request schema; whitespace-only strings are NOT treated as skips (they go through normalisation and almost certainly fail the match — that's correct behaviour).
4. **Frontend** — a secondary "Skip →" button next to the Submit button. No confirmation dialog. Tapping it submits `submitted_answer: null`. Visual treatment de-emphasises Skip relative to Submit (e.g. ghost / outlined button vs filled).

## Acceptance criteria

- [x] `POST /games/picture/answer` with `submitted_answer: null` creates an attempt row with `correct=false, skipped=true, submitted_answer=null`, returns `correct=false`, `score_earned=0`, and advances `next_puzzle` to a different unresolved puzzle
- [x] Skipping the final puzzle returns `next_puzzle=null` and an inline `result` block; session is marked `completed`; `result.score` reflects 0 pts for the skipped puzzle
- [x] A puzzle that has been skipped does not appear again on subsequent `play` or `answer` calls
- [x] Empty string and whitespace-only `submitted_answer` are NOT treated as skips — they go through normalisation and fail the match (returning `correct=false, next_puzzle=null` so the player stays on the puzzle)
- [x] Frontend Skip button is visible alongside Submit during active play; tapping it advances the game without confirmation
- [x] Service-level unit tests cover: skip on first puzzle advances; skip on final puzzle ends game; skipped attempt row has expected shape

## Blocked by

Sub-1 — the answer endpoint, attempt persistence, and frontend shell must exist before skip can be layered on.
