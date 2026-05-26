# AGENTS.md

**Repo:** leap-5m-26 — internal corporate event game platform

## Tech Stack & Architecture

- **Runtime:** Python 3.12+ · FastAPI · SQLAlchemy 2.0 async · asyncpg · PostgreSQL
- **Auth:** PyJWT (HS256) — corp_id + shared event code; no per-player secret
- **Config:** pydantic-settings · structlog · Alembic migrations
- **Package manager:** `uv` (not pip, not poetry)
- **Structure:**
  - `backend/leap/api/` — routes + schema (HTTP layer only)
  - `backend/leap/service/` — business logic; owns session lifecycle
  - `backend/leap/dao/` — DB access; each method takes `AsyncSession` as first arg
  - `backend/leap/types/` — internal Pydantic DTOs (`BaseLeapModel`); shared between DAO and service
  - `backend/leap/games/rapid_fire/` — game-specific logic (only rapid_fire is in scope)
  - `backend/leap/config/` — settings, constants, error definitions
  - `backend/leap/seeds/` — JSON seed files + idempotent loader (runs at startup)

## Project Purpose

One-day corporate event with ~100–200 players playing 5 mini-games on a shared platform. Players log in with their corp employee ID and a shared event code. Games: Rapid Fire Quiz (in scope), Wikipedia Speed Run, Picture Illustration, Four Pics One Lie, Crossword (last 4 are out of scope for this build — do not implement or stub them beyond what already exists).

Key domain terms: player, corp_id, event_code, game_session, rapid_fire_question, rapid_fire_answer, lobby, leaderboard.

## Development Workflow

All commands run from `backend/`:

- **Install:** `uv sync`
- **Dev server:** `uv run uvicorn leap.api.main:app --port 8000`
- **Tests:** `uv run pytest tests/ -v`
- **Migrations:** `uv run alembic upgrade head`
- **Generate migration:** `uv run alembic revision --autogenerate -m "<description>"`
- **Local DB:** from repo root, `docker compose --env-file backend/.env up -d postgres` or `make dev` (postgres + api; reads `backend/.env`)
- **Type check:** `uv run pyright` (if configured)

## Dos and Don'ts

- Use `uv`, never pip
- Use `typing.List`, `typing.Dict`, `typing.Optional` — not bare lowercase builtins
- Internal domain types go in `leap/types/` (subclass `BaseLeapModel`); API shapes go in `leap/api/schema/`
- `CurrentPlayer` lives in `leap/types/player.py` — services must not import from `leap/api/`
- Services own the session: `async with self._ctx.session() as session:` — DAOs take `AsyncSession`, never create one
- DAOs return typed Pydantic DTOs, not plain dicts
- Service errors use `BaseServiceException` subclasses from `leap/service/exceptions.py` — never raise raw `HTTPException` from a service
- Use `utc_now()` from `leap.core.common.time` for all timestamp operations — never import `datetime` directly in business logic
- Do not define fixed-count constants for game content (e.g., no `RAPID_FIRE_QUESTION_COUNT`) — pool size comes from the DB
- Seeds are idempotent (`ON CONFLICT DO NOTHING` / `DO UPDATE`) — safe to re-run on every startup
- Never add game logic for wiki, picture, four_pics, crossword — they are out of scope
- **Cross-stack static assets:** games that serve images from seed JSON (Picture Illustration, Four Pics) must coordinate backend `image_paths` with `frontend/public/` layout and the auth proxy matcher in `frontend/src/proxy.ts` — see `frontend/AGENTS.md` (Learned Workspace Facts: auth proxy vs static assets)

## Agent Memory

### Learned User Preferences

- Always use fast subagents (e.g., `composer-2-fast`) for codebase exploration — whether during planning, general conversation, or implementation. Never explore inline when a subagent can be dispatched instead.
- No `_` prefix on injected dependencies in services (`self.ctx`, `self.player_dao`, `self.game_session_dao`). Reserve `_` only for genuinely private helpers and lazy-init internals (e.g., `_engine`, `_sessionmaker` in infrastructure classes, private helper methods on the base DAO)
- The `/deep-design` jam walks the call graph top-down (route → service → DAO → model); do not pre-write models and build up
- Prefer hand-written fakes over `MagicMock` in tests — fakes express the contract honestly
- DAO unit tests that need a real `AsyncSession` (i.e., execute real SQL) are integration tests — mark them with a TODO for integration test scaffolding; don't fake the SQLAlchemy execute/result API
- When the `BasePgDAO` abstract methods (`_to_orm`, `_apply_filters`) are unused for a read-only DAO, stub them with `raise NotImplementedError` and move on — don't bloat the DAO to satisfy the base class

### Learned Workspace Facts

- `backend/.env` holds all local credentials; repo-root `docker-compose.yml` spins up postgres — pass `--env-file backend/.env` (or use `make dev`)
- `alembic/env.py` requires explicit `await connection.commit()` after `context.run_migrations()` — without it, DDL is silently rolled back
- `alembic.ini` `sqlalchemy.url` must be set to the leap DB (`postgresql+asyncpg://leap:leap@localhost:5432/leap`) — the default scaffold pointed to a stale billing DB
- Rapid Fire design: spec `docs/design/rapid-fire.meridian.yaml`; compile to `docs/design/rapid-fire-design-map.html` via `meridian compile` (YAML is source of truth; do not edit the HTML by hand)
- Backend technical design: `docs/plans/2026-05-10-backend-technical-design.md`
- `leap/api/routes/games/rapid_fire.py` and `leap/api/routes/leaderboard.py` are the remaining stubs to implement
- `GET /players/me/sessions` — new endpoint needed to support lobby tile status; returns `[{ game_id, status, score }]` for the authenticated player
