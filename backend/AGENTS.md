# AGENTS.md

## Tech Stack & Architecture

- **Runtime / package manager:** Python 3.12 · **`uv`** only (`uv sync`, `uv run …`)
- **API:** FastAPI (async) · single service under `leap/`
- **Database:** PostgreSQL · SQLAlchemy 2.0 async · Alembic migrations
- **Auth:** simple JWT (corp ID + event code → signed token) · no Clerk, no external auth service
- **Deployment:** Docker Compose — `docker compose up` starts everything

**Package layout:**

```
leap/
  api/          routes/ + deps.py (FastAPI deps: current_player, db session)
  config/       settings.py
  core/         context_manager.py, auth.py (JWT sign/verify), database/
  dao/
    base_pg_dao.py
    models/           # all models imported in __init__.py for Alembic autogenerate
      player.py
      game_session.py
      wiki_content.py, picture_content.py, rapid_fire_content.py,
      four_pics_content.py, crossword_content.py
    player_dao.py
    session_dao.py
    wiki_content_dao.py, picture_content_dao.py, rapid_fire_content_dao.py,
    four_pics_content_dao.py, crossword_content_dao.py
  games/        base.py (ScoringResult), wiki/, picture/, rapid_fire/, four_pics/, crossword/
  service/      container.py (ServiceContainer), exceptions.py (BaseServiceException), *_service.py
  seeds/        loader.py (upsert at startup), data/ (JSON seed files per game — organizer edits pre-event)
```

Each game module (`leap/games/<game>/`) owns: `service.py`, `scoring.py`, and any game-specific logic (e.g. `wiki/proxy.py` for the Wikipedia fetch + link rewrite). Game services depend on their content DAO from `leap/dao/` — never read seed files directly at runtime.

## Project Purpose

Self-hosted tournament platform for Fidelity's LEAP graduate onboarding programme. Players compete across 5 mini-games (Wikipedia Speed Run, Picture Illustration, Rapid Fire Quiz, Four Pics One Lie, Crossword) and rank on a shared live leaderboard.

Key domain terms: player, game_session, score, leaderboard, event_code, corp_id, session_data (JSONB game state).

No Redis. No external services at runtime (except Wikipedia live proxy for the wiki game). Designed for ~200 concurrent players on a single VM.

## Development Workflow

- **Install:** `uv sync`
- **Dev server:** `uv run dev` (uvicorn, hot-reload, port 8000)
- **Production server:** `uv run start` (gunicorn + uvicorn workers, 4 workers, port 8000)
- **Migrations:** `uv run alembic revision --autogenerate -m "describe"` · `uv run alembic upgrade head`
- **Lint:** `uvx ruff check . --fix`
- **Type check:** `uv run pyright leap/`
- **Seed data:** controlled by `SEED_ON_STARTUP=true` env var — runs in lifespan at startup

## Dos and Don'ts

- Use **`uv`**, not pip or poetry, for all dependency management
- Register every new SQLAlchemy model in **`leap/dao/models/__init__.py`** — Alembic autogenerate only sees what's imported there
- **Do not** edit applied migrations in place — always generate a new revision
- Game scoring logic lives in **`leap/games/<game>/scoring.py`** — not in route handlers or DAOs
- Wikipedia proxy logic lives in **`leap/games/wiki/proxy.py`** — httpx async client, BeautifulSoup, link rewrite
- Use **`BaseServiceException`** subclasses for service errors (never raw `HTTPException` from service layer)
- `session_data` on `game_sessions` is a JSONB column — use it for game-specific runtime state (e.g. wiki click path, rapid fire current question index)
- Game content (questions, puzzles, image sets) lives in content tables, seeded from `leap/seeds/data/*.json` at startup — game services query content via DAOs, never read seed files at runtime
- Server-side timestamp (`started_at`) is the source of truth for all timer logic — never trust client-reported elapsed time
- Unique constraint on `(player_id, game_id)` in `game_sessions` enforces one session per game per player — duplicate start attempts should 409, not create a second row

## Agent Memory

### Learned User Preferences

- When dispatching parallel implementation tasks, use `composer-2-fast` as the subagent model and keep the main orchestration chat for high-level decisions only.

### Learned Workspace Facts

- Package root is `leap/` (not `app/`) — all imports use `from leap.*`
- Seed loading happens in the FastAPI lifespan function, gated by `SEED_ON_STARTUP` setting
- The existing migration (`0de1443cd0f2_initial.py`) is from a previous project scaffold and should be deleted — start migrations fresh for the LEAP schema
- `docs/patterns/` contains task-specific guidance — check `index.md` before writing new features
- Content DAOs (questions, puzzles, image sets) stay flat under `leap/dao/` — no separate `content/` module; content models (e.g. `wiki_content.py`, `rapid_fire_content.py`) live flat in `leap/dao/models/`
- Content is pre-event configuration only (seed JSON → Postgres at startup) — no runtime content editing API is needed; game services always query content via DAOs, never read seed files directly

## Reference Docs

| Doc | When to read |
|-----|-------------|
| `docs/patterns/index.md` | Entry point — what pattern docs exist and when to use them |
