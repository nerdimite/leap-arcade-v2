# LEAP (leap-5m-26)

Internal corporate event game platform: players sign in with a corp employee ID and shared event code, play mini-games from a lobby, and appear on a leaderboard. **Rapid Fire Quiz** is the primary implemented backend game; other games may exist as stubs in the codebase.

This repo contains:

| Path | Role |
|------|------|
| `backend/` | FastAPI + SQLAlchemy (async) + PostgreSQL — API, migrations, seeds |
| `frontend/` | Next.js app (login, lobby, game shells, API rewrites to the backend) |
| `docs/` | Plans, design specs, and issue write-ups |

Conventions and agent-oriented detail live in **`AGENTS.md`** (repo root) and **`frontend/AGENTS.md`**.

## Prerequisites

- **Docker** and Docker Compose (for Postgres and optional API container)
- **[uv](https://docs.astral.sh/uv/)** (Python 3.12+; the backend pins dependencies via `backend/pyproject.toml`)
- **Bun** (for the frontend — see `frontend/AGENTS.md`)

Optional: **GNU Make** at the repo root for short commands (`make dev`, `make e2e`, …). If `make` is missing, use the shell equivalents below.

## First-time setup

1. **Backend env** — copy `backend/.env.example` to `backend/.env` and adjust values as needed. Compose and local commands load this file.
2. **Backend deps** — from `backend/`: `uv sync`
3. **Frontend deps** — from `frontend/`: `bun install`

## Local development

### Full stack (Postgres + API in Docker)

From the **repo root** (uses `backend/.env`):

```bash
make dev
# or
docker compose --env-file backend/.env up -d
```

API: `http://localhost:8000` · Postgres (dev): `localhost:5432`

Stop:

```bash
make dev-down
# or
docker compose --env-file backend/.env down
```

### Backend only (against existing Postgres)

From `backend/`:

```bash
uv run uvicorn leap.api.main:app --port 8000
```

See **`AGENTS.md`** for migrations, seeding, and project layout (`leap/api`, `leap/service`, `leap/dao`, …).

### Frontend

From `frontend/`:

```bash
bun dev
```

---

## Tests

### Unit tests (in-memory fakes, no Docker DB)

From the **repo root**:

```bash
make unit
```

From `backend/`:

```bash
uv run pytest tests/unit/ -v
```

### E2E API tests (real PostgreSQL, migrations, seeds)

These run **httpx + ASGITransport** against the app while using a **dedicated test database** on port **5433** (`leap_test`), so dev data on `5432` is untouched. Compose uses project name **`leap-e2e`** so tearing down test stacks does not remove the dev `postgres_data` volume.

**One-shot (recommended):**

```bash
make e2e
```

**If `make` is not installed**, run this from the **repo root**:

```bash
docker compose -p leap-e2e --env-file backend/.env \
  -f docker-compose.yml -f docker-compose.test.yml \
  up -d postgres_test --wait

( cd backend && POSTGRES_CONNECTION_STRING="postgresql+asyncpg://leap:leap@localhost:5433/leap_test" \
  uv run alembic upgrade head )

( cd backend && uv run pytest tests/e2e/ -v )

docker compose -p leap-e2e --env-file backend/.env \
  -f docker-compose.yml -f docker-compose.test.yml down
```

**Reset test DB volume** (bad migration state, corrupted volume, etc.):

```bash
make e2e-reset
```

Without `make`: destroy the `leap-e2e` project volumes, then run the full manual e2e sequence above.

```bash
docker compose -p leap-e2e --env-file backend/.env \
  -f docker-compose.yml -f docker-compose.test.yml down -v
```

Design and journey list: **`docs/plans/2026-05-16-e2e-api-tests-prd.md`**.

---

## Key documentation

| Document | Contents |
|----------|----------|
| `docs/plans/2026-05-10-backend-technical-design.md` | Backend architecture |
| `docs/plans/2026-05-16-e2e-api-tests-prd.md` | E2E API test infrastructure |
| `docs/design/rapid-fire.meridian.yaml` | Rapid Fire domain spec (source of truth) |
