"""wiki rounds and puzzle attempts

Revision ID: a1b2c3d4e5f6
Revises: f3a8b1c2d4e5
Create Date: 2026-05-17

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "f3a8b1c2d4e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "wiki_rounds",
        sa.Column("id", sa.String(), server_default=sa.text("gen_random_uuid()::text"), nullable=False),
        sa.Column("sequence_index", sa.Integer(), nullable=False),
        sa.Column("start_title", sa.String(), nullable=False),
        sa.Column("start_url", sa.String(), nullable=False),
        sa.Column("target_title", sa.String(), nullable=False),
        sa.Column("target_url", sa.String(), nullable=False),
        sa.Column("clue", sa.String(), nullable=False),
        sa.Column("optimal_click_count", sa.Integer(), nullable=False),
        sa.Column(
            "solution_path",
            postgresql.ARRAY(sa.String()),
            server_default=sa.text("'{}'::text[]"),
            nullable=False,
        ),
        sa.Column("time_limit_ms", sa.Integer(), server_default=sa.text("180000"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("sequence_index >= 1", name="ck_wiki_rounds_sequence_index_positive"),
        sa.CheckConstraint("optimal_click_count >= 1", name="ck_wiki_rounds_optimal_clicks"),
        sa.CheckConstraint("time_limit_ms > 0", name="ck_wiki_rounds_time_limit_positive"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sequence_index", name="uq_wiki_rounds_sequence_index"),
    )
    op.create_table(
        "wiki_puzzle_attempts",
        sa.Column("id", sa.String(), server_default=sa.text("gen_random_uuid()::text"), nullable=False),
        sa.Column("game_session_id", sa.String(), nullable=False),
        sa.Column("round_id", sa.String(), nullable=False),
        sa.Column("status", sa.String(), server_default=sa.text("'active'"), nullable=False),
        sa.Column("current_title", sa.String(), nullable=False),
        sa.Column(
            "click_path",
            postgresql.ARRAY(sa.String()),
            server_default=sa.text("'{}'::text[]"),
            nullable=False,
        ),
        sa.Column("steps_taken", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("time_ms", sa.Integer(), nullable=True),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('active', 'completed', 'timed_out')",
            name="ck_wiki_attempts_status",
        ),
        sa.CheckConstraint("steps_taken >= 0", name="ck_wiki_attempts_steps"),
        sa.CheckConstraint("score IS NULL OR score >= 0", name="ck_wiki_attempts_score"),
        sa.CheckConstraint("time_ms IS NULL OR time_ms >= 0", name="ck_wiki_attempts_time_ms"),
        sa.ForeignKeyConstraint(
            ["game_session_id"], ["game_sessions.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["round_id"], ["wiki_rounds.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "game_session_id",
            "round_id",
            name="uq_wiki_attempts_session_round",
        ),
    )


def downgrade() -> None:
    op.drop_table("wiki_puzzle_attempts")
    op.drop_table("wiki_rounds")
