from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from leap.dao.models.base import Base


class Player(Base):
    __tablename__ = "players"

    id: Mapped[str] = mapped_column(String, primary_key=True)  # normalised corp_id (lowercase)
    display_name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
