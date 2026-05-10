from sqlalchemy import CheckConstraint, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from leap.dao.models.base import Base


class WikiContent(Base):
    __tablename__ = "wiki_content"
    __table_args__ = (
        CheckConstraint("difficulty IN ('easy', 'medium', 'hard')", name="ck_wiki_content_difficulty"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, server_default=text("gen_random_uuid()::text"))
    start_page: Mapped[str] = mapped_column(String, nullable=False)
    target_page: Mapped[str] = mapped_column(String, nullable=False)
    difficulty: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'medium'"))
    optimal_steps: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
