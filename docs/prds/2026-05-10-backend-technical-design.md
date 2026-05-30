# Backend Technical Design

**Scope:** Wikipedia Speed Run + Rapid Fire Quiz (Phase 1)
**Stack:** FastAPI · SQLAlchemy 2.0 async · PostgreSQL · JWT auth
**Date:** 2026-05-10

---

## 1. Database Schema

### `players`

```sql
CREATE TABLE players (
    id          TEXT PRIMARY KEY,          -- normalised corp_id (lowercase + trimmed)
    display_name TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### `game_sessions`

Score ledger — one row per player per game. The leaderboard aggregates this table.

```sql
CREATE TABLE game_sessions (
    id           TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    player_id    TEXT NOT NULL REFERENCES players(id),
    game_id      TEXT NOT NULL,            -- 'wiki' | 'rapid_fire' | ...
    status       TEXT NOT NULL DEFAULT 'active',  -- 'active' | 'completed' | 'abandoned'
    score        INTEGER,                  -- null until completed/abandoned
    started_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ,

    UNIQUE (player_id, game_id),
    CHECK (status IN ('active', 'completed', 'abandoned')),
    CHECK (game_id IN ('wiki', 'rapid_fire'))
);
```

Leaderboard query:

```sql
SELECT
    gs.player_id,
    p.display_name,
    SUM(gs.score) AS total_score,
    COUNT(*) AS games_completed,
    MIN(gs.completed_at) AS first_completion
FROM game_sessions gs
JOIN players p ON p.id = gs.player_id
WHERE gs.status = 'completed'
GROUP BY gs.player_id, p.display_name
ORDER BY total_score DESC, first_completion ASC;
```

### `wiki_rounds`

Content table. One row per challenge (start/target pair). One row marked `is_active = true` at event time.

```sql
CREATE TABLE wiki_rounds (
    id            TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    start_page    TEXT NOT NULL,           -- Wikipedia page title
    target_page   TEXT NOT NULL,           -- Wikipedia page title
    optimal_steps INTEGER,                 -- for bonus scoring
    difficulty    TEXT NOT NULL DEFAULT 'medium',
    is_active     BOOLEAN NOT NULL DEFAULT false,
    hints         TEXT[] NOT NULL DEFAULT '{}',  -- ordered free-text hints; indexed by hints_used
    notes         TEXT,

    CHECK (difficulty IN ('easy', 'medium', 'hard'))
);
```

Service picks the active round: `SELECT * FROM wiki_rounds WHERE is_active = true LIMIT 1`.

### `wiki_sessions`

One row per player. All wiki gameplay state lives here.

```sql
CREATE TABLE wiki_sessions (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    game_session_id TEXT NOT NULL REFERENCES game_sessions(id),
    round_id        TEXT NOT NULL REFERENCES wiki_rounds(id),
    click_path      TEXT[] NOT NULL DEFAULT '{}',   -- ordered visited titles; seeded with [start_page]
    current_page    TEXT NOT NULL,                   -- page currently rendered for this player
    hints_used      INTEGER NOT NULL DEFAULT 0,

    UNIQUE (game_session_id)
);
```

### `rapid_fire_questions`

Question pool.

```sql
CREATE TABLE rapid_fire_questions (
    id            TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    question_text TEXT NOT NULL,
    question_type TEXT NOT NULL,           -- 'mcq' | 'typed'
    options       TEXT[],                  -- nullable; MCQ only
    correct_answer TEXT NOT NULL,
    difficulty    TEXT NOT NULL DEFAULT 'medium',
    category      TEXT NOT NULL,           -- topic grouping for potential filtering
    time_limit_ms INTEGER NOT NULL,        -- per-question display countdown for client

    CHECK (question_type IN ('mcq', 'typed')),
    CHECK (difficulty IN ('easy', 'medium', 'hard'))
);
```

### `rapid_fire_answers`

One row per question answered. FKs directly to `game_sessions` — no intermediate session table.

```sql
CREATE TABLE rapid_fire_answers (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    game_session_id TEXT NOT NULL REFERENCES game_sessions(id),
    question_id     TEXT NOT NULL REFERENCES rapid_fire_questions(id),
    correct         BOOLEAN NOT NULL,
    skipped         BOOLEAN NOT NULL DEFAULT false,  -- true when auto-advanced by timer
    time_ms         INTEGER NOT NULL,               -- ms from question display to answer
    answered_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Already-served question tracking: `SELECT question_id FROM rapid_fire_answers WHERE game_session_id = $1`.

---

## 2. SQLAlchemy Models

File locations: `leap/dao/models/<table>.py`

### `player.py`

```python
class Player(Base):
    __tablename__ = "players"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    display_name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
```

### `game_session.py`

```python
class GameSession(Base):
    __tablename__ = "game_sessions"
    __table_args__ = (
        UniqueConstraint("player_id", "game_id", name="uq_game_sessions_player_game"),
        CheckConstraint("status IN ('active','completed','abandoned')", ...),
        CheckConstraint("game_id IN ('wiki','rapid_fire')", ...),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, server_default=...)
    player_id: Mapped[str] = mapped_column(String, ForeignKey("players.id"), nullable=False)
    game_id: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, server_default=text("'active'"), nullable=False)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
```

### `wiki_round.py`

```python
class WikiRound(Base):
    __tablename__ = "wiki_rounds"

    id: Mapped[str] = ...
    start_page: Mapped[str] = ...
    target_page: Mapped[str] = ...
    optimal_steps: Mapped[int | None] = ...
    difficulty: Mapped[str] = ...
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("false"), nullable=False)
    hints: Mapped[list[str]] = mapped_column(ARRAY(String), server_default=text("'{}'"), nullable=False)
    notes: Mapped[str | None] = ...
```

### `wiki_session.py`

```python
class WikiSession(Base):
    __tablename__ = "wiki_sessions"
    __table_args__ = (UniqueConstraint("game_session_id", ...),)

    id: Mapped[str] = ...
    game_session_id: Mapped[str] = mapped_column(String, ForeignKey("game_sessions.id"), nullable=False)
    round_id: Mapped[str] = mapped_column(String, ForeignKey("wiki_rounds.id"), nullable=False)
    click_path: Mapped[list[str]] = mapped_column(ARRAY(String), server_default=text("'{}'"), nullable=False)
    current_page: Mapped[str] = mapped_column(String, nullable=False)
    hints_used: Mapped[int] = mapped_column(Integer, server_default=text("0"), nullable=False)
```

### `rapid_fire_question.py`

```python
class RapidFireQuestion(Base):
    __tablename__ = "rapid_fire_questions"

    id: Mapped[str] = ...
    question_text: Mapped[str] = ...
    question_type: Mapped[str] = ...          # 'mcq' | 'typed'
    options: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    correct_answer: Mapped[str] = ...
    difficulty: Mapped[str] = ...
    category: Mapped[str] = ...
    time_limit_ms: Mapped[int] = ...
```

### `rapid_fire_answer.py`

```python
class RapidFireAnswer(Base):
    __tablename__ = "rapid_fire_answers"

    id: Mapped[str] = ...
    game_session_id: Mapped[str] = mapped_column(String, ForeignKey("game_sessions.id"), nullable=False)
    question_id: Mapped[str] = mapped_column(String, ForeignKey("rapid_fire_questions.id"), nullable=False)
    correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    skipped: Mapped[bool] = mapped_column(Boolean, server_default=text("false"), nullable=False)
    time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    answered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
```

---

## 3. API Endpoints

### Auth

| Method | Path | Auth required | Description |
|---|---|---|---|
| `POST` | `/auth/login` | No | Verify corp_id + event_code, issue JWT |
| `POST` | `/auth/logout` | Yes | No-op server-side; client drops token |

### Lobby

| Method | Path | Description |
|---|---|---|
| `GET` | `/lobby` | Returns game list with player's status per game |

### Leaderboard

| Method | Path | Description |
|---|---|---|
| `GET` | `/leaderboard` | Ranked aggregate scores across all players |

### Wiki

| Method | Path | Description |
|---|---|---|
| `POST` | `/games/wiki/sessions` | Start a wiki session; returns session + proxied start page HTML |
| `GET` | `/games/wiki/sessions/me` | Rehydrate active session (on refresh) |
| `GET` | `/games/wiki/page` | Navigate to a page (`?title=`); logs step, checks target, returns proxied HTML |
| `POST` | `/games/wiki/sessions/me/hint` | Request a hint; increments `hints_used`, returns hint text |
| `POST` | `/games/wiki/sessions/me/abandon` | Forfeit; locks score at 0, status → abandoned |

### Rapid Fire

| Method | Path | Description |
|---|---|---|
| `POST` | `/games/rapid-fire/sessions` | Start a session; returns `game_session_id` + first question |
| `GET` | `/games/rapid-fire/sessions/me` | Rehydrate active session |
| `POST` | `/games/rapid-fire/sessions/me/answer` | Submit answer; returns result + next question (or null if done) |
| `POST` | `/games/rapid-fire/sessions/me/abandon` | Forfeit; scores accumulated answers, status → abandoned |

---

## 4. DTO Shapes (Pydantic)

### Auth

```python
class LoginRequest(BaseModel):
    corp_id: str
    event_code: str

class PlayerDTO(BaseModel):
    id: str          # normalised corp_id
    display_name: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    player: PlayerDTO
```

### Lobby

```python
class GameStatusDTO(BaseModel):
    game_id: str          # 'wiki' | 'rapid_fire' | ...
    display_name: str     # 'Wikipedia Speed Run' | 'Rapid Fire Quiz' | ...
    status: str           # 'not_started' | 'active' | 'completed' | 'abandoned'
    score: int | None

class LobbyResponse(BaseModel):
    player: PlayerDTO
    games: list[GameStatusDTO]
```

### Leaderboard

```python
class LeaderboardEntryDTO(BaseModel):
    rank: int
    player_id: str
    display_name: str
    total_score: int
    games_completed: int

class LeaderboardResponse(BaseModel):
    entries: list[LeaderboardEntryDTO]
```

### Wiki

```python
class WikiSessionStartResponse(BaseModel):
    game_session_id: str
    wiki_session_id: str
    round: WikiRoundDTO           # start_page, target_page, optimal_steps
    current_page: str
    click_path: list[str]
    hints_used: int
    page_content: str             # proxied + rewritten HTML

class WikiRoundDTO(BaseModel):
    start_page: str
    target_page: str
    optimal_steps: int | None

class WikiPageResponse(BaseModel):
    page_title: str
    page_content: str             # proxied + rewritten HTML
    click_path: list[str]
    steps_taken: int
    target_reached: bool
    result: WikiResultDTO | None  # populated only when target_reached=True

class WikiResultDTO(BaseModel):
    score: int
    steps_taken: int
    hints_used: int
    time_taken_seconds: float
    optimal_path_bonus: bool
    no_hints_bonus: bool

class WikiHintResponse(BaseModel):
    hint_text: str
    hints_used: int               # updated total (after this request)
    hints_remaining: int          # len(round.hints) - hints_used
    penalty: int                  # flat points deducted per hint
```

### Rapid Fire

```python
class QuestionDTO(BaseModel):
    id: str
    question_text: str
    question_type: str            # 'mcq' | 'typed'
    options: list[str] | None
    time_limit_ms: int

class RapidFireSessionStartResponse(BaseModel):
    game_session_id: str
    started_at: datetime
    first_question: QuestionDTO

class RapidFireAnswerRequest(BaseModel):
    question_id: str
    answer: str                   # empty string for skipped questions
    skipped: bool = False
    time_ms: int                  # client-measured ms; stored as-is

class RapidFireAnswerResponse(BaseModel):
    correct: bool
    correct_answer: str
    current_score: int            # running total computed from all answers so far
    next_question: QuestionDTO | None   # null when no more questions remain
    questions_answered: int
    questions_remaining: int      # based on RAPID_FIRE_QUESTION_COUNT config

class RapidFireResultDTO(BaseModel):
    score: int
    questions_answered: int
    correct_count: int
    skipped_count: int
    time_taken_seconds: float
```

---

## 5. DAO Layer

One DAO class per table, in `leap/dao/pg/`. All extend `BasePgDAO`. All return dicts (via `_to_dto`), never ORM instances.

### `PlayerDAO`

```
get_by_id(corp_id) → dict | None
```

### `GameSessionDAO`

```
create(player_id, game_id) → dict
get_by_player_and_game(player_id, game_id) → dict | None
update_score_and_complete(id, score) → dict
update_status(id, status, score=None) → dict
get_leaderboard() → list[dict]          # runs the aggregate query
```

### `WikiRoundDAO`

```
get_active_round() → dict | None        # WHERE is_active = true LIMIT 1
```

### `WikiSessionDAO`

```
create(game_session_id, round_id, start_page) → dict
get_by_game_session(game_session_id) → dict | None
append_click(id, page_title) → dict     # array_append on click_path, update current_page
increment_hints(id) → dict
```

### `RapidFireQuestionDAO`

```
get_random_excluding(exclude_ids: list[str]) → dict | None
get_question_count() → int
```

### `RapidFireAnswerDAO`

```
create(game_session_id, question_id, correct, skipped, time_ms) → dict
get_asked_question_ids(game_session_id) → list[str]
get_all_for_session(game_session_id) → list[dict]  # for scoring
```

---

## 6. Service Layer

One service per domain in `leap/games/<game>/service.py` (for games) and `leap/service/` (for cross-cutting).

### `AuthService` (`leap/service/auth_service.py`)

```
login(corp_id, event_code) → LoginResponse
  1. Normalise corp_id: lowercase + strip
  2. Fetch player by id → 404 PlayerNotFoundException if not found
  3. bcrypt.checkpw(event_code, ENV[EVENT_CODE_HASH]) → 401 InvalidEventCodeException if mismatch
  4. Issue JWT: {sub: corp_id, display_name, iat, exp: now + JWT_EXPIRE_HOURS}
  5. Return LoginResponse(access_token, player: PlayerDTO)

logout() → void
  No-op. Server does nothing. Client is responsible for dropping the token.
```

### `LobbyService` (`leap/service/lobby_service.py`)

```
get_lobby(player_id, display_name) → LobbyResponse
  1. Fetch all game_sessions for player (one per game_id)
  2. For each entry in GAMES (from leap/config/constants.py):
     - Look up session row by game_id; default to 'not_started' if absent
     - Build GameStatusDTO with display_name from GAMES registry
  3. Return PlayerDTO (from JWT claims) + games list
```

No DB fetch for the player row — `display_name` comes from the JWT claim via `CurrentPlayer`.

### `LeaderboardService` (`leap/service/leaderboard_service.py`)

```
get_leaderboard() → LeaderboardResponse
  1. Run aggregate query via GameSessionDAO.get_leaderboard()
  2. Attach rank (row number)
  3. Return entries
```

### `WikiService` (`leap/games/wiki/service.py`)

```
start_session(player_id) → WikiSessionStartResponse
  1. Check game_sessions for (player_id, 'wiki') → 409 if exists
  2. Get active wiki round → 503 if none configured
  3. Create game_sessions row
  4. Create wiki_sessions row (click_path=[start_page], current_page=start_page)
  5. Proxy + transform start_page HTML via WikiProxy
  6. Return session state + HTML

navigate(player_id, page_title) → WikiPageResponse
  1. Fetch active wiki_session for player → 404 if none / 409 if completed
  2. Validate page_title is not the same as current_page (no self-links)
  3. Fetch + proxy page HTML
  4. append_click on wiki_session
  5. Check if page_title == round.target_page
     - If yes: compute score → update game_sessions (completed) → return with result
     - If no: return updated state + HTML

request_hint(player_id) → WikiHintResponse
  1. Fetch active session + round
  2. Guard: hints_used >= len(round.hints) → 400 "no more hints available"
  3. Retrieve round.hints[hints_used]
  4. increment_hints on wiki_session
  5. Return hint_text + updated hints_used + hints_remaining + flat penalty

abandon(player_id) → void
  1. Fetch active session → 404 if none
  2. update_status(game_session_id, 'abandoned', score=0)
```

### `RapidFireService` (`leap/games/rapid_fire/service.py`)

```
start_session(player_id) → RapidFireSessionStartResponse
  1. Check game_sessions for (player_id, 'rapid_fire') → 409 if exists
  2. Create game_sessions row
  3. Pick first question: get_random_excluding([])
  4. Return session + first question

submit_answer(player_id, question_id, answer, skipped, time_ms) → RapidFireAnswerResponse
  1. Fetch game_session for (player_id, 'rapid_fire') → 404/409 guards
  2. Get asked_question_ids; validate question_id is the last served (not a replay)
  3. Validate answer against rapid_fire_questions.correct_answer (case-insensitive strip)
  4. Insert rapid_fire_answers row
  5. Compute current_score from all answers (scoring formula in scoring.py)
  6. Check if questions_answered == RAPID_FIRE_QUESTION_COUNT (env var, default 10)
     - If done: update game_sessions (completed, score=final_score)
     - Return next_question=null + result
  7. Otherwise: pick next question (get_random_excluding(asked_ids))
  8. Return answer result + next_question

abandon(player_id) → void
  1. Fetch active session
  2. Score accumulated answers via scoring module
  3. update_status(game_session_id, 'abandoned', score=computed_score)
```

---

## 7. Scoring Modules

Each game has `leap/games/<game>/scoring.py`. Scoring is pure functions — no DB access, takes plain dicts.

### `leap/games/wiki/scoring.py`

```python
def compute_wiki_score(
    steps_taken: int,
    time_taken_seconds: float,
    hints_used: int,
    optimal_steps: int | None,
) -> tuple[int, bool, bool]:
    """Returns (score, optimal_path_bonus, no_hints_bonus)."""
    base = 1000
    score = base - (time_taken_seconds * 2) - (steps_taken * 5) - (hints_used * 50)
    optimal_bonus = optimal_steps is not None and steps_taken <= optimal_steps
    no_hints_bonus = hints_used == 0
    if optimal_bonus:
        score += 200
    if no_hints_bonus:
        score += 100
    return max(0, int(score)), optimal_bonus, no_hints_bonus
```

### `leap/games/rapid_fire/scoring.py`

```python
def compute_rapid_fire_score(answers: list[dict]) -> int:
    """answers: list of {correct, skipped, time_ms}"""
    score = 0
    for a in answers:
        if a["skipped"]:
            continue
        if a["correct"]:
            score += 50
        else:
            score -= 10
    return max(0, score)
```

> Note: streak bonus (+100 per 5 correct in a row) is client-side display only and not factored into server score. Time bonus formula TBD during game logic implementation.

---

## 8. Auth Middleware

`leap/api/deps.py` — `get_current_player` dependency.

**No DB fetch per request.** Player identity is derived entirely from the JWT claims. The token is trusted if it is valid and non-expired.

```python
class CurrentPlayer(BaseModel):
    id: str           # corp_id (normalised)
    display_name: str

async def get_current_player(
    token: str = Depends(oauth2_scheme),
) -> CurrentPlayer:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return CurrentPlayer(
        id=payload["sub"],
        display_name=payload["display_name"],
    )
```

All protected endpoints inject `player: CurrentPlayer = Depends(get_current_player)`.

### Service call pattern (session ownership)

Every service method that touches the DB owns its session via `ContextManager.session()`. DAO calls share that session for atomicity:

```python
async def some_service_method(self, player_id: str) -> ...:
    async with self._context_manager.session() as session:
        row_a = await self._dao_a.create(session, ...)
        row_b = await self._dao_b.create(session, ...)  # same transaction
        return ...
```

Never open multiple `context_manager.session()` blocks in one service method.

---

## 9. Wikipedia Proxy

`leap/games/wiki/proxy.py`

```
fetch_and_transform(page_title: str, session_id: str) -> str
  1. GET https://en.wikipedia.org/api/rest_v1/page/html/{title}
  2. Parse with BeautifulSoup, extract #mw-content-text only
  3. Rewrite all <a href="/wiki/X"> → <a href="/games/wiki/page?title=X&session={session_id}">
  4. Strip: navboxes, infoboxes, external links, edit links, references section
  5. Return cleaned HTML string
```

The client renders this via `dangerouslySetInnerHTML`. Every link click hits `GET /games/wiki/page?title=`.

---

## 10. Config / Env Vars

| Var | Purpose | Default |
|---|---|---|
| `POSTGRES_CONNECTION_STRING` | Postgres connection string | required |
| `JWT_SECRET_KEY` | JWT signing key (HS256) | required |
| `JWT_EXPIRE_HOURS` | Token lifetime in hours | `24` |
| `EVENT_CODE_HASH` | bcrypt hash of the shared event code | required |
| `RAPID_FIRE_QUESTION_COUNT` | Questions per rapid fire session | `10` |
| `SEED_ON_STARTUP` | Run seed script on boot | `true` |
| `ENVIRONMENT` | `development` \| `production` | `development` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |

---

## 11. Constants (`leap/config/constants.py`)

Single source of truth for values that are config-like but not env vars.

```python
GAMES = [
    {"id": "wiki",       "display_name": "Wikipedia Speed Run"},
    {"id": "rapid_fire", "display_name": "Rapid Fire Quiz"},
    {"id": "picture",    "display_name": "Picture Illustration"},
    {"id": "four_pics",  "display_name": "Four Pics One Lie"},
    {"id": "crossword",  "display_name": "Crossword"},
]

GAME_IDS = [g["id"] for g in GAMES]
```

`LobbyService` imports `GAMES` for the game registry.
`GameSession` CHECK constraint uses `GAME_IDS` for the `game_id` column.

---

## 12. Seed Data Structure



`leap/seeds/` — JSON files loaded by `loader.py` at startup when `SEED_ON_STARTUP=true`.

```
seeds/
  players.json          → [{id, display_name}]
  wiki_rounds.json      → [{start_page, target_page, optimal_steps, difficulty, is_active, hints: [...]}]
  rapid_fire_questions.json  → [{question_text, question_type, options, correct_answer, difficulty, category, time_limit_ms}]
```

---

## 13. Domain Exceptions

All service exceptions extend `BaseServiceException` from `leap/service/exceptions.py`. Routes never raise `HTTPException` directly — the global handler in `leap/api/main.py` converts `BaseServiceException` to a JSON error response.

Error code ranges:
- `1xxx` — Auth errors
- `2xxx` — Session / game flow errors
- `3xxx` — Content / configuration errors
- `5xxx` — Unexpected server errors

### Auth

| Exception | Code | HTTP | When |
|---|---|---|---|
| `PlayerNotFoundException` | `1001` | 404 | `corp_id` not found in players table |
| `InvalidEventCodeException` | `1002` | 401 | Event code bcrypt check fails |
| `InvalidTokenException` | `1003` | 401 | JWT missing, malformed, or expired |

### Game Sessions

| Exception | Code | HTTP | When |
|---|---|---|---|
| `SessionAlreadyExistsException` | `2001` | 409 | Player tries to start a game they already started |
| `SessionNotFoundException` | `2002` | 404 | No active session found for this player + game |
| `SessionAlreadyCompletedException` | `2003` | 409 | Action attempted on a completed/abandoned session |
| `NoMoreHintsException` | `2004` | 400 | `hints_used >= len(round.hints)` |

### Content / Configuration

| Exception | Code | HTTP | When |
|---|---|---|---|
| `NoActiveRoundException` | `3001` | 503 | Wiki started but no `is_active=true` round configured |
| `NoQuestionsAvailableException` | `3002` | 503 | Rapid fire can't find an unasked question |

---

## 14. Open Items

- Wiki scoring time bonus: formula not finalised — deferred to game logic implementation.
- Rapid fire time bonus: `time_taken_seconds` → scoring impact TBD.
- Wiki hint text generation: currently assumed to be authored inline in seed data (e.g. `hint_category`, `hint_intermediate` columns on `wiki_rounds`). To be confirmed.
- Question count for rapid fire: `RAPID_FIRE_QUESTION_COUNT=10` assumed; revisit once question pool size is known.
