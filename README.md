# LEAP Arcade — 2026 5-month Intern Batch

**LEAP Arcade** is an internal corporate event game platform built for the 2026 5-month intern batch. Players compete across a set of live mini-games — Rapid Fire Quiz, Wikipedia Speed Run, Picture Illustration, Four Pics One Lie, and Crossword — from a shared lobby, with scores flowing into a real-time leaderboard.

Players sign in using their corporate employee ID and a shared event code. No per-player secrets, no user management overhead — just play.

---

## Repo layout

| Path | What lives here |
|------|----------------|
| `backend/` | FastAPI · SQLAlchemy (async) · PostgreSQL — API, migrations, seeds |
| `frontend/` | Next.js — login, lobby, game shells, leaderboard |
| `docs/` | Technical plans, design specs, and ADRs |

> Agent-oriented conventions and architecture detail are in **`AGENTS.md`** (repo root) and **`frontend/AGENTS.md`**.

---

## Prerequisites

- **Docker & Docker Compose** — for Postgres (and optional containerised API)
- **[uv](https://docs.astral.sh/uv/)** — Python 3.12+ package manager (`backend/pyproject.toml`)
- **Bun** — frontend package manager (see `frontend/AGENTS.md`)
- **GNU Make** *(optional)* — short commands at the repo root; raw shell equivalents are shown below each `make` call

---

## First-time setup

```bash
# 1. Backend environment
cp backend/.env.example backend/.env   # then adjust values as needed

# 2. Backend dependencies (from backend/)
uv sync

# 3. Frontend dependencies (from frontend/)
bun install
```

---

## Running locally

### Option A — Full stack in Docker

Spin up Postgres, the API, and the frontend all at once:

```bash
make dev
# or
docker compose --env-file backend/.env up -d
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| Postgres | localhost:5432 |

```bash
make dev-down
# or
docker compose --env-file backend/.env down
```

---

### Option B — Postgres in Docker, API + frontend on host

Best for active development — hot reload works for both backend and frontend.

**1. Start Postgres only:**

```bash
docker compose --env-file backend/.env up -d postgres
```

**2. Run the API** (from `backend/`):

```bash
uv run alembic upgrade head   # apply migrations + seed data
uv run dev                    # hot-reload on http://localhost:8000
```

**3. Run the frontend** (from `frontend/`):

```bash
bun dev   # http://localhost:3000
```

Start order: Postgres → API → frontend.

```bash
# Stop Postgres when done (omit -v to keep the postgres_data volume)
docker compose --env-file backend/.env down
```

---

## Tests

### Unit tests

No Docker required — runs against in-memory fakes.

```bash
make unit
# or (from backend/)
uv run pytest tests/unit/ -v
```

### E2E API tests

Spins up a **dedicated test database** on port `5433` (`leap_test`) so dev data on `5432` is never touched. Uses Compose project name `leap-e2e` to keep volumes isolated.

```bash
make e2e
```

<details>
<summary>Without <code>make</code></summary>

```bash
# Start test Postgres
docker compose -p leap-e2e --env-file backend/.env \
  -f docker-compose.yml -f docker-compose.test.yml \
  up -d postgres_test --wait

# Migrate test DB
(cd backend && POSTGRES_CONNECTION_STRING="postgresql+asyncpg://leap:leap@localhost:5433/leap_test" \
  uv run alembic upgrade head)

# Run tests
(cd backend && uv run pytest tests/e2e/ -v)

# Tear down
docker compose -p leap-e2e --env-file backend/.env \
  -f docker-compose.yml -f docker-compose.test.yml down
```

</details>

**Reset a broken test DB:**

```bash
make e2e-reset
# or
docker compose -p leap-e2e --env-file backend/.env \
  -f docker-compose.yml -f docker-compose.test.yml down -v
```

---

## Key docs

| Document | What it covers |
|----------|---------------|
| `docs/plans/2026-05-10-backend-technical-design.md` | Backend architecture |
| `docs/plans/2026-05-16-e2e-api-tests-prd.md` | E2E test infrastructure |
| `docs/design/rapid-fire.meridian.yaml` | Rapid Fire domain spec (source of truth) |
