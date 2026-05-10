from datetime import datetime

from sqlalchemy import DateTime, Integer, String, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from leap.dao.models.base import Base


class RapidFireQuestion(Base):
    __tablename__ = "rapid_fire_questions"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        server_default=text("gen_random_uuid()::text"),
    )
    question: Mapped[str] = mapped_column(String, nullable=False)
    options: Mapped[list] = mapped_column(ARRAY(String), nullable=False)
    correct_option_index: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[str | None] = mapped_column(String, nullable=True)
    time_limit_ms: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("15000"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
