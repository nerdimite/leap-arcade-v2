# Design Doc — Rapid Fire Vertical Slice
Started: 2026-05-11. Informal capture; living artifact during the deep-design jam.

## Intent

> Full deep-design session for the rapid fire game including login and auth and all that. By the end of meridian, we have the full game platform working for the one game — that also means adding other endpoints around the user flow like getting all the games, the leaderboard as well.

## Scope

In scope:
- Auth: `POST /auth/login`, `POST /auth/logout`
- Lobby: `GET /lobby`
- Leaderboard: `GET /leaderboard`
- Rapid Fire: `POST /games/rapid-fire/start`, `GET /games/rapid-fire/state`, `POST /games/rapid-fire/answer`, `POST /games/rapid-fire/abandon`
- Supporting plumbing: JWT util, FastAPI deps, domain exceptions, global error handlers, settings, constants, seed loader (rapid fire only), migrations, container wiring

Out of scope (later jams):
- Wikipedia Speed Run, Picture, Four Pics, Crossword — models, DAOs, services, seeds.
- The wiki model files in `leap/dao/models/` (`wiki_content.py` etc.) are left untouched; their reshape happens in the wiki jam.

## Entry Points

| Method | Path | Auth | Trigger |
|---|---|---|---|
| `POST` | `/auth/login` | No | Player submits corp_id + event_code |
| `POST` | `/auth/logout` | Yes | Player initiates logout (server no-op) |
| `GET` | `/lobby` | Yes | Player loads home / refreshes |
| `GET` | `/leaderboard` | Yes | Player opens leaderboard |
| `POST` | `/games/rapid-fire/start` | Yes | Player clicks Play on Rapid Fire |
| `GET` | `/games/rapid-fire/state` | Yes | Page load / rehydration |
| `POST` | `/games/rapid-fire/answer` | Yes | Player submits answer or auto-skip |
| `POST` | `/games/rapid-fire/abandon` | Yes | Player forfeits mid-game |

## Traversal Strategy

**Wide-first.** Four entry-point clusters share the same downstream layers (auth dep, exceptions, DAO pattern, container, transaction model). Mapping the routes + service signatures first surfaces shared utilities and refactor impact before going deep on rapid-fire business logic.

Order: cross-cutting plumbing → models + DAOs → auth → lobby → leaderboard → rapid fire (service + scoring) → routes wiring → seed loader → container + lifespan.

## Non-Functional Constraints

### Cross-cutting

- **Atomicity:** every service method that mutates >1 row runs inside a single `ContextManager.session()` block. DAOs take the session in. Never open nested or multiple session blocks per service call.
- **Idempotency on `start`:** UNIQUE `(player_id, game_id)` on `game_sessions` is the enforcement; service catches the integrity error and surfaces `SessionAlreadyExistsException` (409). Never silently return the existing row.
- **JWT trust model:** `get_current_player` decodes only, no DB fetch. Identity = `(corp_id, display_name)` from claims. 24h expiry (env-configurable). Trade-off: cannot revoke mid-event.
- **Timer source of truth:** `game_sessions.started_at` (server `now()`). Client `time_ms` is recorded per answer but never canonical for total-time scoring (`completed_at - started_at`).
- **Service errors:** never raise `HTTPException` from service. Subclass `BaseServiceException`. Global handler in `leap/api/main.py` converts to JSON.
- **Concurrency target:** ~200 concurrent players, ~10 questions each. Negligible load. Single Postgres, single VM. No locking required beyond the UNIQUE constraint.
- **Event code:** plain env var `EVENT_CODE`, compared with `secrets.compare_digest()`. No bcrypt — same protection (env var) at zero dep cost.

### Rapid Fire specific

- **Replay protection:** answer endpoint rejects a `question_id` already present in `rapid_fire_answers` for this session.
- **Question selection:** must exclude already-asked. Done via `WHERE id NOT IN (SELECT question_id FROM rapid_fire_answers WHERE game_session_id = $1)` ORDER BY random() LIMIT 1.
- **No mid-question rehydration:** the "pending" question is never persisted. On rehydrate, the server serves a fresh random unanswered question. Functionally equivalent because scoring is correct/incorrect, not time-per-question.
- **Game end signal:** `get_random_excluding(asked_ids)` returns `None` — pool exhausted. No artificial question count cap; game length = seed pool size. `questions_remaining` in the response is `total_pool_size - len(asked_ids)`, where `total_pool_size` comes from `RapidFireQuestionDAO.get_question_count(session)`.

## File Map

(File entries are filled in as each is walked. Status legend: `[done]` direct code complete · `[stub]` stub + failing tests landed · `[pending]` not yet walked.)

### Cross-cutting plumbing (all `[done]` — direct code, not stubbed)

- `leap/config/settings.py` — added `JWT_SECRET_KEY`, `JWT_EXPIRE_HOURS`, `EVENT_CODE`, `RAPID_FIRE_QUESTION_COUNT`.
- `leap/config/constants.py` — `GAMES`, `GAME_IDS`, `GAME_SESSION_STATUSES`, `RAPID_FIRE_QUESTION_TYPES`.
- `leap/core/auth.py` — `encode_token`, `decode_token`, `verify_event_code`. Pure, no DB.
- `leap/service/exceptions.py` — rewritten with the 8 domain exceptions listed below.
- `leap/api/main.py` — global handlers (service / starlette HTTP / FastAPI HTTP / validation / unhandled), narrow route registration.
- `leap/api/deps.py` — `CurrentPlayer` dataclass, `get_current_player`, `get_container`.
- `leap/api/routes/lobby.py` — placeholder router; handler raises `NotImplementedError` until the lobby service lands.
- Deleted: `leap/api/routes/sessions.py` (obsolete generic `/sessions/{game_id}/start` — superseded by per-game routes).

### Types module `[done]`
`leap/types/` — internal Pydantic domain types flowing between DAO and service. Flat (no subfolders; project scope doesn't warrant it). API shapes live in `leap/api/schema/` and import from here when they match.

- `leap/types/__init__.py` — `BaseLeapModel` (`extra="ignore"`, `from_attributes=True`)
- `leap/types/player.py` — `PlayerDTO`
- `leap/types/game.py` — `GameSessionStatus`, `GameSessionDTO`, `GameStatusDTO`
- `leap/types/rapid_fire.py` — `RapidFireQuestionDTO`, `RapidFireAnswerDTO`, `RapidFireResultDTO`

### Auth path `[done/stub]`

- `leap/api/schema/auth.py` `[done]` — `LoginRequest`, `PlayerDTO`, `LoginResponse`. Direct code.
- `leap/api/routes/auth.py` `[done]` — `POST /auth/login` → `container.auth.login()`. `POST /auth/logout` → no-op. Direct code.
- `leap/service/auth_service.py` `[stub]` — `AuthService.login(corp_id, event_code)`. Normalises corp_id, fetches player, verifies event code, issues JWT.
- `leap/dao/player_dao.py` `[stub]` — `PlayerDAO.get_by_id(session, corp_id)`. Read-only; players are pre-seeded.
- `leap/dao/models/player.py` `[done]` — `id` (text PK = normalised corp_id), `display_name`, `created_at`. Removed stale `event_code_hash` and `is_active` columns.
- `tests/fakes.py` `[done]` — `FakeContextManager`, `FakeAsyncSession`, `FakePlayerDAO` (+ stubs for game session / question / answer DAOs used later).
- `tests/unit/service/test_auth_service.py` `[done]` — 5 failing tests covering happy path, normalisation, 404, 401, ordering of checks.
- `tests/unit/dao/test_player_dao.py` `[done]` — 2 failing tests; edge-case TODO for integration tests.

### NFRs — auth_service.py
- `login()` normalises `corp_id` (lowercase + strip) before any lookup. DAO receives the already-normalised ID — no ILIKE in the query.
- `verify_event_code` uses `secrets.compare_digest` — constant time, no short-circuit.

### Models (next — `[pending]`)

To replace / add:
- `leap/dao/models/game_session.py` — rewrite to new schema (no `session_data` JSONB).
- `leap/dao/models/rapid_fire_question.py` — new (replaces stale `rapid_fire_content.py`).
- `leap/dao/models/rapid_fire_answer.py` — new.
- `leap/dao/models/player.py` — already matches; keep.
- `leap/dao/models/__init__.py` — register only the 4 in-scope models so Alembic autogenerate only sees them; the unreshaped game model files (wiki/picture/four_pics/crossword) stay on disk but are *not* imported here.

Also: delete `backend/alembic/versions/0de1443cd0f2_initial.py` (stale scaffold migration); generate a fresh initial after models land.

### DAOs (next — `[pending]`)

- `leap/dao/player_dao.py`
- `leap/dao/game_session_dao.py`
- `leap/dao/rapid_fire_question_dao.py`
- `leap/dao/rapid_fire_answer_dao.py`

### Services (next — `[pending]`)

- `leap/service/auth_service.py`
- `leap/service/lobby_service.py`
- `leap/service/leaderboard_service.py`
- `leap/games/rapid_fire/service.py` (rewrite the placeholder)
- `leap/games/rapid_fire/scoring.py` (rewrite the placeholder)
- `leap/service/container.py` — wire in the new services; drop the not-in-scope `wiki/picture/four_pics/crossword` wiring for now.

### Routes (later — `[pending]`, thin direct wiring)

- `leap/api/routes/auth.py` — replace stub with login/logout handlers.
- `leap/api/routes/lobby.py` — replace stub body.
- `leap/api/routes/leaderboard.py` — replace stub body.
- `leap/api/routes/games/rapid_fire.py` — replace stub with `start`/`state`/`answer`/`abandon`.

### DTOs (`[pending]`, direct code)

- `leap/api/schema/auth.py`
- `leap/api/schema/lobby.py`
- `leap/api/schema/leaderboard.py`
- `leap/api/schema/rapid_fire.py`

### Seed loader (`[pending]`)

- `leap/seeds/loader.py` — implement upsert for `players` + `rapid_fire_questions` from JSON; wiki seed untouched.
- `leap/seeds/data/rapid_fire.json` — extend the existing 2-question fixture with the real 15 questions from `docs/rapid-fire.json` (after format conversion `option1..4` → `options[]`, add `category`, `time_limit_ms`).
- `leap/seeds/data/players.json` — new; pre-event roster.

### Dev tooling (`[pending]`)

- `pyproject.toml` — add `pytest`, `pytest-asyncio`, and `pytest-mock` to a dev dep group; tests live under `backend/tests/`.

## Settings

New / updated env vars:

| Var | Purpose | Default |
|---|---|---|
| `JWT_SECRET_KEY` | HS256 signing secret | required |
| `JWT_EXPIRE_HOURS` | Token lifetime hours | `24` |
| `EVENT_CODE` | Shared event code (plain) | required |

Existing kept: `POSTGRES_CONNECTION_STRING`, `LOG_LEVEL`, `ENVIRONMENT`, `API_HOST`, `API_PORT`, `API_WORKERS`, `API_WORKER_TIMEOUT`, `SEED_ON_STARTUP`.

## Domain Exceptions

All extend `BaseServiceException`. Code ranges: `1xxx` auth, `2xxx` game flow, `3xxx` content/config.

| Exception | Code | HTTP | When |
|---|---|---|---|
| `PlayerNotFoundException` | 1001 | 404 | `corp_id` not in players |
| `InvalidEventCodeException` | 1002 | 401 | Event code mismatch |
| `InvalidTokenException` | 1003 | 401 | JWT missing / malformed / expired |
| `SessionAlreadyExistsException` | 2001 | 409 | Duplicate start |
| `SessionNotFoundException` | 2002 | 404 | No active session for `(player_id, game_id)` |
| `SessionAlreadyCompletedException` | 2003 | 409 | Action on completed/abandoned session |
| `QuestionAlreadyAnsweredException` | 2004 | 409 | Replay attempt — `question_id` already in answers |
| `NoQuestionsAvailableException` | 3001 | 503 | No unanswered questions remain (pool exhausted) |

## Key Design Decisions

- Event code stored as plain env var with `secrets.compare_digest()` — see Appendix A1.
- Per-game session tables (`rapid_fire_answers` etc.) instead of a JSONB `session_data` blob on `game_sessions` — explicit schema per game. The AGENTS.md mention of `session_data` is from the older design and will be updated post-jam.
- Session ownership: DAOs are stateless, take `AsyncSession` per call. Service owns the session lifecycle per method. (Already implemented in `BasePgDAO`.)
- `/me/` path segment dropped from endpoints — identity is always implicit via JWT, there's only one session per player per game.
- Answer response = state response + evaluation fields. Same shape for `GET /state` and `POST /answer` (with extra `correct` + `correct_answer` on the latter).

## Open Edge Cases (executor to handle)

- Race condition on `start_session` — two concurrent POST requests for the same `(player_id, 'rapid_fire')`: the UNIQUE constraint catches it, both should not succeed.
- Rapid fire question pool exhausted before reaching `RAPID_FIRE_QUESTION_COUNT` — currently surfaces `NoQuestionsAvailableException`; alternative is to end the game early at whatever count was reached.
- Player abandons after answering 0 questions — score should be 0, status `abandoned`.

## Appendix

### A1 — Event code: plain env var vs bcrypt (rejected: bcrypt)

The shared event code is a one-day office event credential. Threat model: someone glances at someone else's screen or guesses; not an external password-spraying attack. The code lives only in server-side env vars, never in the frontend bundle. Hashing it with bcrypt provides no additional protection (the env var is the security boundary) and adds:

- A runtime dep on `bcrypt` / `passlib`
- ~100ms bcrypt cost per login (negligible at our scale, but worthless)
- Operational complexity (generating + storing a hash instead of the plain code)

`secrets.compare_digest()` against the plain string is constant-time and sufficient. Stayed with this.

### A2 — Why no DB fetch in `get_current_player` (rejected: per-request fetch)

DB fetch on every authenticated request would let us revoke a player mid-event by deleting their row, but:

- Players are pre-seeded; nobody gets unseeded mid-event in practice.
- Every API call would pay a redundant DB roundtrip (~1ms+) for no real-world benefit.
- The JWT already carries `display_name`, so there's no data we need.

Trade-off accepted: no revocation. If we ever need it, add the DB fetch then.

### A3 — Why no `current_question_id` field on session state

Persisting "the last question I served you" would require either a per-game session table for rapid fire or a JSONB column. We don't need it because:

- Scoring is correct/incorrect, not time-per-question
- Rehydration serving a different random unanswered question is functionally equivalent
- It removes a class of state-sync bugs

The replay-protection check ("this question_id has already been answered in this session") is sufficient.
