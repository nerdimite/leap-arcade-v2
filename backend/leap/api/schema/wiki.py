"""HTTP API schemas — Wikipedia Speed Run."""

from typing import Annotated, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from leap.types.wiki import WikiPuzzleAttemptStatus


class WikiPuzzleResultSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    round_id: str
    puzzle_index: int
    clue: str
    target_title: str
    optimal_click_count: int
    steps_taken: int
    time_ms: Optional[int] = None
    score: int
    status: WikiPuzzleAttemptStatus


class WikiActivePuzzleSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    game_session_id: str
    attempt_id: str
    round_id: str
    puzzle_index: int
    puzzle_count: int
    clue: str
    current_title: str
    time_limit_ms: int
    time_remaining_ms: int
    steps_taken: int
    click_path: List[str]
    article_html: str
    back_enabled: bool


class WikiPlayActiveResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    state: Literal["active"] = "active"
    total_score: int
    completed_count: int
    current: WikiActivePuzzleSchema
    completed_attempts: List[WikiPuzzleResultSchema]


class WikiPlayTerminalResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    state: Literal["completed", "abandoned"]
    total_score: int
    results: List[WikiPuzzleResultSchema]


WikiPlayResponse = Annotated[
    Union[WikiPlayActiveResponse, WikiPlayTerminalResponse],
    Field(discriminator="state"),
]


class WikiNavigateRequestSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str


class WikiNavigateActiveResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    state: Literal["active"] = "active"
    current: WikiActivePuzzleSchema


class WikiNavigatePuzzleCompletedResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    state: Literal["puzzle_completed"] = "puzzle_completed"
    puzzle_result: WikiPuzzleResultSchema
    next_puzzle_available: bool
    total_score: int


WikiNavigateResponse = Annotated[
    Union[WikiNavigateActiveResponse, WikiNavigatePuzzleCompletedResponse],
    Field(discriminator="state"),
]


def wiki_play_to_response(payload) -> WikiPlayActiveResponse | WikiPlayTerminalResponse:
    from leap.types.wiki import WikiPlayActiveDTO, WikiPlayTerminalDTO

    if isinstance(payload, WikiPlayActiveDTO):
        return WikiPlayActiveResponse(
            total_score=payload.total_score,
            completed_count=payload.completed_count,
            current=WikiActivePuzzleSchema.model_validate(payload.current.model_dump()),
            completed_attempts=[
                WikiPuzzleResultSchema.model_validate(r.model_dump())
                for r in payload.completed_attempts
            ],
        )
    if isinstance(payload, WikiPlayTerminalDTO):
        return WikiPlayTerminalResponse(
            state=payload.state,
            total_score=payload.total_score,
            results=[
                WikiPuzzleResultSchema.model_validate(r.model_dump()) for r in payload.results
            ],
        )
    raise TypeError(f"Unsupported wiki play payload: {type(payload)!r}")


def wiki_navigate_to_response(
    payload,
) -> WikiNavigateActiveResponse | WikiNavigatePuzzleCompletedResponse:
    from leap.types.wiki import WikiNavigateActiveDTO, WikiNavigatePuzzleCompletedDTO

    if isinstance(payload, WikiNavigateActiveDTO):
        return WikiNavigateActiveResponse(
            current=WikiActivePuzzleSchema.model_validate(payload.current.model_dump()),
        )
    if isinstance(payload, WikiNavigatePuzzleCompletedDTO):
        return WikiNavigatePuzzleCompletedResponse(
            puzzle_result=WikiPuzzleResultSchema.model_validate(payload.puzzle_result.model_dump()),
            next_puzzle_available=payload.next_puzzle_available,
            total_score=payload.total_score,
        )
    raise TypeError(f"Unsupported wiki navigate payload: {type(payload)!r}")
