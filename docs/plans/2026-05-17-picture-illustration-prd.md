# Picture Illustration — Full Implementation PRD

---

## Problem Statement

The LEAP platform has four mini-games to offer players during the one-day corporate event. Picture Illustration is the third game to be implemented. Currently, only a frontend route stub and a constants/migration stub exist — there is no playable game. Players who navigate to the Picture Illustration tile on the Lobby encounter a placeholder page and cannot participate.

---

## Solution

Implement Picture Illustration end-to-end: a rebus-puzzle game where the player is shown one image at a time and must type the tech/corporate concept it visually encodes. All puzzles are played within a single 5-minute global Session Timer. The faster and more accurately the player decodes each puzzle, the higher their final score. The game is fully server-authoritative: session state, answer validation, and scoring are owned by the backend.

---

## User Stories

1. As a player, I want to start a Picture Illustration session from the Lobby, so that my game session is created and I am shown the first puzzle immediately.
2. As a player, I want to see one image at a time, so that I can focus on decoding each concept without distraction.
3. As a player, I want to type my answer freely, so that the game feels like a genuine decode challenge rather than a process-of-elimination MCQ.
4. As a player, I want immediate feedback when my answer is wrong, so that I know to try again without leaving the current puzzle.
5. As a player, I want the input field to clear automatically after a wrong answer, so that I can type my next attempt without extra effort.
6. As a player, I want to be able to skip a puzzle I cannot solve, so that I am not stuck indefinitely on a hard rebus.
7. As a player, I want the skip action to be a single tap with no confirmation dialog, so that the global timer is not wasted on friction.
8. As a player, I want to see the global countdown timer at all times during play, so that I am always aware of my remaining time budget.
9. As a player, I want the timer to turn red and pulse when under 60 seconds, so that I get a clear urgency signal before time runs out.
10. As a player, I want the game to end immediately when the timer reaches zero, so that the outcome is fair and the experience is clean.
11. As a player, I want each session to present the puzzles in a shuffled order, so that the game feels fresh and I cannot predict the sequence from watching others play.
12. As a player, I want to earn more points for solving a puzzle on my first attempt than on later attempts, so that careful thinking is rewarded over trial and error.
13. As a player, I want a time bonus added to my score based on how much time I have left at game end, so that solving puzzles quickly is meaningfully rewarded.
14. As a player, I want to be shown a result screen after the game ends, so that I can see my total score and a per-puzzle correct/wrong breakdown.
15. As a player, I want the result screen to show the time bonus I earned separately from the accuracy score, so that I understand exactly how my score was built.
16. As a player, I want the result screen to not reveal the canonical answers to puzzles I missed, so that correct players cannot share answers mid-event.
17. As a player, I want a "Back to Lobby" button on the result screen, so that I can return and check the leaderboard.
18. As a player, I want my Picture Illustration session to be locked once completed, so that I cannot replay the game and inflate my score.
19. As a player, I want the Lobby game tile for Picture Illustration to reflect my session status (not started / in progress / completed), so that I can see my progress at a glance.
20. As a player, I want to resume an in-progress session if I navigate away and return, so that an accidental navigation does not forfeit my score silently.
21. As a player who navigates away mid-game, I want the navigation guard to intercept the action and end my session cleanly, so that the game records a completed state rather than leaving an orphaned active session.
22. As a player, I want answers like "NLP", "nlp", "Natural Language Processing", and "Natural Language Models" to all be accepted for the same puzzle, so that legitimate variations of the correct concept are not penalised.
23. As a player, I want punctuation like hyphens and dots to be ignored when my answer is matched, so that "Hugging-Face" and "Hugging Face" are treated the same.
24. As a player, I want extra spaces in my typed answer to be ignored, so that accidental whitespace does not cause a correct answer to be marked wrong.
25. As an event organiser, I want puzzle images to be served directly from the frontend's static asset path, so that no additional infrastructure is needed for image hosting.
26. As an event organiser, I want the global time limit to be configurable via a backend constant, so that the event team can tune difficulty without a code change.
27. As an event organiser, I want accepted answer variants to be stored in seed data, so that the puzzle content team can maintain them without touching application logic.

---

## Implementation Decisions

### Scoring Model

- **Per-puzzle accuracy score:**
  - Correct on 1st attempt: 200 pts
  - Correct on 2nd attempt: 150 pts
  - Correct on 3rd attempt: 100 pts
  - Correct on 4th+ attempt: 50 pts
  - Skipped, timed out, or not reached: 0 pts
- **Time bonus:** 1 pt per second remaining on the Session Timer at game end (max 300 pts for a 5-minute timer).
- **Maximum score:** 1 300 pts (5 puzzles × 200 + 300 time bonus). Theoretical ceiling; unreachable in practice.
- **No negative marking.** Wrong attempts lower the per-puzzle ceiling but never subtract from the running total.

### Session Timer

- Configured via `PICTURE_TIME_LIMIT_MS` (default `300_000`).
- The server stores `game_session.started_at`; time remaining is computed as `time_limit_ms − (now − started_at)`.
- When the client countdown reaches zero it calls `POST /games/picture/abandon`, which ends the game immediately. Remaining unresolved puzzles score 0. The session status is set to `completed` (not `abandoned`), since timer expiry is a natural game-end condition, not a forfeit.
- The navigation guard also calls the same `abandon` endpoint; result is identical.

### Puzzle Progression

- All seeded Picture Puzzles are played in a single session — no fixed-count constant.
- Order is dynamically shuffled: on each `play` or correct/skip advance, the service picks randomly from the pool of unresolved puzzles (those with no `correct` or `skipped` attempt row for this session). No shuffle order is stored.
- Sessions are keyed on `(player_id, game_id)` — one session per player per game, consistent with the platform's Game Session contract.

### Answer Normalisation

Applied to both the submitted answer and (at comparison time) to each entry in `accepted_answers`:

```
normalize(s):
  s = s.lower()
  s = remove all non-alphanumeric-non-space characters  (hyphens, dots, etc.)
  s = collapse consecutive whitespace to single space
  s = strip leading/trailing whitespace
```

All accepted variations must be listed explicitly in seed data. There is no fuzzy or edit-distance matching in application code.

### Image Storage

Puzzle images live in the frontend's public directory under `games/picture/`. Seed data stores the filename only (e.g. `"huggingface.png"`); the service returns this value and the frontend constructs the URL as `/games/picture/<filename>`. No FastAPI static mount is required. Seed filenames must be verified to match the assets on disk during implementation.

### DB Schema

Two new tables:

**`picture_puzzles`** (seed data)
- `id` UUID PK
- `image_filename` TEXT — relative to `frontend/public/games/picture/`
- `canonical_answer` TEXT — for server-side display only; never sent to the frontend during active play
- `accepted_answers` JSONB — pre-normalised lowercase list of all valid answer strings

**`picture_puzzle_attempts`** (one row per submit, including wrong attempts)
- `id` UUID PK
- `session_id` TEXT FK → `game_sessions.id`
- `puzzle_id` TEXT FK → `picture_puzzles.id`
- `submitted_answer` TEXT nullable (null = skip)
- `correct` BOOLEAN
- `skipped` BOOLEAN
- `created_at` TIMESTAMPTZ

Score per puzzle is computed at resolution time from the attempt count; it is not stored per attempt. Final session score is stored on `game_sessions.score` when the session ends, consistent with all other games.

### API Contract

```
POST /games/picture/play
  → 200 PlayResponse { status, game_session_id?, puzzles_answered?, puzzles_total?, puzzle?, result? }

POST /games/picture/answer
  body: { puzzle_id: str, submitted_answer: str | null }   (null = skip)
  → 200 AnswerResponse {
      correct: bool,
      skipped: bool,
      score_earned: int,          # 0 on wrong; populated on correct/skip resolution
      current_score: int,
      puzzles_solved: int,
      puzzles_remaining: int,
      next_puzzle: PuzzleSchema | null,   # null when wrong (stay on puzzle) or game over
      result: ResultSchema | null         # populated only on game-over
    }

POST /games/picture/abandon
  → 200 AbandonResponse { result: ResultSchema }
```

`PuzzleSchema` sent to the frontend contains: `id`, `image_filename`, `puzzles_answered`, `puzzles_total`. It does **not** contain `canonical_answer` or `accepted_answers`.

`ResultSchema` contains: `score`, `accuracy_score`, `time_bonus`, `time_remaining_seconds`, `puzzles` (list of `{ puzzle_id, image_filename, status: correct|skipped|not_reached, score_earned }`). Canonical answers are not included.

### Module Breakdown

- **`scoring.py`** — pure functions: `normalize_answer`, `score_per_puzzle`, `compute_time_bonus`, `compute_total_score`. No I/O; deepest testable unit.
- **`PictureService`** — session lifecycle: `play`, `submit_answer`, `abandon`. Warms a puzzle cache from DB at startup (same pattern as `RapidFireService`). Owns normalisation, matching, score computation, and timer-expiry enforcement (server clamps time_remaining to 0 if session has already exceeded `time_limit_ms`).
- **`PicturePuzzleDAO`** — read-only; `get_all` used for cache warm. Stubs `_to_orm` / `_apply_filters` with `raise NotImplementedError` per AGENTS.md rule.
- **`PicturePuzzleAttemptDAO`** — `create`, `get_all_for_session`, `get_resolved_puzzle_ids`.
- **ORM models** — `PicturePuzzleModel`, `PicturePuzzleAttemptModel`.
- **Types** — `PicturePuzzleDTO`, `PicturePuzzleAttemptDTO`, `PictureResultDTO`, `PicturePlayPayload`, `PictureAnswerPayload`.
- **Routes + schema** — three route handlers delegating entirely to `PictureService`; route-layer mapping functions mirror the Rapid Fire pattern.
- **Seed data** — `picture.json` with 5 puzzles; each entry includes `image_filename`, `canonical_answer`, `accepted_answers` (pre-normalised lowercase).
- **Alembic migration** — adds both new tables.
- **Frontend** — replaces the stub `page.tsx` with a game shell; `PuzzleView`, `SessionTimer`, `ResultView` components; typed API client wrappers; image assets in `public/games/picture/`.

---

## Testing Decisions

Good tests for this game test **external behaviour** — what the service returns given specific sequences of calls — not internal implementation details like cache internals or private helper methods. Tests should use hand-written fakes (not `MagicMock`) per project convention.

### Modules to test

**`scoring.py` — unit tests (highest priority)**
- `normalize_answer`: covers lowercase, hyphen removal, dot removal, whitespace collapse, leading/trailing strip.
- `score_per_puzzle`: covers attempt counts 1–4+ for correct answers, and skipped/not-reached → 0.
- `compute_time_bonus`: covers full time remaining, zero remaining, negative remaining (clamped to 0).
- `compute_total_score`: integration of per-puzzle scores + time bonus.

**`PictureService` — service-level acceptance tests with hand-written DAO fakes**
- `play` with no existing session → creates session, returns first puzzle.
- `play` with active session → returns next unresolved puzzle.
- `play` with completed session → returns result block.
- `submit_answer` correct first attempt → 200 pts, returns next puzzle.
- `submit_answer` correct second attempt → 150 pts.
- `submit_answer` wrong → `correct=false`, `next_puzzle=null`, stays on same puzzle.
- `submit_answer` skip (null) → `skipped=true`, advances to next puzzle, 0 pts.
- `submit_answer` on final puzzle (correct) → `result` block inline, session completed.
- `submit_answer` when session already completed → `SessionAlreadyCompletedException`.
- `submit_answer` with unknown `puzzle_id` → `InvalidPuzzleIdException`.
- `abandon` with active session → session completed, partial score.
- `abandon` with no session → `SessionNotFoundException`.
- `abandon` with already-completed session → `SessionAlreadyCompletedException`.
- Timer already expired at submit time → server clamps `time_remaining_ms` to 0, time bonus = 0.

**Prior art:** `backend/tests/unit/services/test_rapid_fire_service.py` (same pattern, same fake DAO style).

### DAO and route tests

DAO tests that require real SQL execution are integration tests — mark with `# TODO: integration test` per AGENTS.md. Route-layer behaviour (HTTP status codes, 422 validation) is covered by e2e API tests in `tests/e2e/`.

---

## Out of Scope

- Hint system (no hints of any kind during active play).
- Canonical answer reveal on the result screen (deliberately excluded to prevent answer sharing).
- Admin tooling for puzzle management.
- Progressive image reveal (all images shown in full immediately).
- Multiple image sets per puzzle (one image per puzzle).
- Any game logic for Wikipedia Speed Run, Four Pics One Lie, or Crossword.

---

## Further Notes

- The game ID is `"picture"` — already present in `leap/config/constants.py` and the initial Alembic migration's `game_id` CHECK constraint.
- `PICTURE_TIME_LIMIT_MS` joins `PICTURE_*` constants; keep it alongside any other game-specific configurable values.
- The Meridian design doc (`docs/design/picture.meridian.yaml`) should be authored before implementation begins, walking the call graph top-down from route → service → DAO → model, consistent with the Rapid Fire design doc pattern.
- Seed data accepted answers for the three example puzzles: `huggingface.png` → `["hugging face", "huggingface"]`; `large_language_model.png` → `["large language model", "llm", "large language models"]`; `nlp.png` → `["nlp", "natural language processing", "natural language models"]`. The remaining two puzzles need content before implementation.
