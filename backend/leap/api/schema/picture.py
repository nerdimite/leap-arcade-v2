"""HTTP request/response shapes for Picture Illustration."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class PuzzleSchema(BaseModel):
    id: str
    image_filename: str
    puzzles_answered: int
    puzzles_total: int


class ResultPuzzleSchema(BaseModel):
    puzzle_id: str
    image_filename: str
    status: str
    score_earned: int


class ResultSchema(BaseModel):
    score: int
    accuracy_score: int
    time_bonus: int
    time_remaining_seconds: int
    puzzles: List[ResultPuzzleSchema]


class PlayResponse(BaseModel):
    status: str
    game_session_id: Optional[str] = None
    puzzles_answered: Optional[int] = None
    puzzles_total: Optional[int] = None
    session_started_at: Optional[datetime] = None
    time_limit_ms: Optional[int] = None
    puzzle: Optional[PuzzleSchema] = None
    result: Optional[ResultSchema] = None


class AnswerRequest(BaseModel):
    puzzle_id: str = Field(min_length=1)
    submitted_answer: Optional[str] = None


class AnswerResponse(BaseModel):
    correct: bool
    score_earned: int
    current_score: int
    puzzles_solved: int
    puzzles_remaining: int
    next_puzzle: Optional[PuzzleSchema] = None
    result: Optional[ResultSchema] = None


class AbandonResponse(BaseModel):
    result: ResultSchema
