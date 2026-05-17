# Sub-3: Time Bonus + Stopwatch

**Type:** AFK
**Status:** ready-for-agent
**Depends on:** Sub-1
**Blocks:** Sub-5

## Parent

`docs/issues/pinpoint/parent.md`

## What to build

Add the time-bonus dimension to scoring and surface a live stopwatch in the UI. Sub-1 deliberately ships base-score-only so this slice can land independently and in parallel with Sub-2 / Sub-4.

End-to-end behaviour delivered:

1. **Schema delta** — Alembic migration adds a `time_bonus INT NULL` column to `pinpoint_puzzle_attempts`. Existing rows (none in production yet) backfill to NULL.
2. **Scoring** — extend `leap/games/pinpoint/scoring.py` with a pure function `compute_time_bonus(elapsed_ms)` returning `max(0, floor(100 * (1 - elapsed_ms / 90_000)))`. Constants `PINPOINT_TIME_BONUS_MAX_PTS = 100` and `PINPOINT_TIME_BONUS_DECAY_MS = 90_000` live alongside.
3. **Service** — on a correct guess, compute `elapsed_ms = now - attempt.started_at` (server-authoritative; `now` is sourced from an injectable clock so tests are deterministic), then store `time_bonus` on the attempt and add it to the persisted `score` so `score = base + time_bonus`. The session score sums per-puzzle scores. On `failed` puzzles, `time_bonus` stays NULL and contributes 0.
4. **API contract** — `PuzzleState` adds an optional `time_bonus: int | null` field, populated only when `status == "solved"`. `ResultSchema.puzzles[]` rows include a `time_bonus: int` field (0 when not solved). Backwards-compatible — only adds fields.
5. **Frontend stopwatch** — a small live counter rendered above the badge row, ticking from 00:00 on each new puzzle. Driven by `puzzle.started_at` if exposed, OR by a client-side `Date.now()` reference captured when the puzzle first appears (acceptable since the score is server-authoritative regardless). Resets on each new puzzle.
6. **Result-screen breakdown** — when shown, each puzzle row in the result screen displays `clues_used`, `score` (total), and `time_bonus`, broken down as `<base> + <time_bonus> = <total>`. Failed rows show `0`.
7. **Result-flash overlay enrichment** (if Sub-2 has shipped) — the 2s "Correct" overlay shows `+<base> + <time_bonus> = <total>` instead of just `+<base>`. If Sub-2 has not yet shipped, leave the overlay copy from Sub-1 alone — Sub-2 will pick up the time-bonus copy when it lands.

## Acceptance criteria

- [ ] `time_bonus` column exists on `pinpoint_puzzle_attempts` after migration
- [ ] `compute_time_bonus(0) == 100`; `compute_time_bonus(45_000) == 50`; `compute_time_bonus(90_000) == 0`; `compute_time_bonus(120_000) == 0` (clamped); function is pure and reads no time source
- [ ] On a correct guess, the service stores `time_bonus` on the attempt and persists `score = base + time_bonus`
- [ ] On a failed puzzle, `time_bonus` is NULL on the attempt and contributes 0 to session score
- [ ] `PuzzleState.time_bonus` appears in API responses, populated only when `status == "solved"`
- [ ] `ResultSchema.puzzles[].time_bonus` is present on every row (0 for non-solved)
- [ ] Service tests cover: solve at simulated `elapsed_ms = 30_000` produces `time_bonus = 66`; solve at `elapsed_ms = 120_000` produces `time_bonus = 0` (still earns full base); failed puzzle has `time_bonus = NULL` and contributes 0
- [ ] Service tests use an injectable clock — no direct calls to `datetime.utcnow()` in the production path
- [ ] Stopwatch is visible above the badge row during active play and resets on each new puzzle
- [ ] Result screen renders the per-puzzle `<base> + <time_bonus> = <total>` breakdown for solved rows; failed rows show `0`

## Blocked by

Sub-1 — the puzzle attempt schema, service, and result screen must exist before time-bonus enrichment can layer on.
