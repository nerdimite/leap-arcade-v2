from sqlalchemy import CheckConstraint, String, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from leap.dao.models.base import Base


class CrosswordContent(Base):
    __tablename__ = "crossword_content"
    __table_args__ = (
        CheckConstraint("difficulty IN ('easy', 'medium', 'hard')", name="ck_crossword_content_difficulty"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, server_default=text("gen_random_uuid()::text"))
    grid: Mapped[dict] = mapped_column(JSONB, nullable=False)  # 2D array of cells
    clues_across: Mapped[dict] = mapped_column(JSONB, nullable=False)  # {"1": "clue text", ...}
    clues_down: Mapped[dict] = mapped_column(JSONB, nullable=False)
    difficulty: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'medium'"))
    title: Mapped[str | None] = mapped_column(String, nullable=True)
