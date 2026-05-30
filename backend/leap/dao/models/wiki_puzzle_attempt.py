from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from leap.dao.models.base import Base


class WikiPuzzleAttempt(Base):
    __tablename__ = "wiki_puzzle_attempts"
    __table_args__ = (
        UniqueConstraint("game_session_id", "round_id", name="uq_wiki_attempts_session_round"),
        CheckConstraint(
            "status IN ('active', 'completed', 'timed_out')",
            name="ck_wiki_attempts_status",
        ),
        CheckConstraint("steps_taken >= 0", name="ck_wiki_attempts_steps"),
        CheckConstraint("score IS NULL OR score >= 0", name="ck_wiki_attempts_score"),
        CheckConstraint("time_ms IS NULL OR time_ms >= 0", name="ck_wiki_attempts_time_ms"),
    )

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        server_default=text("gen_random_uuid()::text"),
    )
    game_session_id: Mapped[str] = mapped_column(
        String, ForeignKey("game_sessions.id", ondelete="CASCADE"), nullable=False
    )
    round_id: Mapped[str] = mapped_column(String, ForeignKey("wiki_rounds.id"), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'active'"))
    current_title: Mapped[str] = mapped_column(String, nullable=False)
    click_path: Mapped[list] = mapped_column(
        ARRAY(String), nullable=False, server_default=text("'{}'::text[]")
    )
    steps_taken: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
