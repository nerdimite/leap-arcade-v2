from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from leap.dao.models.base import Base


class CrosswordPuzzle(Base):
    __tablename__ = "crossword_puzzles"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        server_default=text("gen_random_uuid()::text"),
    )
    rows: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    cols: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    grid: Mapped[list] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    entries: Mapped[list["CrosswordEntry"]] = relationship(
        back_populates="puzzle",
        cascade="all, delete-orphan",
    )


class CrosswordEntry(Base):
    __tablename__ = "crossword_entries"
    __table_args__ = (
        UniqueConstraint("puzzle_id", "number", "direction", name="uq_crossword_entries_puzzle_num_dir"),
        CheckConstraint(
            "direction IN ('across', 'down')",
            name="ck_crossword_entries_direction",
        ),
    )

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        server_default=text("gen_random_uuid()::text"),
    )
    puzzle_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("crossword_puzzles.id", ondelete="CASCADE"),
        nullable=False,
    )
    number: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    direction: Mapped[str] = mapped_column(Text, nullable=False)
    start_row: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    start_col: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    clue: Mapped[str] = mapped_column(Text, nullable=False)

    puzzle: Mapped["CrosswordPuzzle"] = relationship(back_populates="entries")


class CrosswordSolve(Base):
    __tablename__ = "crossword_solves"
    __table_args__ = (
        UniqueConstraint("session_id", "entry_id", name="uq_crossword_solves_session_entry"),
        Index("ix_crossword_solves_session_id", "session_id"),
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
    entry_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("crossword_entries.id", ondelete="CASCADE"),
        nullable=False,
    )
    solved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
