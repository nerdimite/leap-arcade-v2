from sqlalchemy import CheckConstraint, Integer, String, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from leap.dao.models.base import Base


class FourPicsContent(Base):
    __tablename__ = "four_pics_content"
    __table_args__ = (
        CheckConstraint("difficulty IN ('easy', 'medium', 'hard')", name="ck_four_pics_content_difficulty"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, server_default=text("gen_random_uuid()::text"))
    image_refs: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)  # exactly 4 filenames
    category: Mapped[str] = mapped_column(String, nullable=False)  # e.g. "Types of pasta"
    outlier_index: Mapped[int] = mapped_column(Integer, nullable=False)  # 0-3, which image is the odd one out
    difficulty: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'medium'"))
