"""HTTP request/response shapes for Rapid Fire Quiz."""

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class QuestionSchema(BaseModel):
    id: str
    question: str
    options: List[str]
    time_limit_ms: int


class ResultSchema(BaseModel):
    score: int
    correct_count: int
    wrong_count: int
    skipped_count: int
    time_taken_seconds: float


class PlayResponse(BaseModel):
    status: str
    game_session_id: Optional[str] = None
    questions_answered: Optional[int] = None
    questions_total: Optional[int] = None
    question: Optional[QuestionSchema] = None
    result: Optional[ResultSchema] = None


class AnswerRequest(BaseModel):
    question_id: str
    selected_option: Optional[int] = None
    time_ms: int = Field(ge=0)

    @field_validator("selected_option")
    @classmethod
    def validate_selected_option(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v not in (1, 2, 3, 4):
            raise ValueError("selected_option must be 1, 2, 3, or 4")
        return v


class AnswerResponse(BaseModel):
    correct: bool
    correct_option: int
    correct_answer_text: str
    current_score: int
    questions_answered: int
    questions_remaining: int
    next_question: Optional[QuestionSchema] = None
    result: Optional[ResultSchema] = None


class AbandonResponse(BaseModel):
    result: ResultSchema
