# PRD: Leaderboard Endpoint + Test Suite Overhaul

**Date:** 2026-05-16  
**Status:** Ready for implementation

---

## Problem Statement

Two gaps remain before the Rapid Fire backend is shippable:

1. **The leaderboard endpoint is a stub.** `GET /leaderboard` raises `NotImplementedError`. Players can complete Rapid Fire and see their own score, but the platform has no way to show how they rank against other players — which is the entire competitive premise of the event.

2. **The test suite is testing the wrong surface.** The existing service-level tests (where they exist) call service methods directly with injected fake DAOs. This is one layer too deep — it tests internal wiring rather than the HTTP interface players and the frontend actually talk to. The fakes are also stale: `FakeRapidFireQuestionDAO` has methods that no longer exist on the real DAO, and `FakeGameSessionDAO.update_status` does not set `completed_at`, making time-based result assertions silently wrong.

---

## Solution

Implement the leaderboard as a fully authenticated `GET /leaderboard` endpoint backed by a `LeaderboardService` and a new `get_leaderboard()` method on `GameSessionDAO`. The leaderboard includes every player — even those who have not completed any game — sorted by total score descending, with ties broken by games completed, then earliest completion time, then display name.

Replace the existing test approach with subcutaneous tests: `TestClient` calls against the real FastAPI app with fake DAOs injected via `app.dependency_overrides`. This tests behaviour through the actual HTTP surface — routing, auth, serialization, service logic, and error responses — without touching a real database. Update the shared fakes to match current DAO contracts.

---

## User Stories

1. As a player, I want to see a ranked leaderboard with all players' scores, so that I know where I stand competitively during the event.
2. As a player, I want to see players who have not yet scored appear on the leaderboard with 0 points, so that I can see the full competitive field at a glance.
3. As a player, I want the leaderboard to reflect partial points from abandoned games, so that no progress is invisible.
4. As a player, I want ties broken by number of completed games, so that players who finished more games rank higher than those who scored the same but gave up on some.
5. As a player, I want ties among players with equal score and equal completions broken by who finished first, so that speed is rewarded.
6. As a player, I want the leaderboard to require login, so that it cannot be accessed by anyone outside the event.
7. As a player, I want each leaderboard entry to include a rank number, so that the frontend can display "You are #3" without computing it client-side.
8. As a player, I want to see the total number of players on the leaderboard, so that I know the size of the field I'm competing in.
9. As a player, I want the leaderboard to show how many games each player has completed, so that I understand whose score came from finishing full games vs partial attempts.
10. As a developer, I want the leaderboard query encapsulated in a single DAO method, so that the aggregation SQL is testable in isolation and cannot leak into service or route code.
11. As a developer, I want all Rapid Fire route behaviour verified through the HTTP interface, so that tests catch serialization bugs, wrong status codes, and missing schema fields — not just service return values.
12. As a developer, I want the shared test fakes to accurately reflect current DAO contracts, so that fake-based tests cannot silently pass while real behaviour is broken.
13. As a developer, I want `FakeGameSessionDAO.update_status` to set `completed_at`, so that tests of the abandon and complete flows produce non-zero `time_taken_seconds` results.
14. As a developer, I want `FakeRapidFireQuestionDAO` to only expose `get_all()`, matching the real DAO, so that stale methods cannot be called in tests.
15. As a developer, I want the leaderboard service to be wired into `ServiceContainer`, so that it is injected consistently with all other services.
16. As a developer, I want subcutaneous tests for `POST /games/rapid-fire/play` covering the new-player, mid-game resume, completed, and abandoned branches, so that the full play flow is verified end-to-end through HTTP.
17. As a developer, I want subcutaneous tests for `POST /games/rapid-fire/answer` covering correct, wrong, skipped, replay (409), and game-over-inline-result cases, so that the answer submission contract is unambiguous.
18. As a developer, I want subcutaneous tests for `POST /games/rapid-fire/abandon` covering the partial-score and already-completed (409) cases, so that the forfeit path is verified.
19. As a developer, I want subcutaneous tests for `GET /leaderboard` covering the all-players result, zero-score players, and correct ordering, so that leaderboard behaviour is verified through HTTP.
20. As a developer, I want auth rejection (401) verified for all four routes in tests, so that the JWT requirement is not silently dropped.

---

## Implementation Decisions

### Leaderboard DAO

A new `get_leaderboard()` method is added to `GameSessionDAO` (not a separate `LeaderboardDAO` — the query is fundamentally a game session aggregation). It executes a single SQL query and returns `List[LeaderboardEntryDTO]` ordered by the server-side sort. Rank is not computed in SQL; it is added by the service as the list index + 1.

The query is a LEFT JOIN from `players` to `game_sessions` filtered to `status IN ('completed', 'abandoned')`. This means:
- Every player in the `players` table appears in the result regardless of session state
- `total_score` sums scores from both completed and abandoned sessions; players with no sessions get 0 (via `COALESCE`)
- `games_completed` counts only `status = 'completed'` sessions
- `first_completion` is the earliest `completed_at` across completed sessions only

```sql
SELECT
    p.id AS player_id,
    p.display_name,
    COALESCE(SUM(gs.score), 0) AS total_score,
    COUNT(CASE WHEN gs.status = 'completed' THEN 1 END) AS games_completed,
    MIN(CASE WHEN gs.status = 'completed' THEN gs.completed_at END) AS first_completion
FROM players p
LEFT JOIN game_sessions gs
    ON gs.player_id = p.id AND gs.status IN ('completed', 'abandoned')
GROUP BY p.id, p.display_name
ORDER BY
    total_score DESC,
    games_completed DESC,
    first_completion ASC NULLS LAST,
    p.display_name ASC
```

### `LeaderboardEntryDTO`

New internal DTO with fields: `player_id: str`, `display_name: str`, `total_score: int`, `games_completed: int`, `first_completion: Optional[datetime]`. Subclasses `BaseLeapModel`. Lives alongside `GameSessionDTO` in the game types module.

### `LeaderboardService`

New service class with a single `get_leaderboard()` method. Opens `async with self.ctx.session()`, calls `game_session_dao.get_leaderboard(session)`, adds `rank` field (enumerate starting at 1), and returns a list of ranked entries plus `total_players` count. Wired into `ServiceContainer` alongside `auth`, `lobby`, and `rapid_fire`.

### API Schema

Two new response shapes:

- `LeaderboardEntrySchema`: `rank: int`, `player_id: str`, `display_name: str`, `total_score: int`, `games_completed: int`
- `LeaderboardResponse`: `entries: List[LeaderboardEntrySchema]`, `total_players: int`

`first_completion` is internal to the DTO and not exposed in the API response — it is only used for server-side ordering.

### Leaderboard Route

`GET /leaderboard` requires a valid JWT (uses `get_current_player` dependency for auth; the player identity itself is not used in the response). Returns `LeaderboardResponse`. The existing stub is replaced entirely.

### Test Architecture

Tests shift from service-method calls to subcutaneous tests via FastAPI's `TestClient` with `app.dependency_overrides`. The dependency override replaces `get_container` with a factory returning a `FakeServiceContainer` that wraps the fake DAOs. The `get_current_player` dependency is also overridden to return a fixed `CurrentPlayer` for auth bypass.

This approach tests routing, auth enforcement, response serialization, service logic, and error code mapping in a single pass — without touching a real database.

Test files are organised under `tests/unit/api/`, mirroring the route structure. The existing `tests/unit/games/rapid_fire/test_scoring.py` is untouched — pure function tests through the correct interface.

### Fake Updates

`FakeRapidFireQuestionDAO` is rewritten to expose only `get_all()`, matching the real DAO. The stale `get_random_excluding()` and `get_question_count()` methods are removed.

`FakeGameSessionDAO.update_status()` is updated to set `completed_at = utc_now()` when the status is `COMPLETED` or `ABANDONED`, matching the real DAO's behaviour. This makes `time_taken_seconds` in `_build_result` non-zero and testable.

`FakeGameSessionDAO.get_leaderboard()` is implemented to return a deterministic ordered list from the in-memory session store, suitable for leaderboard route tests.

A new `FakeLeaderboardService` (or a `FakeServiceContainer` that wires all fakes together) is introduced for `dependency_overrides` injection.

---

## Testing Decisions

**What makes a good test here:** tests verify behaviour through the HTTP surface — status codes, response body shape, field values — not service return types or DAO call counts. A test should survive renaming an internal helper without breaking. If a test can only fail when observable HTTP behaviour changes, it is testing the right thing.

**Modules with tests:**

- `POST /games/rapid-fire/play` — new-player branch (201 active + question), mid-game resume (active + different question), completed session (result block, no question), abandoned session (result block, no question), 401 when no token
- `POST /games/rapid-fire/answer` — correct answer (correct=true, score increases), wrong answer (correct=false, score unchanged), skipped (selected_option=null), selected_option=5 (422), replay same question_id (409), last question triggers game-over inline result (next_question=null, result block present), 401 when no token
- `POST /games/rapid-fire/abandon` — mid-game abandon returns partial score, abandon with 0 answers returns score=0, already-completed session returns 409, 401 when no token
- `GET /leaderboard` — returns all players (including 0-score), ordering is correct (higher score first), rank is 1-indexed and sequential, total_players matches player count, 401 when no token

**Pure function tests (unchanged):**

- `compute_rapid_fire_score` in `tests/unit/games/rapid_fire/test_scoring.py` — already complete and correct. These stay as-is.

**Prior art:** `tests/unit/service/test_auth_service.py` and `tests/unit/service/test_lobby_service.py` show the existing fake-based pattern. The new tests follow the same fake philosophy (hand-written, contract-expressing) but operate through `TestClient` rather than direct service instantiation.

---

## Out of Scope

- Facilitator admin view — no separate admin leaderboard endpoint
- Real-time leaderboard via WebSockets or polling push — frontend polls `GET /leaderboard` on its own schedule
- Per-game score breakdown per player in the leaderboard response
- Wikipedia, Picture Illustration, Four Pics One Lie, and Crossword game implementations
- Integration tests against a real database — DAO correctness against Postgres is deferred; a TODO marker is sufficient
- E2E tests — manual walkthrough on event day is sufficient given the one-day event context
- Leaderboard filtering or pagination — the player count (~100–200) makes this unnecessary

---

## Further Notes

- The Rapid Fire implementation (routes, service, DAOs, scoring, schemas) is already in place and matches the design spec in `docs/design/rapid-fire.meridian.yaml`. The pending sub-issues in `docs/issues/rapid-fire/` reflect a plan that was overtaken by an earlier implementation — they should be marked done or deleted once the test suite is written and passing.
- The scoring formula in `docs/issues/rapid-fire/sub-3-types-daos-scoring.md` differs slightly from the live implementation. The live formula is correct (500ms maps to exactly 100 points); the issue's formula would give ~98. Do not regress the formula when writing tests — use the live code's behaviour as the source of truth.
- `correct_option_index` is 1-indexed throughout: DB, seed data, DTOs, and the `correct_answer_text` derivation (`options[correct_option_index - 1]`) all align on this. Tests should verify the index convention is honoured in API responses (the field must be absent from `QuestionSchema`, present in `AnswerResponse.correct_option`).
