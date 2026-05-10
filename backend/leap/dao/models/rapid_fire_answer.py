from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from leap.dao.models.base import Base


class RapidFireAnswer(Base):
    __tablename__ = "rapid_fire_answers"
    __table_args__ = (
        Index("ix_rapid_fire_answers_game_session_id", "game_session_id"),
    )

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        server_default=text("gen_random_uuid()::text"),
    )
    game_session_id: Mapped[str] = mapped_column(
        String, ForeignKey("game_sessions.id"), nullable=False
    )
    question_id: Mapped[str] = mapped_column(
        String, ForeignKey("rapid_fire_questions.id"), nullable=False
    )
    correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    skipped: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    answered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
