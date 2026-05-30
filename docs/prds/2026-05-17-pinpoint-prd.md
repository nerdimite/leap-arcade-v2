# Pinpoint — Full Implementation PRD

---

## Problem Statement

The LEAP platform has a roster of mini-games for the corporate event. Pinpoint — a word-association puzzle inspired by LinkedIn's daily game — is a planned game with no implementation yet. There is no `pinpoint` entry in the game registry, no backend module, no DB schema, no seed data, and no frontend route. Players cannot encounter the game today, and the seed JSON in `docs/games-examples/pinpoint.json` is the only artefact in the repo.

---

## Solution

Implement Pinpoint end-to-end: a server-authoritative word-association game where each puzzle hides a category behind 5 thematic clue words. The player sees one clue at a time and types a guess; each wrong guess unconditionally reveals the next clue. With at most 5 guesses per puzzle, scoring rewards both fewer clues used and faster solves. The player works through every seeded puzzle in a random order per session. Answer matching is exact-after-normalisation against a curated alias list per puzzle — never fuzzy. The answer is never revealed, even on failure.

---

## User Stories

1. As a player, I want to start a Pinpoint session from the Lobby tile, so that my game session is created and the first puzzle is shown immediately.
2. As a player, I want to see one clue at a time, so that the puzzle has the same "guess from minimal information" feel as LinkedIn Pinpoint.
3. As a player, I want clues to appear in five visible card slots (revealed left-to-right), so that I always know how many clues remain and how many I have used.
4. As a player, I want a free-text input to type my guess, so that the game tests recall rather than process-of-elimination.
5. As a player, I want a wrong guess to immediately reveal the next clue and clear my input, so that I can keep playing without friction.
6. As a player, I want a correct guess to end the puzzle with a brief "Correct" celebration, so that the win feels rewarded.
7. As a player, I want a 5th wrong guess to end the puzzle as failed without revealing the answer, so that the mystery stays intact and answer-sharing during the event is suppressed.
8. As a player, I want the score for each puzzle to depend on how few clues I needed, so that thinking carefully is rewarded over guessing.
9. As a player, I want a time bonus on each puzzle that decays as I take longer, so that quick solves earn more points but slow solves still earn the base clue score.
10. As a player, I want the time bonus to floor at zero (never go negative), so that taking my time on a hard puzzle still gives me a positive score.
11. As a player, I want the puzzle stopwatch to run indefinitely with no hard timeout, so that I can keep thinking without panic and still earn the clue base score.
12. As a player, I want puzzles served in a random order per session, so that the game feels fresh and players cannot share "puzzle 3 is X" across the room.
13. As a player, I want every seeded puzzle played within my session, so that my final score is comparable to other players who also played the full pool.
14. As a player, I want the result screen to show my total score and a per-puzzle breakdown (clues used, time bonus, points), so that I understand exactly how my score was built.
15. As a player, I want the result screen to *not* reveal canonical answers, so that finished players cannot leak puzzles to others still playing.
16. As a player, I want a "Back to Lobby" button on the result screen, so that I can return and check the leaderboard.
17. As a player, I want my Pinpoint session to be locked once completed or abandoned, so that I cannot replay and inflate my score.
18. As a player, I want the Lobby game tile for Pinpoint to reflect my session status (not started / in progress / completed / abandoned), so that I see my progress at a glance.
19. As a player, I want to resume an in-progress puzzle if I refresh the page or navigate back and re-enter, so that an accidental navigation does not forfeit progress silently.
20. As a player who navigates away mid-game, I want the navigation guard to intercept and abandon my session cleanly, so that the partial score is recorded and the session does not stay orphaned.
21. As a player, I want answer matching to be case-insensitive and ignore leading/trailing whitespace, so that `cloud computing`, `Cloud Computing`, and `  CLOUD COMPUTING ` are all accepted.
22. As a player, I want common synonyms and abbreviations to be accepted (e.g. `LLM`, `large language model`, `large language models`), so that the right answer in slightly different phrasing is not punished.
23. As a player, I want my guess history (wrong guesses) to be remembered server-side for the active puzzle, so that I cannot be falsely told I have a guess remaining after a refresh.
24. As an event organiser, I want the puzzle pool to be defined entirely in seed JSON, so that the content team can edit puzzles without touching code.
25. As an event organiser, I want each puzzle's accepted answers to be an explicit list of aliases, so that there is zero ambiguity about what counts as a correct guess.
26. As an event organiser, I want the time-bonus decay parameters to live in code constants, so that they are reviewable but not casually editable.
27. As an event organiser, I want the API to never send the canonical answer to the client, so that a determined player cannot inspect network traffic to cheat.

---

## Implementation Decisions

### Scoring Model

- **Per-puzzle base score (by clues used at moment of correct guess):**
  - 1 clue: 500 pts
  - 2 clues: 400 pts
  - 3 clues: 300 pts
  - 4 clues: 200 pts
  - 5 clues: 100 pts
  - Failed (5th guess wrong): 0 pts
- **Per-puzzle time bonus** (added to base, only on solve):

  ```
  time_bonus = max(0, floor(TIME_BONUS_MAX * (1 - elapsed_ms / TIME_DECAY_MS)))
  ```

  with `TIME_BONUS_MAX = 100` and `TIME_DECAY_MS = 90_000`. Bonus is 0 on failed puzzles.
- **Maximum per puzzle:** 600 pts. **Maximum per session:** 600 × N seeded puzzles.
- **No negative marking.** Wrong guesses lower the per-puzzle ceiling but never subtract from the running total.

### Puzzle Mechanic

- Each puzzle has exactly 5 ordered clue words (`clue1`–`clue5`).
- A puzzle attempt starts with `clues_revealed = 1` (clue1 visible).
- A wrong guess is atomic: it increments `clues_revealed` by 1 and exposes the next clue. The player can never make two guesses while still on the same clue.
- After 5 wrong guesses the puzzle terminates with status `failed`.
- The stopwatch starts when the puzzle is first served (`puzzle_started_at`) and is server-authoritative.
- There is no per-puzzle hard timeout: the stopwatch can run indefinitely. The time bonus simply floors at 0 after 90 seconds.

### Puzzle Progression

- All seeded puzzles are played in a single session — no fixed-count constant, no `session_puzzle_count` config field.
- Order is dynamically randomised: on each `play` advance, the service picks uniformly at random from the pool of unattempted puzzles for this session (those without a `pinpoint_puzzle_attempt` row in a terminal state).
- Sessions are keyed on `(player_id, game_id)` per the platform's `game_sessions` unique constraint.

### Answer Normalisation and Matching

Applied to both the submitted guess and (at comparison time) every entry in `answer_aliases`:

```
normalize(s):
  s = s.strip()
  s = s.lower()
```

A guess is correct iff `normalize(guess) ∈ { normalize(a) : a ∈ {answer} ∪ answer_aliases }`. Aliases must enumerate every accepted phrasing. There is no fuzzy or edit-distance matching in application code. The seed schema requires `answer_aliases` to be present (may be empty if the canonical answer is the only acceptable form).

### Answer Confidentiality

- The canonical `answer` and `answer_aliases` are **never** included in any API response sent to the client — not during play, not on solve, not on failure, not on the result screen.
- The frontend only receives the clues that have been revealed and the puzzle status.

### DB Schema

Two new tables.

**`pinpoint_puzzles`** (seed data; one row per puzzle)

- `id` UUID PK
- `answer` TEXT — canonical answer; server-side only
- `answer_aliases` JSONB — array of accepted alias strings (pre-normalised lowercase recommended; service still normalises defensively)
- `clue1` TEXT, `clue2` TEXT, `clue3` TEXT, `clue4` TEXT, `clue5` TEXT — all NOT NULL

**`pinpoint_puzzle_attempts`** (one row per (session, puzzle) when first served)

- `id` UUID PK
- `session_id` TEXT FK → `game_sessions.id`
- `puzzle_id` UUID FK → `pinpoint_puzzles.id`
- `clues_revealed` SMALLINT NOT NULL — 1..5
- `guesses` JSONB NOT NULL DEFAULT `[]` — array of submitted (raw) wrong guesses
- `status` TEXT NOT NULL CHECK in (`active`, `solved`, `failed`)
- `score` INT NULL — populated on terminal status
- `time_bonus` INT NULL — populated on `solved`
- `started_at` TIMESTAMPTZ NOT NULL
- `completed_at` TIMESTAMPTZ NULL
- UNIQUE `(session_id, puzzle_id)` — one attempt per puzzle per session

Final session score is stored on `game_sessions.score` when the session ends, consistent with all other games.

### Game Registry

- Add `{"id": "pinpoint", "display_name": "Pinpoint"}` to `GAMES` in `leap/config/constants.py`.
- Add `"pinpoint"` to the `game_id` CHECK constraint on `game_sessions` via Alembic migration.

### API Contract

```
POST /games/pinpoint/play
  → 200 PlayResponse {
      session_status: "active" | "completed" | "abandoned",
      session_score: int,
      puzzle: PuzzleState | null,    # null when session is terminal
      result: ResultSchema | null    # populated when session is terminal
    }

POST /games/pinpoint/guess
  body: { puzzle_id: UUID, guess: str }
  → 200 GuessResponse {
      correct: bool,
      puzzle: PuzzleState,           # always returned, with updated clues_revealed/status/score
      session_status: "active" | "completed",
      session_score: int,
      result: ResultSchema | null    # populated only when this guess ended the final puzzle
    }

POST /games/pinpoint/abandon
  → 200 AbandonResponse { result: ResultSchema }
```

`PuzzleState`:

```
{
  puzzle_id: UUID,
  puzzle_number: int,        # 1-indexed position in this session's play order
  total_puzzles: int,        # total seeded puzzles
  clues_revealed: int,       # 1..5
  clues: List[str],          # exactly clues_revealed entries
  status: "active" | "solved" | "failed",
  score: int | null,         # null while active; populated on terminal
  time_bonus: int | null     # null while active or failed; populated on solved
}
```

`ResultSchema`:

```
{
  score: int,                              # session total
  puzzles_solved: int,
  puzzles_failed: int,
  puzzles_not_reached: int,                # only nonzero on abandon
  puzzles: List[{
    puzzle_id: UUID,
    status: "solved" | "failed" | "not_reached",
    clues_used: int | null,
    score: int,
    time_bonus: int
  }]
}
```

`PlayResponse` is **idempotent**: repeated calls with no intervening guess return the same `PuzzleState` (same `puzzle_id`, same `clues_revealed`). The first call after a terminal puzzle advances to the next random unattempted puzzle.

### State Transitions

`pinpoint_puzzle_attempt.status`:

- `active` (initial) → `solved` on a correct guess → puzzle terminal
- `active` → `active` on a wrong guess with `clues_revealed < 5` (clues_revealed += 1, guess appended)
- `active` → `failed` on a wrong guess with `clues_revealed == 5`

`game_sessions.status` for Pinpoint:

- `active` → `completed` when the last unattempted puzzle reaches a terminal status
- `active` → `abandoned` on `POST /abandon`. Any currently-`active` puzzle attempt is closed with `status = failed`, `score = 0`. Unattempted puzzles produce `status = not_reached` rows in the result.

### Module Breakdown

- **`leap/games/pinpoint/scoring.py`** — pure functions: `normalize_answer`, `match_answer(guess, answer, aliases)`, `base_score_for_clues(clues_revealed)`, `compute_time_bonus(elapsed_ms)`. No I/O — deepest testable unit.
- **`leap/games/pinpoint/service.py`** — `PinpointService` owns session lifecycle: `play`, `submit_guess`, `abandon`. Warms a puzzle cache from DB at startup (mirrors `RapidFireService`). Responsible for: random selection of next unattempted puzzle, normalisation and matching, `clues_revealed` increment on wrong guess, score computation, terminal-state transitions. Owns the session via `async with self.ctx.session() as session`.
- **`leap/dao/pinpoint_puzzle_dao.py`** — read-only; `get_all` for cache warm. Stubs `_to_orm` / `_apply_filters` with `raise NotImplementedError` per AGENTS.md rule.
- **`leap/dao/pinpoint_puzzle_attempt_dao.py`** — `create`, `get_for_session`, `get_by_session_and_puzzle`, `update_status_and_score`, `append_guess_and_increment_clues`.
- **ORM models** — `PinpointPuzzleModel`, `PinpointPuzzleAttemptModel` in `leap/dao/models/`, registered in `leap/dao/models/__init__.py`.
- **Types** (`leap/types/pinpoint.py`) — `PinpointPuzzleDTO`, `PinpointPuzzleAttemptDTO`, `PinpointPuzzleStateDTO`, `PinpointResultDTO`, `PinpointPlayPayload`, `PinpointGuessPayload`.
- **API schema** (`leap/api/schema/pinpoint.py`) — request/response Pydantic models per the API Contract above.
- **API routes** (`leap/api/routes/games/pinpoint.py`) — three handlers; each delegates to `PinpointService` and maps DTOs to API schemas. Mounted at prefix `/games/pinpoint` in `leap/api/main.py`.
- **ServiceContainer** — wires `PinpointService` alongside other game services.
- **Seed data** (`leap/seeds/data/pinpoint.json`) — flat array; each entry: `{ answer, answer_aliases, clue1..clue5 }`. Seed loader is idempotent (`ON CONFLICT DO NOTHING` / `DO UPDATE`) per platform contract.
- **Alembic migration** — adds both new tables and extends the `game_sessions.game_id` CHECK constraint to include `"pinpoint"`.
- **Frontend** — replaces the placeholder game route at `app/(games)/pinpoint/`. Components: `PinpointGame` shell, `ClueBadgeRow` (5 badge slots, reveal animation), `GuessInput`, `Stopwatch`, `ResultView`. Typed API client wrappers in `lib/api/pinpoint.ts`. React Query hooks for `play`, `guess`, `abandon`. Wired into the existing navigation guard.
- **Player session aggregation** — `GET /players/me/sessions` and the lobby tile already key on `game_id`; ensure `pinpoint` is reflected once the constant is added. No new endpoints needed.

### Constants

In `leap/games/pinpoint/scoring.py` (or a dedicated `constants.py` if grouping is preferred):

- `PINPOINT_BASE_SCORES = (500, 400, 300, 200, 100)`  # indexed 0..4 for clues_revealed 1..5
- `PINPOINT_TIME_BONUS_MAX_PTS = 100`
- `PINPOINT_TIME_BONUS_DECAY_MS = 90_000`
- `PINPOINT_MAX_CLUES = 5`

### Frontend UX Decisions

- Five horizontally-laid clue badge cards. Greyed/empty initially; reveal left-to-right with a slide+fade animation as `clues_revealed` increments.
- Below the badges: a single text input + "Guess" button. Submit on Enter.
- Wrong guess: brief shake + red flash on the badge that just unlocked, input clears, focus stays on input.
- Correct guess: 2s green overlay showing `+<base> + <time_bonus> = <total>` breakdown, then auto-advances to the next puzzle.
- Failed puzzle (5th wrong): 2s red overlay showing "Out of clues" and `+0`. The answer is **not** displayed. Auto-advances.
- Stopwatch is rendered client-side from `puzzle_started_at` for live display, but the score is always computed server-side from the server's `started_at` at the moment of correct guess.
- Result screen mirrors Rapid Fire's pattern: total score, per-puzzle row showing clues used / status / score / time bonus.

---

## Testing Decisions

Good tests for this game test **external behaviour** — what the service returns given specific sequences of calls — not internal helpers like cache structure or query construction. Tests use hand-written DAO fakes (not `MagicMock`) per project convention. DAO tests that require real SQL execution are integration tests — mark with a TODO comment per AGENTS.md.

### Modules to test

**`scoring.py` — unit tests (highest priority)**

- `normalize_answer`: lowercase, trim, idempotence.
- `match_answer`: matches canonical, matches each alias, rejects clearly wrong, handles whitespace/case variations, treats empty alias list correctly.
- `base_score_for_clues`: `1 → 500`, `2 → 400`, `3 → 300`, `4 → 200`, `5 → 100`. Out-of-range raises.
- `compute_time_bonus`: `0ms → 100`, `45_000ms → 50`, `90_000ms → 0`, `120_000ms → 0` (clamped), boundary at exactly 90_000 is 0.

**`PinpointService` — service-level acceptance tests with hand-written DAO fakes**

- `play` with no existing session → creates session, returns first random puzzle with `clues_revealed = 1`.
- `play` with active puzzle → returns the same puzzle idempotently (same `puzzle_id`, same `clues_revealed`).
- `play` after a solved puzzle → returns next random unattempted puzzle.
- `play` after the final puzzle is solved → returns `puzzle: null` and a populated `result`.
- `submit_guess` correct on clue 1 → status `solved`, base 500 + time bonus, advances on next `play`.
- `submit_guess` wrong on clue 1 → status still `active`, `clues_revealed = 2`, guess appended.
- `submit_guess` wrong 5 times → status `failed`, score 0, no answer in response.
- `submit_guess` correct on clue 5 → status `solved`, base 100 + time bonus.
- `submit_guess` matches an alias → correct.
- `submit_guess` matches with leading/trailing whitespace and mixed case → correct.
- `submit_guess` when puzzle is already terminal → `PuzzleAlreadyResolvedException`.
- `submit_guess` with `puzzle_id` that does not match the session's current active puzzle → `InvalidPuzzleIdException` (prevents skipping ahead via API misuse).
- `abandon` with active session → session `abandoned`, current active puzzle closed as `failed` with score 0, unattempted puzzles surface as `not_reached` in result.
- `abandon` with completed session → `SessionAlreadyCompletedException`.
- `abandon` with no session → `SessionNotFoundException`.
- Time bonus integration: a solve at simulated `elapsed_ms = 30_000` against a 90s decay returns bonus `floor(100 * (1 - 30/90)) = 66`. Service uses an injectable clock (not `datetime.utcnow` directly) so tests can advance time deterministically.

**Prior art:** `backend/tests/unit/services/test_rapid_fire_service.py` (same fake-DAO style, same session-lifecycle assertions). Route-layer tests follow `backend/tests/unit/api/rapid_fire/` (auth, play, answer, abandon split files).

### E2E tests

Add a Pinpoint journey to `backend/tests/e2e/`:

- **`test_pinpoint_journey.py`** — full-pool playthrough: login → start → solve some puzzles on clue 1, fail one, solve last on clue 3 → assert final session score equals expected sum, assert lobby tile flips to `completed`, assert leaderboard reflects the score.
- **`test_pinpoint_lifecycle_journeys.py`** — abandon mid-puzzle and confirm the partial score is recorded; refresh mid-puzzle and confirm `play` returns the same `clues_revealed`.

### Frontend tests

- Reducer / hook tests for the Pinpoint client state machine (analogous to existing `rapid-fire` reducer tests).
- API client wrapper tests (`lib/api/pinpoint.test.ts`) following the Rapid Fire pattern.
- Navigation guard abandon behaviour for Pinpoint mirrors the existing tests for Rapid Fire — extend the existing test file or add a parallel one.

---

## Out of Scope

- Hint system of any kind (no "reveal first letter", no "category hint").
- Revealing the canonical answer on solve, fail, or the result screen.
- Per-puzzle hard timeout (stopwatch is unbounded by design).
- Penalty/negative scoring for wrong guesses (already encoded in clue-based score decay).
- Configurable `session_puzzle_count` — every player plays the entire seeded pool.
- Fuzzy / edit-distance answer matching — aliases are explicit.
- Admin tooling for puzzle authoring or live puzzle editing during the event.
- Daily-puzzle / streak mechanics from LinkedIn Pinpoint — the LEAP event is a single-day tournament.
- Any logic for Wikipedia Speed Run, Picture Illustration, Four Pics One Lie, or Crossword.

---

## Further Notes

- The `pinpoint` game id must be added to `leap/config/constants.py` `GAMES` and to the `game_sessions.game_id` CHECK constraint via a new Alembic migration **before** any code paths reference it.
- The seed file at `docs/games-examples/pinpoint.json` shows the per-puzzle shape but lacks `answer_aliases`. The production seed at `leap/seeds/data/pinpoint.json` must include aliases for every puzzle. Example:

  ```json
  {
      "answer": "Cloud Computing",
      "answer_aliases": ["cloud", "cloud computing", "the cloud", "aws", "azure", "gcp"],
      "clue1": "virtualization",
      "clue2": "redundancy",
      "clue3": "scalability",
      "clue4": "load balancing",
      "clue5": "instances"
  }
  ```

- A Meridian design YAML (`docs/design/pinpoint.meridian.yaml`) should be authored before implementation, walking the call graph top-down route → service → DAO → model, mirroring the Rapid Fire and Picture Illustration design docs.
- The injectable clock pattern used for Wiki time-bonus tests should be reused here so that `compute_time_bonus` and the service-level time-bonus assertions are deterministic.
- Alphabetisation in the lobby is governed by the `GAMES` registry order; place `pinpoint` after the existing entries unless event design says otherwise.
