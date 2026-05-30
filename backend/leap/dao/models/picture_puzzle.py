from datetime import datetime

from sqlalchemy import DateTime, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from leap.dao.models.base import Base


class PicturePuzzle(Base):
    __tablename__ = "picture_puzzles"
    __table_args__ = (UniqueConstraint("image_filename", name="uq_picture_puzzles_image_filename"),)

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        server_default=text("gen_random_uuid()::text"),
    )
    image_filename: Mapped[str] = mapped_column(String, nullable=False)
    canonical_answer: Mapped[str] = mapped_column(String, nullable=False)
    accepted_answers: Mapped[list] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
