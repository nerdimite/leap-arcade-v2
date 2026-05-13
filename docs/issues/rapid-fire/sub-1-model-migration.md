# Sub-1: ORM Model Update + Alembic Migration

**Status:** pending
**Depends on:** nothing
**Blocks:** Sub-3 (DAOs build against the final schema)

## Tasks

- **Update `RapidFireAnswer` model** (`leap/dao/models/rapid_fire_answer.py`):
  - Add `selected_option: Mapped[int | None] = mapped_column(Integer, nullable=True)` — null when skipped
  - Add `UniqueConstraint("game_session_id", "question_id", name="uq_rfa_session_question")` to `__table_args__` alongside the existing index — this is the DB-level replay protection safety net

- **Verify `RapidFireQuestion` model** (`leap/dao/models/rapid_fire_question.py`):
  - Confirm columns match design: `id`, `question`, `options: ARRAY(String)`, `correct_option_index: Integer`, `category: String`, `time_limit_ms: Integer`, `created_at`
  - `correct_option_index` is **1-indexed** (1–4) — the model has no CHECK constraint for this; that's intentional (enforced at application layer)
  - No changes needed beyond verification

- **Stale migration cleanup + fresh migration**:
  - Check `backend/alembic/versions/` for the stale scaffold migration `0de1443cd0f2_initial.py` — delete it if present
  - Run `uv run alembic revision --autogenerate -m "rapid fire schema"` from `backend/`
  - Inspect the generated file — confirm it creates `rapid_fire_questions`, `rapid_fire_answers`, and the UNIQUE constraint; confirm it does not touch wiki/picture/four_pics/crossword tables
  - Run `uv run alembic upgrade head` and verify it applies cleanly against a running Postgres (`docker compose up -d postgres`)

## Acceptance Criteria

- `rapid_fire_answers` table has a `selected_option` INTEGER nullable column
- `rapid_fire_answers` has a UNIQUE constraint on `(game_session_id, question_id)`
- Migration applies cleanly from a clean database with no errors
- `dao/models/__init__.py` imports only the 4 in-scope models (Player, GameSession, RapidFireQuestion, RapidFireAnswer) — verify it does, fix if not

## Code References

- `leap/dao/models/rapid_fire_answer.py` — primary change
- `leap/dao/models/rapid_fire_question.py` — verify only
- `leap/dao/models/__init__.py` — verify only
- `backend/alembic/versions/` — delete stale, generate new

## Technical Guidelines

- `__table_args__` must be a tuple when adding both an Index and a UniqueConstraint — `(Index(...), UniqueConstraint(...),)`
- Do not add a CHECK constraint on `correct_option_index` range — the service enforces it at the application layer
- The `selected_option` column stores what the player actually clicked (1–4) or null for skipped — it is clamped and validated before insert, not at the DB level
