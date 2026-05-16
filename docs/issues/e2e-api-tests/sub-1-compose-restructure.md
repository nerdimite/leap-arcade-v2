# Sub-1: Compose Restructure + Makefile

**Status:** done  
**Blocked by:** None — can start immediately  
**Blocks:** Sub-2

## Parent

`docs/issues/e2e-api-tests/parent.md`

## What to build

Move the Docker Compose setup from `backend/` to the repo root and wire in a test database overlay and a Makefile.

**Compose restructure:**
- Delete `backend/docker-compose.yml`; create `docker-compose.yml` at the repo root
- The `api` service `build` context becomes `./backend`, `env_file` becomes `./backend/.env`, and the `./scripts` volume mount adjusts to `./backend/scripts`
- The `postgres` and `api` service definitions are otherwise unchanged

**Test overlay:**
- Create `docker-compose.test.yml` at the repo root with a single new service: `postgres_test`
- `postgres_test` uses the same `postgres:16-alpine` image, same credentials as dev, database name `leap_test`, host port `5433` (to avoid clashing with dev postgres on `5432`), and its own named volume `postgres_test_data`
- `postgres_test` has the same healthcheck pattern as `postgres`

**Makefile** at the repo root with these targets (dev commands pass `--env-file backend/.env` so `POSTGRES_*` interpolation matches the old `backend/` compose behavior; e2e also uses `-p leap-e2e` so `e2e-reset` never removes the dev `postgres_data` volume):

| Target | What it does |
|---|---|
| `make dev` | `docker compose --env-file backend/.env up -d` |
| `make dev-down` | `docker compose --env-file backend/.env down` |
| `make unit` | `cd backend && uv run pytest tests/unit/ -v` |
| `make e2e` | Bring up `postgres_test`, wait for healthy, run alembic upgrade against test DB, run `uv run pytest tests/e2e/ -v`, tear down `postgres_test` |
| `make e2e-reset` | Destroy `postgres_test_data` volume, then run `make e2e` |

## Acceptance criteria

- [x] `docker compose --env-file backend/.env up -d` from the repo root starts `postgres` and `api` successfully (`docker compose config` validated; optional `--env-file` keeps credentials aligned with `backend/.env`)
- [x] `docker compose -f docker-compose.yml -f docker-compose.test.yml up -d postgres_test` starts the test DB on port `5433` without affecting the dev DB on `5432` (validate with `docker compose … config`)
- [x] `make dev` and `make dev-down` work from the repo root (requires `make`)
- [x] `make unit` runs the existing unit suite and all tests pass
- [x] `make e2e` target exists and its shell commands are syntactically correct (full journey coverage in Sub-2+)
- [x] `make e2e-reset` destroys the `leap-e2e` project’s `postgres_test_data` volume and re-runs `make e2e`
- [x] `backend/.env` is not moved or modified; existing `uv run` dev workflow inside `backend/` is unaffected
- [x] Old `backend/docker-compose.yml` is deleted

## Blocked by

None — can start immediately
