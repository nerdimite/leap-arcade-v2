# Sub-3: Types + DAOs + Scoring

**Status:** pending
**Depends on:** Sub-1 (model schema must be final before DAOs are written against it)
**Blocks:** Sub-4 (service imports all of these)

## Tasks

### 1. Update `leap/types/rapid_fire.py`

Replace the existing types to match the design spec:

- **`RapidFireQuestionDTO`** — verify fields: `id: str`, `question: str`, `options: List[str]`, `correct_option_index: int`, `category: str`, `time_limit_ms: int`. These are the internal cache type — `correct_option_index` is intentionally included (never serialized to client).

- **`RapidFireAnswerDTO`** — add `selected_option: Optional[int]` (null when skipped). Full shape: `id`, `game_session_id`, `question_id`, `correct`, `skipped`, `selected_option`, `time_ms`, `answered_at`.

- **`RapidFireResultDTO`** — rewrite to match design: `score: int`, `correct_count: int`, `wrong_count: int`, `skipped_count: int`, `time_taken_seconds: float`. Remove any stale fields (`total_questions`, `time_taken_ms`).

All three subclass `BaseLeapModel` with `from_attributes=True`.

### 2. Create `leap/dao/rapid_fire_question_dao.py`

One method only — this DAO exists solely for the startup cache load:

```python
async def get_all(self, session: AsyncSession) -> List[RapidFireQuestionDTO]:
    # SELECT * FROM rapid_fire_questions ORDER BY id
    # Returns all questions including correct_option_index
    # Called exactly once at startup — not at request time
```

Extend `BasePgDAO[RapidFireQuestion]`. Stub `_to_orm` and `_apply_filters` with `raise NotImplementedError` (read-only DAO).

### 3. Create `leap/dao/rapid_fire_answer_dao.py`

Three methods:

```python
async def create(
    self, session: AsyncSession,
    game_session_id: str, question_id: str,
    correct: bool, skipped: bool,
    selected_option: Optional[int], time_ms: int
) -> RapidFireAnswerDTO:
    # Inserts row; answered_at and id are server-generated
    # flush + refresh; return _to_dto(orm)

async def get_asked_question_ids(
    self, session: AsyncSession, game_session_id: str
) -> List[str]:
    # SELECT question_id FROM rapid_fire_answers WHERE game_session_id=$1
    # Lightweight — used in /play resume branch
    # Returns [] for a new session

async def get_all_for_session(
    self, session: AsyncSession, game_session_id: str
) -> List[RapidFireAnswerDTO]:
    # SELECT * FROM rapid_fire_answers WHERE game_session_id=$1 ORDER BY answered_at ASC
    # Used in submit_answer (asked_ids + scoring) and abandon
    # Returns [] for a new session
```

Extend `BasePgDAO[RapidFireAnswer]`. Stub `_to_orm` and `_apply_filters` with `raise NotImplementedError`.

### 4. Implement `leap/games/rapid_fire/scoring.py`

```python
def compute_rapid_fire_score(
    answers: List[RapidFireAnswerDTO],
    questions: Dict[str, RapidFireQuestionDTO],
) -> int:
    # Pure function — no DB access, fully deterministic
    # For each answer:
    #   skipped or not correct → 0 points
    #   correct → effective_time_ms = max(500, min(answer.time_ms, question.time_limit_ms))
    #             points = 50 + round((time_limit_ms - effective_time_ms) / time_limit_ms * 50)
    #             range: 50 (answered at buzzer) to 100 (answered instantly)
    # Returns sum of all points; minimum 0
    # Raises KeyError if answer.question_id not in questions — caller must guarantee cache is loaded
```

Write unit tests in `tests/unit/games/rapid_fire/test_scoring.py`:
- Correct answer at `time_ms=500` → 100 pts
- Correct answer at `time_ms=time_limit_ms` (15000) → 50 pts
- Correct answer at `time_ms=7500` (half time) → 75 pts
- Wrong answer → 0 pts
- Skipped answer → 0 pts
- All 15 correct at `time_ms=500` → 1500 total
- Empty answers list → 0
- `time_ms=0` clamped to 500 → 100 pts

## Acceptance Criteria

- `RapidFireAnswerDTO.selected_option` is present and `Optional[int]`
- `RapidFireResultDTO` has `wrong_count` (not just correct and skipped)
- `RapidFireQuestionDAO.get_all()` returns a list of DTOs with `correct_option_index`
- `RapidFireAnswerDAO.get_asked_question_ids()` returns only IDs; `get_all_for_session()` returns full DTOs
- All scoring unit tests pass

## Code References

- `leap/types/rapid_fire.py` — update existing
- `leap/dao/rapid_fire_question_dao.py` — new file
- `leap/dao/rapid_fire_answer_dao.py` — new file
- `leap/games/rapid_fire/scoring.py` — implement (was placeholder)
- `tests/unit/games/rapid_fire/test_scoring.py` — new test file

## Technical Guidelines

- DAOs follow the existing pattern in `game_session_dao.py`: `_to_dto` uses `model_validate(orm)`, `_to_orm` and `_apply_filters` raise `NotImplementedError`
- `get_all_for_session` orders by `answered_at ASC` — required for deterministic scoring and asked_ids derivation
- `compute_rapid_fire_score` takes the full `questions` dict (the in-memory cache) so it can look up `time_limit_ms` per question — callers pass `self._questions`
- No negative marks — wrong and skipped both return 0. `max(0, score)` guard at the end is a safeguard but should never trigger given the formula
- `correct_option_index` is 1-indexed in the DTO — scoring.py does not need to care about this (it only reads `correct` bool from answers, not the index)
