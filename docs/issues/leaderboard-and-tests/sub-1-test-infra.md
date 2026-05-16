# Sub-1: Test Infrastructure + Fake Cleanup

**Status:** done  
**Blocked by:** None  
**Blocks:** Sub-2, Sub-3 (unblocked)

## What to build

Fix the shared test fakes so they accurately reflect current DAO contracts, and establish the `TestClient` + `app.dependency_overrides` pattern that all subsequent route-level tests will use.

The fakes have drifted from the real DAOs since the rapid-fire implementation was built. Two specific problems:

1. `FakeRapidFireQuestionDAO` exposes `get_random_excluding()` and `get_question_count()` — methods that do not exist on the real DAO. The real DAO only has `get_all()`, which is called once at startup by `RapidFireService.initialize()`. The fake needs to match.

2. `FakeGameSessionDAO.update_status()` does not set `completed_at`. The real DAO sets it to `utc_now()` when status becomes `COMPLETED` or `ABANDONED`. Without this, `_build_result()` always produces `time_taken_seconds=0.0` in tests, making time assertions meaningless.

Additionally, set up the test infrastructure that route-level tests depend on:

- A reusable way to override `get_container` with a fake service container via `app.dependency_overrides`
- A reusable way to override `get_current_player` with a fixed `CurrentPlayer` (auth bypass for unit tests)
- `FakeGameSessionDAO.get_leaderboard()` implemented as an in-memory computation (needed by Sub-2 tests)

This slice produces no new endpoints or features — its output is a correct, usable test foundation.

## Acceptance criteria

- [x] `FakeRapidFireQuestionDAO` has only `get_all(session) -> List[RapidFireQuestionDTO]`; stale `get_random_excluding` and `get_question_count` methods are removed
- [x] `FakeGameSessionDAO.update_status()` sets `completed_at = utc_now()` when status is `COMPLETED` or `ABANDONED`; active status leaves `completed_at` unchanged
- [x] `FakeGameSessionDAO.get_leaderboard()` returns a list of `LeaderboardEntryDTO`-compatible data from the in-memory session store (can be a simple aggregation — correctness verified in Sub-2 tests)
- [x] A `conftest.py` (or equivalent fixture module) provides: an `auth_override` fixture that overrides `get_current_player` with a fixed player, and a `make_container` helper that builds a `FakeServiceContainer` for injection via `app.dependency_overrides`
- [x] All previously passing tests continue to pass after fake changes (`uv run pytest tests/unit/ -v`)

## Blocked by

None — can start immediately
