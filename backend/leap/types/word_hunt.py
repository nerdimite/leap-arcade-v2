"""Word Hunt game domain types."""

from datetime import datetime
from typing import List, Optional

from leap.types import BaseLeapModel


class WordHuntWordDTO(BaseLeapModel):
    id: str
    puzzle_id: str
    word: str
    clue: str
    start_row: int
    start_col: int
    end_row: int
    end_col: int


class WordHuntPuzzleDTO(BaseLeapModel):
    id: str
    rows: int
    cols: int
    grid: List[List[str]]
    words: List[WordHuntWordDTO]


class WordHuntFindDTO(BaseLeapModel):
    id: str
    session_id: str
    word_id: str
    start_row: int
    start_col: int
    end_row: int
    end_col: int
    found_at: datetime


class WordHuntCoordinatesDTO(BaseLeapModel):
    start_row: int
    start_col: int
    end_row: int
    end_col: int


class WordHuntClueDTO(BaseLeapModel):
    word_id: str
    clue: str
    found: bool
    word: Optional[str] = None
    coordinates: Optional[WordHuntCoordinatesDTO] = None


class WordHuntPuzzleStateDTO(BaseLeapModel):
    puzzle_id: str
    rows: int
    cols: int
    grid: List[List[str]]
    clues: List[WordHuntClueDTO]
    found_count: int
    total_words: int
    started_at: datetime


class WordHuntFoundWordDTO(BaseLeapModel):
    word_id: str
    word: str
    clue: str
    coordinates: WordHuntCoordinatesDTO


class WordHuntResultDTO(BaseLeapModel):
    score: int
    base_score: int
    time_bonus: int
    time_elapsed_ms: int
    found_count: int
    total_words: int
    found_words: List[WordHuntFoundWordDTO]


class WordHuntPlayPayload(BaseLeapModel):
    session_status: str
    session_score: int
    puzzle: Optional[WordHuntPuzzleStateDTO] = None
    result: Optional[WordHuntResultDTO] = None


class WordHuntFindPayload(BaseLeapModel):
    matched: bool
    word: Optional[WordHuntFoundWordDTO] = None
    session_status: str
    session_score: int
    result: Optional[WordHuntResultDTO] = None
