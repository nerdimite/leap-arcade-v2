"""Rapid Fire game domain types."""

from datetime import datetime
from typing import List, Optional

from leap.types import BaseLeapModel


class RapidFireQuestionDTO(BaseLeapModel):
    """A single rapid fire question as returned by RapidFireQuestionDAO."""

    id: str
    question: str
    options: List[str]
    correct_option_index: int
    category: Optional[str] = None
    time_limit_ms: int = 15000


class RapidFireAnswerDTO(BaseLeapModel):
    """A recorded answer as returned by RapidFireAnswerDAO."""

    id: str
    game_session_id: str
    question_id: str
    correct: bool
    skipped: bool
    time_ms: int
    answered_at: datetime


class RapidFireResultDTO(BaseLeapModel):
    """Final result summary emitted when a rapid fire session ends."""

    total_questions: int
    correct: int
    skipped: int
    score: int
    time_taken_ms: int
