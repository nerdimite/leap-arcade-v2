from sqlalchemy import CheckConstraint, String, Text, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from leap.dao.models.base import Base


class RapidFireContent(Base):
    __tablename__ = "rapid_fire_content"
    __table_args__ = (
        CheckConstraint("question_type IN ('mcq', 'typed')", name="ck_rapid_fire_content_type"),
        CheckConstraint("difficulty IN ('easy', 'medium', 'hard')", name="ck_rapid_fire_content_difficulty"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, server_default=text("gen_random_uuid()::text"))
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String, nullable=False)  # 'mcq' or 'typed'
    options: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)  # MCQ options
    correct_answer: Mapped[str] = mapped_column(String, nullable=False)
    difficulty: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'medium'"))
