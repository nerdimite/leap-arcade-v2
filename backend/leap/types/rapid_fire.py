"""Rapid Fire game domain types."""

from datetime import datetime
from typing import List, Optional

from leap.types import BaseLeapModel


class RapidFireQuestionDTO(BaseLeapModel):
    """Cached rapid fire question (includes server-only correct index)."""

    id: str
    question: str
    options: List[str]
    correct_option_index: int
    category: Optional[str] = None
    time_limit_ms: int = 15000


class RapidFireAnswerDTO(BaseLeapModel):
    """A recorded answer row as returned by RapidFireAnswerDAO."""

    id: str
    game_session_id: str
    question_id: str
    correct: bool
    skipped: bool
    selected_option: Optional[int] = None
    time_ms: int
    answered_at: datetime


class RapidFireResultDTO(BaseLeapModel):
    """Result summary when a rapid fire session ends or is summarized."""

    score: int
    correct_count: int
    wrong_count: int
    skipped_count: int
    time_taken_seconds: float


class RapidFirePlayPayload(BaseLeapModel):
    """Service output for POST /play (maps to API PlayResponse)."""

    status: str
    game_session_id: Optional[str] = None
    questions_answered: Optional[int] = None
    questions_total: Optional[int] = None
    question: Optional[RapidFireQuestionDTO] = None
    result: Optional[RapidFireResultDTO] = None


class RapidFireAnswerPayload(BaseLeapModel):
    """Service output for POST /answer (maps to API AnswerResponse)."""

    correct: bool
    correct_option: int
    correct_answer_text: str
    current_score: int
    questions_answered: int
    questions_remaining: int
    next_question: Optional[RapidFireQuestionDTO] = None
    result: Optional[RapidFireResultDTO] = None
