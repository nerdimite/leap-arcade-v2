"""HTTP request/response shapes for Four Pics, One Lie."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class QuestionStateSchema(BaseModel):
    question_id: str
    question_number: int
    total_questions: int
    image_paths: List[str]
    status: str
    started_at: datetime


class ResultQuestionSchema(BaseModel):
    question_id: str
    status: str
    score: int
    time_bonus: int


class ResultSchema(BaseModel):
    score: int
    questions_correct: int
    questions_wrong: int
    questions_not_reached: int
    questions: List[ResultQuestionSchema]


class PlayResponse(BaseModel):
    session_status: str
    session_score: int
    question: Optional[QuestionStateSchema] = None
    result: Optional[ResultSchema] = None


class AnswerRequest(BaseModel):
    question_id: str = Field(min_length=1)
    selected_index: int
    time_ms: int = Field(ge=0)

    @field_validator("selected_index")
    @classmethod
    def selected_index_in_range(cls, value: int) -> int:
        if value < 0 or value > 3:
            raise ValueError("selected_index must be between 0 and 3")
        return value


class AnswerResponse(BaseModel):
    correct: bool
    score: int
    time_bonus: int
    session_status: str
    session_score: int
    question: Optional[QuestionStateSchema] = None
    result: Optional[ResultSchema] = None


class AbandonResponse(BaseModel):
    result: ResultSchema
