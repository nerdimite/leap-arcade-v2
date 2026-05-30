"""Crossword API schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class CellCoordinateSchema(BaseModel):
    row: int
    col: int


class CellSkeletonSchema(BaseModel):
    row: int
    col: int
    number: Optional[int] = None
    letter: Optional[str] = None


class ClueSchema(BaseModel):
    entry_id: str
    number: int
    direction: str
    clue: str
    length: int
    start_row: int
    start_col: int
    solved: bool
    answer: Optional[str] = None
    cells: Optional[List[CellCoordinateSchema]] = None


class PuzzleStateSchema(BaseModel):
    puzzle_id: str
    rows: int
    cols: int
    cells: List[List[Optional[CellSkeletonSchema]]]
    clues: List[ClueSchema]
    solved_count: int
    total_entries: int
    started_at: datetime


class SolvedEntrySchema(BaseModel):
    entry_id: str
    number: int
    direction: str
    clue: str
    answer: str
    cells: List[CellCoordinateSchema]


class ResultSchema(BaseModel):
    score: int
    base_score: int
    time_bonus: int
    time_elapsed_ms: int
    solved_count: int
    total_entries: int
    solved_entries: List[SolvedEntrySchema]


class PlayResponse(BaseModel):
    session_status: str
    session_score: int
    puzzle: Optional[PuzzleStateSchema] = None
    result: Optional[ResultSchema] = None


class CheckRequest(BaseModel):
    entry_id: str
    letters: str = Field(min_length=0)


class CheckResponse(BaseModel):
    correct: bool
    entry: Optional[SolvedEntrySchema] = None
    session_status: str
    session_score: int
    result: Optional[ResultSchema] = None


class SubmitResponse(BaseModel):
    result: ResultSchema
