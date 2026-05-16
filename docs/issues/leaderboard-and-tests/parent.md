# Leaderboard Endpoint + Test Suite Overhaul

## What to build

Two gaps remain before the Rapid Fire backend is shippable:

1. ~~`GET /leaderboard` raises `NotImplementedError`.~~ **Done (Sub-2).** The leaderboard endpoint returns ranked entries for all players.

2. The existing test suite tests service methods directly — one layer too deep. Overhaul it to use `TestClient` + `app.dependency_overrides` so tests verify behaviour through the actual HTTP surface. Fix the stale fakes that accumulated since the rapid-fire implementation was built.

**PRD:** `docs/plans/2026-05-16-leaderboard-and-tests-prd.md`

## Execution plan

```
Slice 1 (no blockers):   Sub-1 — Test infrastructure + fake cleanup
Slice 2 (after Sub-1):   Sub-2 — Leaderboard endpoint (data → service → route → tests)
Slice 3 (after Sub-1):   Sub-3 — Rapid Fire subcutaneous tests
```

Sub-2 and Sub-3 can be worked in parallel after Sub-1 completes. **Sub-1 is done** (`docs/issues/leaderboard-and-tests/sub-1-test-infra.md`). **Sub-2 is done** (`docs/issues/leaderboard-and-tests/sub-2-leaderboard-endpoint.md`). **Sub-3 is done** (`docs/issues/leaderboard-and-tests/sub-3-rapid-fire-tests.md`).

## Overall acceptance criteria

- [x] `GET /leaderboard` returns all players ordered by score, with 0-score players included
- [x] Abandoned session scores count toward leaderboard total; only completed sessions count for `games_completed`
- [x] All Rapid Fire routes (`/play`, `/answer`, `/abandon`) have subcutaneous tests through `TestClient`
- [x] `FakeRapidFireQuestionDAO` only exposes `get_all()` — stale methods removed
- [x] `FakeGameSessionDAO.update_status` sets `completed_at` for completed/abandoned status
- [x] All unit tests pass with `uv run pytest tests/unit/ -v`
