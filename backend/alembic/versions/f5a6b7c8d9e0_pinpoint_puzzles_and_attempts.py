"""pinpoint puzzles and attempts

Revision ID: f5a6b7c8d9e0
Revises: e4f5a6b7c8d9
Create Date: 2026-05-26

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "f5a6b7c8d9e0"
down_revision: Union[str, Sequence[str], None] = "e4f5a6b7c8d9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("ck_game_sessions_game_id", "game_sessions", type_="check")
    op.create_check_constraint(
        "ck_game_sessions_game_id",
        "game_sessions",
        "game_id IN ('wiki', 'picture', 'rapid_fire', 'four_pics', 'crossword', 'pinpoint')",
    )

    op.create_table(
        "pinpoint_puzzles",
        sa.Column("id", sa.String(), server_default=sa.text("gen_random_uuid()::text"), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column(
            "answer_aliases",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("clue1", sa.Text(), nullable=False),
        sa.Column("clue2", sa.Text(), nullable=False),
        sa.Column("clue3", sa.Text(), nullable=False),
        sa.Column("clue4", sa.Text(), nullable=False),
        sa.Column("clue5", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("answer", name="uq_pinpoint_puzzles_answer"),
    )
    op.create_table(
        "pinpoint_puzzle_attempts",
        sa.Column("id", sa.String(), server_default=sa.text("gen_random_uuid()::text"), nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("puzzle_id", sa.String(), nullable=False),
        sa.Column("clues_revealed", sa.SmallInteger(), nullable=False),
        sa.Column(
            "guesses",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("time_bonus", sa.Integer(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('active', 'solved', 'failed')",
            name="ck_pinpoint_puzzle_attempts_status",
        ),
        sa.CheckConstraint(
            "clues_revealed >= 1 AND clues_revealed <= 5",
            name="ck_pinpoint_puzzle_attempts_clues_revealed",
        ),
        sa.ForeignKeyConstraint(["puzzle_id"], ["pinpoint_puzzles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["session_id"], ["game_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_id", "puzzle_id", name="uq_pinpoint_puzzle_attempts_session_puzzle"),
    )
    op.create_index(
        "ix_pinpoint_puzzle_attempts_session_id",
        "pinpoint_puzzle_attempts",
        ["session_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_pinpoint_puzzle_attempts_session_id", table_name="pinpoint_puzzle_attempts")
    op.drop_table("pinpoint_puzzle_attempts")
    op.drop_table("pinpoint_puzzles")
    op.drop_constraint("ck_game_sessions_game_id", "game_sessions", type_="check")
    op.create_check_constraint(
        "ck_game_sessions_game_id",
        "game_sessions",
        "game_id IN ('wiki', 'picture', 'rapid_fire', 'four_pics', 'crossword')",
    )
