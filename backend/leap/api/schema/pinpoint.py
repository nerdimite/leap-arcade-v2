"""HTTP request/response shapes for Pinpoint."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class PuzzleStateSchema(BaseModel):
    puzzle_id: str
    puzzle_number: int
    total_puzzles: int
    clues_revealed: int
    clues: List[str]
    status: str
    score: Optional[int] = None
    time_bonus: Optional[int] = None
    started_at: datetime


class ResultPuzzleSchema(BaseModel):
    puzzle_id: str
    status: str
    clues_used: Optional[int] = None
    score: int
    time_bonus: int


class ResultSchema(BaseModel):
    score: int
    puzzles_solved: int
    puzzles_failed: int
    puzzles_not_reached: int
    puzzles: List[ResultPuzzleSchema]


class PlayResponse(BaseModel):
    session_status: str
    session_score: int
    puzzle: Optional[PuzzleStateSchema] = None
    result: Optional[ResultSchema] = None


class GuessRequest(BaseModel):
    puzzle_id: str = Field(min_length=1)
    guess: str = Field(min_length=1)


class GuessResponse(BaseModel):
    correct: bool
    puzzle: PuzzleStateSchema
    session_status: str
    session_score: int
    result: Optional[ResultSchema] = None


class AbandonResponse(BaseModel):
    result: ResultSchema
