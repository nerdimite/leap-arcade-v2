"""Internal DTOs for Four Pics, One Lie."""

from datetime import datetime
from typing import List, Optional

from leap.types import BaseLeapModel


class FourPicsQuestionDTO(BaseLeapModel):
    id: str
    image_paths: List[str]
    odd_one_out_index: int


class FourPicsQuestionAttemptDTO(BaseLeapModel):
    id: str
    session_id: str
    question_id: str
    status: str
    selected_index: Optional[int] = None
    score: Optional[int] = None
    time_bonus: Optional[int] = None
    time_ms: Optional[int] = None
    started_at: datetime
    completed_at: Optional[datetime] = None


class FourPicsQuestionStateDTO(BaseLeapModel):
    question_id: str
    question_number: int
    total_questions: int
    image_paths: List[str]
    status: str
    started_at: datetime


class FourPicsResultQuestionDTO(BaseLeapModel):
    question_id: str
    status: str
    score: int
    time_bonus: int


class FourPicsResultDTO(BaseLeapModel):
    score: int
    questions_correct: int
    questions_wrong: int
    questions_not_reached: int
    questions: List[FourPicsResultQuestionDTO]


class FourPicsPlayPayload(BaseLeapModel):
    session_status: str
    session_score: int
    question: Optional[FourPicsQuestionStateDTO] = None
    result: Optional[FourPicsResultDTO] = None


class FourPicsAnswerPayload(BaseLeapModel):
    correct: bool
    score: int
    time_bonus: int
    session_status: str
    session_score: int
    question: Optional[FourPicsQuestionStateDTO] = None
    result: Optional[FourPicsResultDTO] = None
