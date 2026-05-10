from sqlalchemy import Boolean, DateTime, String, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from leap.dao.models.base import Base


class Player(Base):
    __tablename__ = "players"

    id: Mapped[str] = mapped_column(String, primary_key=True)  # corp_id
    display_name: Mapped[str] = mapped_column(String, nullable=False)
    event_code_hash: Mapped[str] = mapped_column(String, nullable=False)  # hashed event code
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
