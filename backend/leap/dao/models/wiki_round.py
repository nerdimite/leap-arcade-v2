from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Integer, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from leap.dao.models.base import Base


class WikiRound(Base):
    __tablename__ = "wiki_rounds"
    __table_args__ = (
        UniqueConstraint("sequence_index", name="uq_wiki_rounds_sequence_index"),
        CheckConstraint("sequence_index >= 1", name="ck_wiki_rounds_sequence_index_positive"),
        CheckConstraint("optimal_click_count >= 1", name="ck_wiki_rounds_optimal_clicks"),
        CheckConstraint("time_limit_ms > 0", name="ck_wiki_rounds_time_limit_positive"),
    )

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        server_default=text("gen_random_uuid()::text"),
    )
    sequence_index: Mapped[int] = mapped_column(Integer, nullable=False)
    start_title: Mapped[str] = mapped_column(String, nullable=False)
    start_url: Mapped[str] = mapped_column(String, nullable=False)
    target_title: Mapped[str] = mapped_column(String, nullable=False)
    target_url: Mapped[str] = mapped_column(String, nullable=False)
    clue: Mapped[str] = mapped_column(String, nullable=False)
    optimal_click_count: Mapped[int] = mapped_column(Integer, nullable=False)
    solution_path: Mapped[list] = mapped_column(
        ARRAY(String), nullable=False, server_default=text("'{}'::text[]")
    )
    time_limit_ms: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("180000")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
