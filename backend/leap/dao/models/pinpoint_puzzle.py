from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from leap.dao.models.base import Base


class PinpointPuzzle(Base):
    __tablename__ = "pinpoint_puzzles"
    __table_args__ = (UniqueConstraint("answer", name="uq_pinpoint_puzzles_answer"),)

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        server_default=text("gen_random_uuid()::text"),
    )
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    answer_aliases: Mapped[list] = mapped_column(JSONB, nullable=False)
    clue1: Mapped[str] = mapped_column(Text, nullable=False)
    clue2: Mapped[str] = mapped_column(Text, nullable=False)
    clue3: Mapped[str] = mapped_column(Text, nullable=False)
    clue4: Mapped[str] = mapped_column(Text, nullable=False)
    clue5: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class PinpointPuzzleAttempt(Base):
    __tablename__ = "pinpoint_puzzle_attempts"
    __table_args__ = (
        UniqueConstraint(
            "session_id", "puzzle_id", name="uq_pinpoint_puzzle_attempts_session_puzzle"
        ),
        CheckConstraint(
            "status IN ('active', 'solved', 'failed')",
            name="ck_pinpoint_puzzle_attempts_status",
        ),
        CheckConstraint(
            "clues_revealed >= 1 AND clues_revealed <= 5",
            name="ck_pinpoint_puzzle_attempts_clues_revealed",
        ),
        Index("ix_pinpoint_puzzle_attempts_session_id", "session_id"),
    )

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        server_default=text("gen_random_uuid()::text"),
    )
    game_session_id: Mapped[str] = mapped_column(
        "session_id",
        String,
        ForeignKey("game_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    puzzle_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("pinpoint_puzzles.id", ondelete="CASCADE"),
        nullable=False,
    )
    clues_revealed: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    guesses: Mapped[list] = mapped_column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    status: Mapped[str] = mapped_column(String, nullable=False)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    time_bonus: Mapped[int | None] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
