"""Wikipedia Speed Run domain types (shared by DAOs and services)."""

from datetime import datetime
from enum import Enum
from typing import List, Literal, Optional, Union

from leap.types import BaseLeapModel


class WikiPuzzleAttemptStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    TIMED_OUT = "timed_out"
    ABANDONED = "abandoned"


class WikiRoundDTO(BaseLeapModel):
    id: str
    sequence_index: int
    start_title: str
    start_url: str
    target_title: str
    target_url: str
    clue: str
    optimal_click_count: int
    solution_path: List[str]
    time_limit_ms: int


class WikiPuzzleAttemptDTO(BaseLeapModel):
    id: str
    game_session_id: str
    round_id: str
    status: WikiPuzzleAttemptStatus
    current_title: str
    click_path: List[str]
    steps_taken: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    time_ms: Optional[int] = None
    score: Optional[int] = None


class WikiArticleDTO(BaseLeapModel):
    requested_title: str
    canonical_title: str
    html: str


class WikiPuzzleResultDTO(BaseLeapModel):
    round_id: str
    puzzle_index: int
    clue: str
    target_title: str
    optimal_click_count: int
    steps_taken: int
    time_ms: Optional[int] = None
    score: int
    status: WikiPuzzleAttemptStatus


class WikiActivePuzzleDTO(BaseLeapModel):
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


class RewrittenWikiHtmlDTO(BaseLeapModel):
    html: str
    internal_link_titles: List[str]
    removed_link_count: int


class WikiPlayActiveDTO(BaseLeapModel):
    state: Literal["active"] = "active"
    total_score: int
    completed_count: int
    current: WikiActivePuzzleDTO
    completed_attempts: List[WikiPuzzleResultDTO]


class WikiPlayTerminalDTO(BaseLeapModel):
    state: Literal["completed", "abandoned"]
    total_score: int
    results: List[WikiPuzzleResultDTO]


WikiPlayPayload = Union[WikiPlayActiveDTO, WikiPlayTerminalDTO]


class WikiNavigateActiveDTO(BaseLeapModel):
    state: Literal["active"] = "active"
    current: WikiActivePuzzleDTO


class WikiNavigatePuzzleCompletedDTO(BaseLeapModel):
    state: Literal["puzzle_completed"] = "puzzle_completed"
    puzzle_result: WikiPuzzleResultDTO
    next_puzzle_available: bool
    total_score: int


WikiNavigatePayload = Union[WikiNavigateActiveDTO, WikiNavigatePuzzleCompletedDTO]
