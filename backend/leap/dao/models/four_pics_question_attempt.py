"""ORM model for Four Pics per-question attempts within a game session."""

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import relationship

from leap.dao.models.base import Base


class FourPicsQuestionAttempt(Base):
    """Tracks one question served in a Four Pics session — active until answered."""

    __tablename__ = "four_pics_question_attempts"
    __table_args__ = (
        UniqueConstraint("session_id", "question_id", name="uq_fpqa_session_question"),
        CheckConstraint(
            "status IN ('active', 'correct', 'wrong')",
            name="ck_fpqa_status",
        ),
        CheckConstraint(
            "(selected_index IS NULL) OR (selected_index >= 0 AND selected_index <= 3)",
            name="ck_fpqa_selected_index",
        ),
    )

    id = Column(String, primary_key=True, server_default=text("gen_random_uuid()::text"))
    session_id = Column(String, ForeignKey("game_sessions.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(
        String, ForeignKey("four_pics_questions.id", ondelete="CASCADE"), nullable=False
    )
    status = Column(String, nullable=False)
    selected_index = Column(SmallInteger, nullable=True)
    score = Column(Integer, nullable=True)
    time_bonus = Column(Integer, nullable=True)
    time_ms = Column(Integer, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    game_session = relationship("GameSession", backref="four_pics_attempts")
    question = relationship("FourPicsQuestion", backref="attempts")
