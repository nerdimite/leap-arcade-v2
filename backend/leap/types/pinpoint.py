"""Pinpoint game domain types."""

from datetime import datetime
from typing import List, Literal, Optional

from leap.types import BaseLeapModel


class PinpointPuzzleDTO(BaseLeapModel):
    """Seeded pinpoint puzzle loaded into the service cache."""

    id: str
    answer: str
    answer_aliases: List[str]
    clue1: str
    clue2: str
    clue3: str
    clue4: str
    clue5: str


class PinpointPuzzleAttemptDTO(BaseLeapModel):
    """One puzzle attempt row for a Pinpoint session."""

    id: str
    game_session_id: str
    puzzle_id: str
    clues_revealed: int
    guesses: List[str]
    status: Literal["active", "solved", "failed"]
    score: Optional[int] = None
    time_bonus: Optional[int] = None
    started_at: datetime
    completed_at: Optional[datetime] = None


class PinpointPuzzleStateDTO(BaseLeapModel):
    """Puzzle shell returned to the client (no answers)."""

    puzzle_id: str
    puzzle_number: int
    total_puzzles: int
    clues_revealed: int
    clues: List[str]
    status: Literal["active", "solved", "failed"]
    score: Optional[int] = None
    time_bonus: Optional[int] = None
    started_at: datetime


class PinpointResultPuzzleDTO(BaseLeapModel):
    """Per-puzzle line item on the final result."""

    puzzle_id: str
    status: Literal["solved", "failed", "not_reached"]
    clues_used: Optional[int] = None
    score: int
    time_bonus: int


class PinpointResultDTO(BaseLeapModel):
    """End-of-game summary for Pinpoint."""

    score: int
    puzzles_solved: int
    puzzles_failed: int
    puzzles_not_reached: int
    puzzles: List[PinpointResultPuzzleDTO]


class PinpointPlayPayload(BaseLeapModel):
    """Service output for POST /games/pinpoint/play."""

    session_status: str
    session_score: int
    puzzle: Optional[PinpointPuzzleStateDTO] = None
    result: Optional[PinpointResultDTO] = None


class PinpointGuessPayload(BaseLeapModel):
    """Service output for POST /games/pinpoint/guess."""

    correct: bool
    puzzle: PinpointPuzzleStateDTO
    session_status: str
    session_score: int
    result: Optional[PinpointResultDTO] = None
