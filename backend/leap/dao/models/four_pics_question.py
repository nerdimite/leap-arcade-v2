"""ORM model for Four Pics seed questions."""

from sqlalchemy import CheckConstraint, Column, DateTime, SmallInteger, String, text
from sqlalchemy.dialects.postgresql import JSONB

from leap.dao.models.base import Base


class FourPicsQuestion(Base):
    """One Four Pics question — four image paths and the server-only odd-one-out index."""

    __tablename__ = "four_pics_questions"
    __table_args__ = (
        CheckConstraint(
            "odd_one_out_index >= 0 AND odd_one_out_index <= 3",
            name="ck_four_pics_questions_odd_one_out_index",
        ),
    )

    id = Column(String, primary_key=True, server_default=text("gen_random_uuid()::text"))
    image_paths = Column(JSONB, nullable=False)
    odd_one_out_index = Column(SmallInteger, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
