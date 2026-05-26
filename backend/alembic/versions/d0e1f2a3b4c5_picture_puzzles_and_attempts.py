"""picture puzzles and attempts

Revision ID: d0e1f2a3b4c5
Revises: a1b2c3d4e5f6
Create Date: 2026-05-17

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "d0e1f2a3b4c5"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "picture_puzzles",
        sa.Column("id", sa.String(), server_default=sa.text("gen_random_uuid()::text"), nullable=False),
        sa.Column("image_filename", sa.String(), nullable=False),
        sa.Column("canonical_answer", sa.String(), nullable=False),
        sa.Column(
            "accepted_answers",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("image_filename", name="uq_picture_puzzles_image_filename"),
    )
    op.create_table(
        "picture_puzzle_attempts",
        sa.Column("id", sa.String(), server_default=sa.text("gen_random_uuid()::text"), nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("puzzle_id", sa.String(), nullable=False),
        sa.Column("submitted_answer", sa.Text(), nullable=True),
        sa.Column("correct", sa.Boolean(), nullable=False),
        sa.Column("skipped", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["session_id"], ["game_sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["puzzle_id"], ["picture_puzzles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_picture_puzzle_attempts_session_id",
        "picture_puzzle_attempts",
        ["session_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_picture_puzzle_attempts_session_id", table_name="picture_puzzle_attempts")
    op.drop_table("picture_puzzle_attempts")
    op.drop_table("picture_puzzles")
