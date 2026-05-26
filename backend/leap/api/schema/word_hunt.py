"""HTTP request/response shapes for Word Hunt."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class CoordinatesSchema(BaseModel):
    start_row: int
    start_col: int
    end_row: int
    end_col: int


class ClueSchema(BaseModel):
    word_id: str
    clue: str
    found: bool
    word: Optional[str] = None
    coordinates: Optional[CoordinatesSchema] = None


class PuzzleStateSchema(BaseModel):
    puzzle_id: str
    rows: int
    cols: int
    grid: List[List[str]]
    clues: List[ClueSchema]
    found_count: int
    total_words: int
    started_at: datetime


class FoundWordSchema(BaseModel):
    word_id: str
    word: str
    clue: str
    coordinates: CoordinatesSchema


class ResultSchema(BaseModel):
    score: int
    base_score: int
    time_bonus: int
    time_elapsed_ms: int
    found_count: int
    total_words: int
    found_words: List[FoundWordSchema]


class PlayResponse(BaseModel):
    session_status: str
    session_score: int
    puzzle: Optional[PuzzleStateSchema] = None
    result: Optional[ResultSchema] = None


class FindRequest(BaseModel):
    start_row: int = Field(ge=0)
    start_col: int = Field(ge=0)
    end_row: int = Field(ge=0)
    end_col: int = Field(ge=0)


class FindResponse(BaseModel):
    matched: bool
    word: Optional[FoundWordSchema] = None
    session_status: str
    session_score: int
    result: Optional[ResultSchema] = None


class SubmitResponse(BaseModel):
    result: ResultSchema
