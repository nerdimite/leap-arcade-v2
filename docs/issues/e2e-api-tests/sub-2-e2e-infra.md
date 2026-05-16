# Sub-2: E2E Test Infrastructure

**Status:** done  
**Blocked by:** Sub-1  
**Blocks:** Sub-3, Sub-4, Sub-5

## Parent

`docs/issues/e2e-api-tests/parent.md`

## What to build

Create the shared e2e conftest and fixtures that all journey tests depend on. No journey tests are written in this slice — only the infrastructure that makes them possible.

**Test location:** `backend/tests/e2e/`

**Settings override:** The conftest overrides `Settings.POSTGRES_CONNECTION_STRING` before the app is imported by any test module, pointing it at `postgresql+asyncpg://leap:leap@localhost:5433/leap_test`. This is done by patching the `get_settings` cache or directly instantiating `Settings` with the test URL and injecting it. No `.env.test` file is needed.

**Fixtures:**

- `db_setup` (session-scoped): runs `alembic upgrade head` against the test database, then calls the seed loader to populate content tables (rapid fire questions). Runs once per suite.
- `clean_db` (function-scoped, autouse within `tests/e2e/`): after each test, truncates `players`, `game_sessions`, `rapid_fire_answers` with `RESTART IDENTITY CASCADE`. Content tables (`rapid_fire_questions`) are never truncated.
- `client` (function-scoped): yields an `httpx.AsyncClient` constructed with `ASGITransport(app=app)` and `base_url="http://test"`. Depends on `clean_db` so every test gets a clean state.

**`__init__.py`** files as needed to make `tests/e2e/` a proper package.

## Acceptance criteria

- [x] `backend/tests/e2e/conftest.py` exists and is importable without error
- [x] Running `uv run pytest tests/e2e/ -v` with `postgres_test` up produces zero collection errors (infra smoke tests exercise fixtures)
- [x] After `db_setup` runs, the `rapid_fire_questions` table in `leap_test` is populated with seed data
- [x] After each test (via `clean_db`), `players`, `game_sessions`, and `rapid_fire_answers` are empty; `rapid_fire_questions` remains populated
- [x] The `client` fixture yields a working `AsyncClient` that can hit the FastAPI app in-process
- [x] `uv run pytest tests/unit/ -v` continues to pass unchanged (conftest must not pollute the unit suite)

## Blocked by

Sub-1 (`docs/issues/e2e-api-tests/sub-1-compose-restructure.md`) — `postgres_test` service must exist before this conftest can be exercised
