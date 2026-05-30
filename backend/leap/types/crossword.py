"""Crossword game domain types."""

from datetime import datetime
from typing import List, Optional, Dict

from leap.types import BaseLeapModel


class CrosswordEntryDTO(BaseLeapModel):
    id: str
    puzzle_id: str
    number: int
    direction: str
    start_row: int
    start_col: int
    answer: str
    clue: str


class CrosswordPuzzleDTO(BaseLeapModel):
    id: str
    rows: int
    cols: int
    grid: List[List[Optional[str]]]
    entries: List[CrosswordEntryDTO]


class CrosswordSolveDTO(BaseLeapModel):
    id: str
    session_id: str
    entry_id: str
    solved_at: datetime


class CellSkeleton(BaseLeapModel):
    row: int
    col: int
    number: Optional[int] = None
    letter: Optional[str] = None


class ClueSkeleton(BaseLeapModel):
    entry_id: str
    number: int
    direction: str
    clue: str
    length: int
    start_row: int
    start_col: int
    solved: bool
    answer: Optional[str] = None
    cells: Optional[List[Dict[str, int]]] = None


class CrosswordPuzzleStateDTO(BaseLeapModel):
    puzzle_id: str
    rows: int
    cols: int
    cells: List[List[Optional[CellSkeleton]]]
    clues: List[ClueSkeleton]
    solved_count: int
    total_entries: int
    started_at: datetime


class CrosswordSolvedEntryDTO(BaseLeapModel):
    entry_id: str
    number: int
    direction: str
    clue: str
    answer: str
    cells: List[Dict[str, int]]


class CrosswordResultDTO(BaseLeapModel):
    score: int
    base_score: int
    time_bonus: int
    time_elapsed_ms: int
    solved_count: int
    total_entries: int
    solved_entries: List[CrosswordSolvedEntryDTO]


class CrosswordPlayPayload(BaseLeapModel):
    session_status: str
    session_score: int
    puzzle: Optional[CrosswordPuzzleStateDTO] = None
    result: Optional[CrosswordResultDTO] = None


class CrosswordCheckPayload(BaseLeapModel):
    correct: bool
    entry: Optional[CrosswordSolvedEntryDTO] = None
    session_status: str
    session_score: int
    result: Optional[CrosswordResultDTO] = None


class CrosswordCheckInput(BaseLeapModel):
    entry_id: str
    letters: str
