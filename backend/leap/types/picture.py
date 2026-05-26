"""Picture Illustration game domain types."""

from datetime import datetime
from typing import List, Literal, Optional

from leap.types import BaseLeapModel


class PicturePuzzleDTO(BaseLeapModel):
    """Seeded picture puzzle loaded into the service cache."""

    id: str
    image_filename: str
    canonical_answer: str
    accepted_answers: List[str]


class PicturePuzzleAttemptDTO(BaseLeapModel):
    """One answer submission row for a picture session."""

    id: str
    game_session_id: str
    puzzle_id: str
    submitted_answer: Optional[str] = None
    correct: bool
    skipped: bool
    created_at: datetime


class PictureResultPuzzleDTO(BaseLeapModel):
    """Per-puzzle line item on the final result."""

    puzzle_id: str
    image_filename: str
    status: Literal["correct", "skipped", "not_reached"]
    score_earned: int


class PictureResultDTO(BaseLeapModel):
    """End-of-game summary for Picture Illustration."""

    score: int
    accuracy_score: int
    time_bonus: int
    time_remaining_seconds: int
    puzzles: List[PictureResultPuzzleDTO]


class PictureDisplayedPuzzleDTO(BaseLeapModel):
    """Puzzle shell returned to the client (no answers)."""

    id: str
    image_filename: str
    puzzles_answered: int
    puzzles_total: int


class PicturePlayPayload(BaseLeapModel):
    """Service output for POST /games/picture/play."""

    status: str
    game_session_id: Optional[str] = None
    puzzles_answered: Optional[int] = None
    puzzles_total: Optional[int] = None
    session_started_at: Optional[datetime] = None
    time_limit_ms: Optional[int] = None
    puzzle: Optional[PictureDisplayedPuzzleDTO] = None
    result: Optional[PictureResultDTO] = None


class PictureAnswerPayload(BaseLeapModel):
    """Service output for POST /games/picture/answer."""

    correct: bool
    score_earned: int
    current_score: int
    puzzles_solved: int
    puzzles_remaining: int
    next_puzzle: Optional[PictureDisplayedPuzzleDTO] = None
    result: Optional[PictureResultDTO] = None
