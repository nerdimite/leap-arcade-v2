# Sub-5: API Schemas + Route Handlers

**Status:** pending
**Depends on:** Sub-4 (service must exist; schemas map to service return types)
**Blocks:** nothing (this is the outermost layer)

## Tasks

### 1. Create `leap/api/schema/rapid_fire.py`

Define all six shapes. Use `BaseModel` (not `BaseLeapModel` — schemas are API boundary types, not internal domain types).

**`QuestionSchema`**
```python
class QuestionSchema(BaseModel):
    id: str
    question: str           # field named "question" not "text"
    options: List[str]      # 4-element list; correct_option_index deliberately absent
    time_limit_ms: int
```

**`ResultSchema`** (reused across all three responses)
```python
class ResultSchema(BaseModel):
    score: int
    correct_count: int
    wrong_count: int
    skipped_count: int
    time_taken_seconds: float
```

**`PlayResponse`** (discriminated on `status`)
```python
class PlayResponse(BaseModel):
    status: str                          # "active" | "completed" | "abandoned"
    game_session_id: Optional[str] = None
    questions_answered: Optional[int] = None
    questions_total: Optional[int] = None
    question: Optional[QuestionSchema] = None
    result: Optional[ResultSchema] = None
```
Active branch populates: `game_session_id`, `questions_answered`, `questions_total`, `question`.
Completed/abandoned branch populates: `result` only.

**`AnswerRequest`**
```python
class AnswerRequest(BaseModel):
    question_id: str
    selected_option: Optional[int] = None   # null = timer expired (skipped)
    time_ms: int

    @field_validator("selected_option")
    @classmethod
    def validate_selected_option(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v not in (1, 2, 3, 4):
            raise ValueError("selected_option must be 1, 2, 3, or 4")
        return v
```

**`AnswerResponse`**
```python
class AnswerResponse(BaseModel):
    correct: bool
    correct_option: int                      # 1-indexed
    correct_answer_text: str
    current_score: int
    questions_answered: int
    questions_remaining: int
    next_question: Optional[QuestionSchema] = None
    result: Optional[ResultSchema] = None    # populated only when next_question is None
```

**`AbandonResponse`**
```python
class AbandonResponse(BaseModel):
    result: ResultSchema
```

### 2. Implement `leap/api/routes/games/rapid_fire.py`

Replace the three `raise NotImplementedError` stubs:

**`play()`**
```python
@router.post("/play", response_model=PlayResponse)
async def play(
    player: CurrentPlayer = Depends(get_current_player),
    container: ServiceContainer = Depends(get_container),
) -> PlayResponse:
    return await container.rapid_fire.play(player.id)
```
The service returns a `PlayResponse`-shaped object. Map `RapidFireQuestionDTO` → `QuestionSchema` (exclude `correct_option_index`, `category`) and `RapidFireResultDTO` → `ResultSchema` in the service, or build the schema objects in the route. Keep the route thin — if mapping is needed, prefer doing it in the service and returning the schema type directly, or use a dedicated `_to_play_response()` helper on the service.

**`answer()`**
```python
@router.post("/answer", response_model=AnswerResponse)
async def answer(
    body: AnswerRequest,
    player: CurrentPlayer = Depends(get_current_player),
    container: ServiceContainer = Depends(get_container),
) -> AnswerResponse:
    return await container.rapid_fire.submit_answer(
        player.id, body.question_id, body.selected_option, body.time_ms
    )
```

**`abandon()`**
```python
@router.post("/abandon", response_model=AbandonResponse)
async def abandon(
    player: CurrentPlayer = Depends(get_current_player),
    container: ServiceContainer = Depends(get_container),
) -> AbandonResponse:
    return await container.rapid_fire.abandon(player.id)
```

Remove the existing `/start` and `/state` stubs — they are superseded by `/play`.

## Acceptance Criteria

- `POST /games/rapid-fire/play` returns 200 with `status="active"` and a `question` for a new player (no request body)
- `POST /games/rapid-fire/answer` returns 200 with `correct`, `current_score`, and `next_question` for a mid-game submission
- `POST /games/rapid-fire/answer` returns `next_question=null` and a `result` block on the last question
- `POST /games/rapid-fire/answer` with `selected_option=5` returns 422
- `POST /games/rapid-fire/abandon` returns 200 with `result.score` reflecting answers submitted so far
- `correct_option_index` is absent from all API responses (QuestionSchema excludes it)
- The old `/start` and `/state` stubs are removed from the router

## Code References

- `leap/api/schema/rapid_fire.py` — new file
- `leap/api/routes/games/rapid_fire.py` — rewrite existing stubs
- `leap/api/deps.py` — reference for `get_current_player`, `get_container` (no changes)
- `leap/api/main.py` — verify route prefix `/games/rapid-fire` is registered (no change expected)

## Technical Guidelines

- `QuestionSchema` must never include `correct_option_index` — if mapping from `RapidFireQuestionDTO`, explicitly exclude it rather than using `model_validate` directly on the internal DTO
- The `field_validator` on `AnswerRequest.selected_option` uses Pydantic v2 syntax (`@field_validator` + `@classmethod`) — do not use the v1 `@validator` decorator
- Routes are thin wiring only — no business logic, no direct DAO calls, no exception handling. Service exceptions bubble up to the global handler in `main.py`
- `status` values in `PlayResponse` must exactly match `GameSessionStatus` enum values: `"active"`, `"completed"`, `"abandoned"` — these are what the frontend keys on
