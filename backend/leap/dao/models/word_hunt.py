from datetime import datetime

from sqlalchemy import (
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


class WordHuntPuzzle(Base):
    __tablename__ = "word_hunt_puzzles"

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
    words: Mapped[list["WordHuntWord"]] = relationship(
        back_populates="puzzle",
        cascade="all, delete-orphan",
    )


class WordHuntWord(Base):
    __tablename__ = "word_hunt_words"
    __table_args__ = (UniqueConstraint("puzzle_id", "word", name="uq_word_hunt_words_puzzle_word"),)

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        server_default=text("gen_random_uuid()::text"),
    )
    puzzle_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("word_hunt_puzzles.id", ondelete="CASCADE"),
        nullable=False,
    )
    word: Mapped[str] = mapped_column(Text, nullable=False)
    clue: Mapped[str] = mapped_column(Text, nullable=False)
    start_row: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    start_col: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    end_row: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    end_col: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    puzzle: Mapped["WordHuntPuzzle"] = relationship(back_populates="words")


class WordHuntFind(Base):
    __tablename__ = "word_hunt_finds"
    __table_args__ = (
        UniqueConstraint("session_id", "word_id", name="uq_word_hunt_finds_session_word"),
        Index("ix_word_hunt_finds_session_id", "session_id"),
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
    word_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("word_hunt_words.id", ondelete="CASCADE"),
        nullable=False,
    )
    start_row: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    start_col: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    end_row: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    end_col: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    found_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
