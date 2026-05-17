# Four Pics, One Lie — Full Implementation PRD

---

## Problem Statement

The LEAP platform lists Four Pics, One Lie as one of its five mini-games, but the game does not exist beyond a frontend route stub and a constants/migration entry. Players who reach the Four Pics tile on the Lobby encounter a placeholder page and cannot play. No backend routes, services, DAOs, DB tables, seed data, or frontend components exist for this game.

---

## Solution

Implement Four Pics, One Lie end-to-end: a visual odd-one-out game where each question shows four images and the player must identify the single image that does not belong to the same category as the other three — with no text prompt or category hint. Every seeded question is played in a randomised order per session. Speed is rewarded via a per-question time bonus that decays from the moment the question is served. One tap per question: a correct tap earns base + time bonus; a wrong tap earns zero and the question advances automatically. The game is fully server-authoritative; images are served from the frontend's static asset path.

---

## User Stories

1. As a player, I want to start a Four Pics session from the Lobby tile, so that my game session is created and the first question is shown immediately.
2. As a player, I want to see four images laid out in a 2×2 grid, so that I can scan all options at once.
3. As a player, I want no category hint or text prompt, so that finding the odd one out is a genuine visual deduction challenge.
4. As a player, I want to tap one image to submit my answer, so that the interaction is a single deliberate action with no confirm step.
5. As a player, I want immediate visual feedback — a green overlay for correct, a red overlay for wrong — so that I know the outcome instantly.
6. As a player, I want the overlay to show my score breakdown (`+100 base + 42 bonus = 142 pts`) on a correct tap, so that the time bonus feels tangible and rewarding.
7. As a player, I want the overlay to show `+0 pts` on a wrong tap without revealing which image was correct, so that the answer remains secret and players cannot share it mid-event.
8. As a player, I want the overlay to auto-dismiss after 2 seconds and advance to the next question, so that the game keeps moving without requiring extra taps.
9. As a player, I want a per-question stopwatch displayed during play, so that I can see time ticking and understand the time-bonus pressure.
10. As a player, I want the stopwatch to resume from the server's recorded start time if I refresh the page, so that refreshing cannot reset my timer and gain extra bonus.
11. As a player, I want questions presented in a random order unique to my session, so that I cannot receive answers from another player in the room.
12. As a player, I want every seeded question to be played within my session, so that my final score is comparable to all other players.
13. As a player, I want a result screen after the final question, showing my total score and a per-question row (correct/wrong, score, time bonus), so that I understand exactly how I performed.
14. As a player, I want the result screen to not reveal which image was correct for wrong answers, so that the mystery is preserved.
15. As a player, I want a "Back to Lobby" button on the result screen, so that I can return and check the leaderboard.
16. As a player, I want my Four Pics session to be locked once completed or abandoned, so that I cannot replay and inflate my score.
17. As a player, I want the Lobby tile to reflect my session status (not started / in progress / completed / abandoned), so that I can see my progress at a glance.
18. As a player, I want to resume an in-progress question if I navigate away and return, so that an accidental navigation does not forfeit progress silently.
19. As a player who navigates away mid-game, I want the navigation guard to intercept the action and abandon my session cleanly, so that the partial score is recorded and the session is not left orphaned.
20. As an event organiser, I want the question pool to be defined entirely in seed JSON, so that the content team can add or edit questions without touching code.
21. As an event organiser, I want puzzle images to be served directly from the frontend's static asset path, so that no additional image hosting infrastructure is needed.
22. As an event organiser, I want the time-bonus decay parameters to live in backend constants, so that they are reviewable but not casually editable.
23. As an event organiser, I want the API to never send `odd_one_out_index` to the client, so that a player cannot inspect network traffic to cheat.

---

## Implementation Decisions

### Scoring Model

- **Base score per correct answer:** `FOUR_PICS_BASE_SCORE = 100`
- **Per-question time bonus** (added to base, only on correct):

  ```
  time_bonus = max(0, floor(FOUR_PICS_TIME_BONUS_MAX * (1 − elapsed_ms / FOUR_PICS_TIME_DECAY_MS)))
  ```

  with `FOUR_PICS_TIME_BONUS_MAX = 50` and `FOUR_PICS_TIME_DECAY_MS = 30_000`.
- **Maximum per question:** 150 pts (100 base + 50 bonus at instant tap).
- **Wrong answer:** 0 pts. No negative marking. No second attempt — the question advances immediately.
- **Final session score:** sum of per-question scores.
- **No hard cap:** total max score is `N × 150` where N equals the number of seeded questions. `GAME_MAX_POINTS["four_pics"]` in the frontend is kept as-is for backward compat only (will be removed in a future lobby redesign); do not rely on it.

### Question Mechanic

- Each question holds exactly 4 image paths and 1 `odd_one_out_index` (0-based integer, 0–3).
- The player taps one of the four images. The selection is submitted as `selected_index` (0–3).
- The server compares `selected_index == odd_one_out_index` to determine correctness.
- One attempt per question — there is no partial state, no retry, no skip.
- `odd_one_out_index` is never included in any API response.
- The stopwatch starts when the question is first served (`question_started_at`). It is server-authoritative and never resets.
- `time_ms` submitted by the client is clamped server-side to `min(time_ms, now − started_at)` to prevent cheating.
- There is no per-question hard timeout: the stopwatch runs indefinitely. The time bonus simply floors at 0 after 30 seconds.

### Question Progression

- All seeded questions are played in a single session — no fixed count constant.
- Order is randomised: on each `play` call the service picks uniformly at random from the pool of unattempted questions for this session (those without a `four_pics_question_attempt` row in a terminal status).
- Sessions are keyed on `(player_id, game_id)` per the platform's `game_sessions` unique constraint.
- `POST /play` is idempotent: if an `active` attempt already exists for this session, the same question is returned (same `question_id`, same `started_at`).

### Image Storage

- Images live in the **frontend** at `frontend/public/images/four-pics/<question_slug>/1.png` through `4.png` (or equivalent filenames chosen by the content team). Next.js serves them as static assets.
- The DB seed row stores the four paths as a JSONB array in `image_paths`, e.g.:

  ```json
  {
    "image_paths": [
      "/images/four-pics/wearables/1.png",
      "/images/four-pics/wearables/2.png",
      "/images/four-pics/wearables/3.png",
      "/images/four-pics/wearables/4.png"
    ],
    "odd_one_out_index": 2
  }
  ```

- `image_paths[odd_one_out_index]` is the lie. Indices are 0-based. Content authors control image ordering; there is no server-side shuffling of the paths array.

### DB Schema

Two new tables.

**`four_pics_questions`** (seed data; one row per question)

- `id` UUID PK
- `image_paths` JSONB NOT NULL — array of exactly 4 path strings
- `odd_one_out_index` SMALLINT NOT NULL CHECK (0–3) — server-side only; never sent to client

**`four_pics_question_attempts`** (one row per (session, question) when first served)

- `id` UUID PK
- `session_id` TEXT FK → `game_sessions.id`
- `question_id` UUID FK → `four_pics_questions.id`
- `status` TEXT NOT NULL CHECK in (`active`, `correct`, `wrong`)
- `selected_index` SMALLINT NULL — null while active; 0–3 once answered
- `score` INT NULL — populated on terminal status (`correct` → base + time_bonus; `wrong` → 0)
- `time_bonus` INT NULL — populated on `correct` only
- `time_ms` INT NULL — client-measured elapsed time submitted with answer
- `started_at` TIMESTAMPTZ NOT NULL — server-set when question is first served; never reset
- `completed_at` TIMESTAMPTZ NULL
- UNIQUE `(session_id, question_id)` — one attempt per question per session

Final session score is stored on `game_sessions.score` when the session ends, consistent with all other games.

### Game Registry

`four_pics` is already present in `GAMES` in `leap/config/constants.py` and the `game_id` CHECK constraint on `game_sessions`. No changes to the registry or existing migration are needed.

### API Contract

```
POST /games/four-pics/play
  → 200 PlayResponse {
      session_status: "active" | "completed" | "abandoned",
      session_score: int,
      question: QuestionState | null,    # null when session is terminal
      result: ResultSchema | null        # populated when session is terminal
    }

POST /games/four-pics/answer
  body: { question_id: UUID, selected_index: int (0–3), time_ms: int }
  → 200 AnswerResponse {
      correct: bool,
      score: int,           # pts earned for this question (base + time_bonus or 0)
      time_bonus: int,      # 0 on wrong
      session_status: "active" | "completed",
      session_score: int,
      question: QuestionState | null,    # next question; null when final question answered
      result: ResultSchema | null        # populated only when final question was just answered
    }

POST /games/four-pics/abandon
  → 200 AbandonResponse { result: ResultSchema }
```

`QuestionState`:

```
{
  question_id: UUID,
  question_number: int,     # 1-indexed position in this session's play order
  total_questions: int,     # total seeded questions
  image_paths: List[str],   # exactly 4 paths; odd_one_out_index NOT included
  status: "active"
}
```

`ResultSchema`:

```
{
  score: int,
  questions_correct: int,
  questions_wrong: int,
  questions_not_reached: int,    # nonzero only on abandon
  questions: List[{
    question_id: UUID,
    status: "correct" | "wrong" | "not_reached",
    score: int,
    time_bonus: int
  }]
}
```

`PlayResponse` is **idempotent**: repeated calls with no intervening answer return the same `QuestionState` (same `question_id`, same `started_at`). The first call after a terminal question (correct or wrong) advances to the next random unattempted question.

### State Transitions

`four_pics_question_attempt.status`:

- `active` (initial, set when question is first served) → `correct` on a matching tap
- `active` → `wrong` on a non-matching tap
- Both `correct` and `wrong` are terminal — no retry

`game_sessions.status` for Four Pics:

- `active` → `completed` when the final unattempted question reaches a terminal status (either `correct` or `wrong`)
- `active` → `abandoned` on `POST /abandon`. Any currently-`active` question attempt is closed with `status = wrong`, `score = 0`. Unattempted questions produce `status = not_reached` rows in the result.

### Module Breakdown

- **`leap/games/four_pics/scoring.py`** — pure functions: `compute_time_bonus(elapsed_ms) → int`, `compute_question_score(correct: bool, elapsed_ms: int) → tuple[int, int]` (returns `(score, time_bonus)`). No I/O — deepest testable unit.
- **`leap/games/four_pics/service.py`** — `FourPicsService` owns session lifecycle: `play`, `submit_answer`, `abandon`. Warms a question cache from DB at startup (mirrors `RapidFireService`). Responsible for: random selection of next unattempted question, `selected_index` validation, server-side `time_ms` clamping, score computation, terminal-state transitions, session completion. Owns the session via `async with self.ctx.session() as session`.
- **`leap/dao/four_pics_question_dao.py`** — read-only; `get_all` for cache warm. Stubs `_to_orm` / `_apply_filters` with `raise NotImplementedError` per AGENTS.md rule.
- **`leap/dao/four_pics_question_attempt_dao.py`** — `create`, `get_active_for_session`, `get_all_for_session`, `update_status_and_score`.
- **ORM models** — `FourPicsQuestionModel`, `FourPicsQuestionAttemptModel` in `leap/dao/models/`, registered in `leap/dao/models/__init__.py`.
- **Types** (`leap/types/four_pics.py`) — `FourPicsQuestionDTO`, `FourPicsQuestionAttemptDTO`, `FourPicsQuestionStateDTO`, `FourPicsResultDTO`, `FourPicsAnswerPayload`.
- **API schema** (`leap/api/schema/four_pics.py`) — request/response Pydantic models per the API Contract above.
- **API routes** (`leap/api/routes/games/four_pics.py`) — three handlers; each delegates to `FourPicsService` and maps DTOs to API schemas. Mounted at prefix `/games/four-pics` in `leap/api/main.py`.
- **ServiceContainer** — wires `FourPicsService` alongside other game services; `initialize(session)` called in lifespan.
- **Seed data** (`leap/seeds/data/four_pics.json`) — flat array; each entry: `{ image_paths: [...], odd_one_out_index: int }`. Seed loader is idempotent (`ON CONFLICT DO NOTHING`) per platform contract.
- **Alembic migration** — adds both new tables. No change to `game_id` CHECK constraint (already includes `four_pics`).
- **Frontend** — replaces the placeholder at `app/(games)/four-pics/page.tsx`. Components: `FourPicsGame` shell, `ImageGrid` (2×2 grid), `AnswerOverlay` (2s correct/wrong popup with score breakdown), `Stopwatch`, `ResultView`. Typed API client wrappers in `lib/api/four-pics.ts`. React Query hooks for `play`, `answer`, `abandon`. Wired into the existing navigation guard.
- **Player session aggregation** — `GET /players/me/sessions` already keys on `game_id`; `four_pics` sessions surface automatically once the seed and service are wired. No new endpoints needed.

### Constants

In `leap/games/four_pics/scoring.py`:

- `FOUR_PICS_BASE_SCORE = 100`
- `FOUR_PICS_TIME_BONUS_MAX = 50`
- `FOUR_PICS_TIME_DECAY_MS = 30_000`

### Frontend UX Decisions

- Four images displayed in a **2×2 grid**, equal-sized, tappable/clickable.
- No category prompt, no hint text — the images speak for themselves.
- Tapping an image immediately locks input and submits to `POST /answer`.
- **Correct overlay:** 2s green overlay on top of the tapped image (or full grid), showing `+{base} base + {time_bonus} bonus = {total} pts`. Auto-dismisses and advances.
- **Wrong overlay:** 2s red overlay showing `+0 pts`. The correct image is **not** highlighted. Auto-dismisses and advances.
- The per-question stopwatch is rendered client-side, initialised from `question_started_at` returned by `POST /play`/`POST /answer`. It provides live visual decay but score is always computed server-side.
- Result screen: total score, per-question rows showing question number / correct or wrong / score / time bonus. No answer images shown on result screen.
- `GAME_MAX_POINTS["four_pics"]` in the frontend is left unchanged (backward compat placeholder); it is not displayed on the lobby tile in a meaningful way and will be removed in a subsequent lobby redesign pass.

---

## Testing Decisions

Tests target **external behaviour** — what the service returns for given sequences of calls — not internal helpers. Hand-written DAO fakes (not `MagicMock`) per project convention. DAO tests requiring real SQL are integration tests — mark with a TODO per AGENTS.md.

### `scoring.py` — unit tests (highest priority)

- `compute_time_bonus`: `0ms → 50`, `15_000ms → 25`, `30_000ms → 0`, `45_000ms → 0` (clamped). Boundary at exactly 30_000 is 0.
- `compute_question_score` correct at `0ms → (150, 50)`, at `15_000ms → (125, 25)`, at `30_000ms → (100, 0)`, at `45_000ms → (100, 0)`.
- `compute_question_score` wrong at any elapsed → `(0, 0)`.

### `FourPicsService` — service-level acceptance tests with hand-written DAO fakes

- `play` with no existing session → creates session, returns first random question with `status = active`.
- `play` with active question → returns the same question idempotently (same `question_id`, same `started_at`).
- `play` after terminal question → returns next random unattempted question.
- `play` after the final question is answered → returns `question: null` and a populated `result`.
- `submit_answer` correct → status `correct`, `score = base + time_bonus`, next question in response.
- `submit_answer` wrong → status `wrong`, `score = 0`, `time_bonus = 0`, next question in response.
- `submit_answer` correct on final question → session `completed`, `result` populated, `question: null`.
- `submit_answer` wrong on final question → session `completed`, `result` populated, `question: null`.
- `submit_answer` when attempt already terminal → `QuestionAlreadyAnsweredException`.
- `submit_answer` with `question_id` not matching the session's active attempt → `InvalidQuestionIdException`.
- `submit_answer` with `selected_index` out of range 0–3 → rejected at schema layer (422).
- `abandon` with active session → session `abandoned`, active attempt closed as `wrong` with score 0, unattempted surface as `not_reached` in result.
- `abandon` with completed session → `SessionAlreadyCompletedException`.
- `abandon` with no session → `SessionNotFoundException`.
- Time bonus integration: a correct tap at simulated `elapsed_ms = 15_000` returns `time_bonus = 25`. Service uses an injectable clock so tests can advance time deterministically.

**Prior art:** `backend/tests/unit/services/test_rapid_fire_service.py` (same fake-DAO style, same session-lifecycle assertions).

### E2E tests

Add a Four Pics journey to `backend/tests/e2e/`:

- **`test_four_pics_journey.py`** — full-pool playthrough: login → start → answer all questions (mix of correct/wrong) → assert final session score equals expected sum, assert lobby tile flips to `completed`, assert leaderboard reflects the score.
- **`test_four_pics_lifecycle_journeys.py`** — abandon mid-session and confirm partial score is recorded; refresh mid-question and confirm `play` returns the same `question_id` and `started_at`.

### Frontend tests

- Reducer / hook tests for the Four Pics client state machine.
- API client wrapper tests (`lib/api/four-pics.test.ts`) following the Rapid Fire/Pinpoint pattern.
- Navigation guard abandon behaviour mirrors existing tests — extend or add a parallel file.

---

## Out of Scope

- Any category hint, text prompt, or visual grouping cue shown to the player.
- Revealing the correct image on wrong answer, on result screen, or anywhere.
- Multiple attempts per question or retry mechanics.
- Per-question hard timeout (stopwatch is unbounded; bonus floors at 0 after 30 s).
- Negative scoring for wrong answers.
- Skip functionality — the player must tap an image to proceed.
- Difficulty mode selection (obvious / tricky / expert from the original brief) — difficulty is baked into the image set by the content team and is not surfaced as a UI mode.
- Admin tooling for question authoring or live question editing.
- Any logic for Wikipedia Speed Run, Picture Illustration, Pinpoint, or Crossword.

---

## Further Notes

- The `four_pics` game id is already in `GAMES` and the `game_id` CHECK constraint — no registry changes needed. The Alembic migration only needs to create the two new tables.
- `odd_one_out_index` must never appear in any Pydantic response schema or be serialised into any API response. Defensive: add an explicit `model_config` exclusion on the DTO or use a separate `FourPicsQuestionPublicDTO` that omits the field.
- The injectable clock pattern used in Wiki and Pinpoint time-bonus tests should be reused here so that `compute_time_bonus` and service-level time-bonus assertions are deterministic.
- The sample question lives at `docs/games-examples/Fourpics/round 1/` (four images; `3.png` is the odd one out — not a wearable). Copy/move images to `frontend/public/images/four-pics/wearables/` when authoring the production seed.
- A Meridian design YAML (`docs/design/four-pics.meridian.yaml`) should be authored before implementation, walking the call graph top-down route → service → DAO → model, mirroring the Rapid Fire and Picture Illustration design docs.
- Route prefix is `/games/four-pics` (kebab-case) consistent with `/games/rapid-fire` and `/games/wiki` in `main.py`. The frontend route is `app/(games)/four-pics/` which already exists as a stub.
