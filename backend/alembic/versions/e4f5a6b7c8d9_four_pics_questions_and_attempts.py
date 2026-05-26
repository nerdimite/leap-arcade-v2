"""four pics questions and attempts

Revision ID: e4f5a6b7c8d9
Revises: d0e1f2a3b4c5
Create Date: 2026-05-26

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "e4f5a6b7c8d9"
down_revision: Union[str, Sequence[str], None] = "d0e1f2a3b4c5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "four_pics_questions",
        sa.Column("id", sa.String(), server_default=sa.text("gen_random_uuid()::text"), nullable=False),
        sa.Column("image_paths", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("odd_one_out_index", sa.SmallInteger(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "odd_one_out_index >= 0 AND odd_one_out_index <= 3",
            name="ck_four_pics_questions_odd_one_out_index",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "four_pics_question_attempts",
        sa.Column("id", sa.String(), server_default=sa.text("gen_random_uuid()::text"), nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("question_id", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("selected_index", sa.SmallInteger(), nullable=True),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("time_bonus", sa.Integer(), nullable=True),
        sa.Column("time_ms", sa.Integer(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('active', 'correct', 'wrong')",
            name="ck_fpqa_status",
        ),
        sa.CheckConstraint(
            "(selected_index IS NULL) OR (selected_index >= 0 AND selected_index <= 3)",
            name="ck_fpqa_selected_index",
        ),
        sa.ForeignKeyConstraint(["question_id"], ["four_pics_questions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["session_id"], ["game_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_id", "question_id", name="uq_fpqa_session_question"),
    )
    op.create_index(
        "ix_four_pics_question_attempts_session_id",
        "four_pics_question_attempts",
        ["session_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_four_pics_question_attempts_session_id", table_name="four_pics_question_attempts")
    op.drop_table("four_pics_question_attempts")
    op.drop_table("four_pics_questions")
