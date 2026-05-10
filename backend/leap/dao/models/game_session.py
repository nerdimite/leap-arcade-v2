from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from leap.dao.models.base import Base


class GameSession(Base):
    __tablename__ = "game_sessions"
    __table_args__ = (
        UniqueConstraint("player_id", "game_id", name="uq_game_sessions_player_game"),
        CheckConstraint(
            "status IN ('active', 'completed', 'abandoned')",
            name="ck_game_sessions_status",
        ),
        CheckConstraint(
            "game_id IN ('wiki', 'picture', 'rapid_fire', 'four_pics', 'crossword')",
            name="ck_game_sessions_game_id",
        ),
    )

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        server_default=text("gen_random_uuid()::text"),
    )
    player_id: Mapped[str] = mapped_column(String, ForeignKey("players.id"), nullable=False)
    game_id: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, server_default=text("'active'"), nullable=False)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    time_taken_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    session_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # game-specific runtime state
    started_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
