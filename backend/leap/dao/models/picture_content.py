from sqlalchemy import CheckConstraint, String, Text, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from leap.dao.models.base import Base


class PictureContent(Base):
    __tablename__ = "picture_content"
    __table_args__ = (
        CheckConstraint("difficulty IN ('easy', 'medium', 'hard')", name="ck_picture_content_difficulty"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, server_default=text("gen_random_uuid()::text"))
    image_refs: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)  # static asset filenames
    answer: Mapped[str] = mapped_column(String, nullable=False)
    hint: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'medium'"))
