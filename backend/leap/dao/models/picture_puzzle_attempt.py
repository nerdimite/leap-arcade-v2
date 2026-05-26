from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from leap.dao.models.base import Base


class PicturePuzzleAttempt(Base):
    __tablename__ = "picture_puzzle_attempts"
    __table_args__ = (Index("ix_picture_puzzle_attempts_session_id", "session_id"),)

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        server_default=text("gen_random_uuid()::text"),
    )
    game_session_id: Mapped[str] = mapped_column(
        "session_id",
        String,
        ForeignKey("game_sessions.id"),
        nullable=False,
    )
    puzzle_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("picture_puzzles.id"),
        nullable=False,
    )
    submitted_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    skipped: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
