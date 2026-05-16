# PRD: E2E API Test Infrastructure

**Date:** 2026-05-16  
**Status:** Ready for implementation

---

## Problem Statement

The backend has a complete unit test suite (routes, service, scoring) backed by in-memory fakes. However, there is no test layer that exercises the real database, real migrations, and real seed data together. Bugs in SQL queries, migration state, or seed-dependent behaviour (e.g. question pool shape) are invisible until the app is run manually. Additionally, the compose setup is confined to `backend/` and cannot be invoked from the repo root — making it awkward to spin up the full stack and run any future cross-cutting tooling.

## Solution

1. Lift the Docker Compose file to the repo root so the full stack (`postgres` + `api`) can be started with a single `docker compose up` from anywhere in the repo.
2. Add a `docker-compose.test.yml` overlay that brings up a dedicated `postgres_test` service with its own isolated volume.
3. Add an e2e test suite under `backend/tests/e2e/` that uses `httpx.AsyncClient` with `ASGITransport` (in-process, no extra API container) against the real test database.
4. Provide a `Makefile` at the repo root with named targets for the common developer workflows.

## User Stories

1. As a developer, I want to run `make dev` from the repo root to start the full dev stack, so that I don't need to `cd` into `backend/` first.
2. As a developer, I want to run `make e2e` to spin up the test database, run migrations, seed data, and execute all e2e tests, so that I get real-database confidence in a single command.
3. As a developer, I want to run `make e2e-reset` to nuke the test database volume and start fresh, so that I can recover from corrupted test state without manual cleanup.
4. As a developer, I want each e2e test journey to start with a clean transactional state (truncated player/session/answer tables), so that tests do not interfere with each other.
5. As a developer, I want seed data (rapid fire questions) to be loaded once per suite run and remain available across all tests, so that journey tests can exercise the full question pool without re-seeding between tests.
6. As a developer, I want the e2e conftest to override `Settings.POSTGRES_CONNECTION_STRING` to point at the test database, so that no extra `.env.test` file is needed and the override is self-documenting in the test code.
7. As a developer, I want to verify the full rapid fire happy path (login → play → answer all questions → completed session → leaderboard) against a real database, so that I know the end-to-end flow works before shipping.
8. As a developer, I want to verify the abandon journey (login → play → answer some → abandon → partial score on leaderboard), so that scoring and status transitions are correct in real SQL.
9. As a developer, I want to verify mid-game resume (login → play → answer some → call play again → correct question returned, correct `questions_answered` count), so that the resume path works end-to-end.
10. As a developer, I want to verify multi-player leaderboard ranking (two players complete rapid fire with different scores → leaderboard order is correct), so that the ranking SQL is correct.
11. As a developer, I want a duplicate session attempt (player calls `/play` when they already have an active session) to return 409, verified against the real unique constraint, so that the DB constraint and service logic are both exercised.
12. As a developer, I want a login attempt with the wrong event code to return 401, verified against real auth logic, so that I know the auth path is correct end-to-end.
13. As a developer, I want the `postgres_test` service to use its own named volume (`postgres_test_data`) separate from `postgres_data`, so that wiping the test DB never touches dev data.
14. As a developer, I want the `api` service in the base compose to continue reading `backend/.env` unchanged, so that the existing dev workflow is not disrupted by the root-level compose move.

## Implementation Decisions

### Compose restructure

- `backend/docker-compose.yml` is moved to `docker-compose.yml` at the repo root.
- The `api` service `build` context changes from `.` to `./backend`, and `env_file` changes from `.env` to `./backend/.env`. Volume mounts on `./scripts` adjust accordingly.
- A `docker-compose.test.yml` overlay adds a single `postgres_test` service with its own named volume `postgres_test_data`, its own port mapping (`5433:5432`), and its own database name (`leap_test`). The test database uses the same credentials as dev for simplicity.
- The `api` service is **not** duplicated in the test overlay — e2e tests use in-process ASGI transport.

### Makefile targets

- `make dev` — `docker compose up -d`
- `make dev-down` — `docker compose down`
- `make e2e` — bring up `postgres_test`, wait for healthy, run `alembic upgrade head` against test DB, run `uv run pytest tests/e2e/ -v`, tear down `postgres_test`
- `make e2e-reset` — `docker compose -f docker-compose.yml -f docker-compose.test.yml down -v postgres_test` then re-run `make e2e`
- `make unit` — `cd backend && uv run pytest tests/unit/ -v` (convenience wrapper)

### E2e conftest

- A session-scoped fixture overrides `Settings.POSTGRES_CONNECTION_STRING` (via monkeypatching `get_settings` or directly patching the `Settings` singleton) to point at `postgresql+asyncpg://leap:leap@localhost:5433/leap_test` before any test module is imported.
- A session-scoped fixture runs Alembic migrations against the test DB on suite start and triggers the seed loader (calls the same function as the FastAPI lifespan, gated by `SEED_ON_STARTUP`).
- A function-scoped `clean_db` fixture truncates the transactional tables — `players`, `game_sessions`, `rapid_fire_answers` — with `RESTART IDENTITY CASCADE` between each test journey. Content tables (`rapid_fire_questions`) are not touched.
- `httpx.AsyncClient` is constructed with `ASGITransport(app=app)` and `base_url="http://test"` — no real HTTP port is bound.

### E2e journey test scope

Six journeys, all in `backend/tests/e2e/`:

| Journey | Key assertions |
|---|---|
| Full game (happy path) | Session status `completed`, correct score, player appears on leaderboard |
| Abandon mid-game | Session status `abandoned`, partial score on leaderboard, `games_completed=0` |
| Resume mid-game | Second `/play` call returns correct `questions_answered`, question not in already-answered set |
| Multi-player ranking | Two players, different scores, leaderboard order correct |
| Duplicate session (409) | Second `/play` call while session active returns 409 |
| Wrong event code (401) | Login with bad event code returns 401, no player created |

### What is NOT duplicated from unit tests

E2e tests do not re-assert field-level response shapes, 422 validation errors, or option index absence from `QuestionSchema` — those are already covered in `tests/unit/`. E2e tests assert journey-level outcomes: status codes, status transitions, and score correctness.

## Testing Decisions

- **What makes a good e2e test:** asserts observable outcomes through the HTTP surface (status code + key response fields) against real infrastructure. Does not inspect internal service state, DAO internals, or ORM objects directly.
- **Modules covered:** auth route, rapid fire routes (`/play`, `/answer`, `/abandon`), leaderboard route — all via real `AsyncSession` and real PostgreSQL.
- **Prior art:** the unit suite (`tests/unit/api/`) establishes the `httpx.AsyncClient` + `ASGITransport` pattern; the e2e conftest extends it with a real DB instead of fakes.
- **Seed dependency:** tests assume rapid fire questions exist (seeded at suite start). Tests must not hard-code question IDs — they call `/play` to discover the active question dynamically.

## Out of Scope

- Frontend container in Docker Compose — deferred until the Next.js app has real API client code.
- Load / performance testing with Locust — deferred to a future `load-tests/` setup at the repo root.
- E2e tests for non-rapid-fire games (wiki, picture, four pics, crossword) — out of scope for this build.
- CI pipeline integration — the Makefile targets are for local developer use; CI integration is a separate concern.
- Browser-level end-to-end tests (Playwright) — out of scope; this PRD covers API-level e2e only.

## Further Notes

- The `postgres_test` container uses port `5433` on the host to avoid clashing with the dev `postgres` on `5432`. The conftest connection string must use `localhost:5433`.
- `make e2e-reset` is the escape hatch for corrupted volume state — it destroys `postgres_test_data` entirely. Developers should reach for this when migrations are in a broken state rather than trying to manually patch the test DB.
- Locust load tests (future) will target the dev stack (`make dev`) on `localhost:8000` and live in `load-tests/locustfile.py` with their own `requirements.txt`. No `uv` project — Locust is a standalone tool.
