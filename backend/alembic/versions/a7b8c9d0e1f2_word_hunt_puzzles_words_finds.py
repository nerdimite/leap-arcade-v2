"""word hunt puzzles, words, finds

Revision ID: a7b8c9d0e1f2
Revises: f5a6b7c8d9e0
Create Date: 2026-05-26

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "a7b8c9d0e1f2"
down_revision: Union[str, Sequence[str], None] = "f5a6b7c8d9e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("ck_game_sessions_game_id", "game_sessions", type_="check")
    op.create_check_constraint(
        "ck_game_sessions_game_id",
        "game_sessions",
        "game_id IN ('wiki', 'picture', 'rapid_fire', 'four_pics', 'word_hunt', 'pinpoint')",
    )

    op.create_table(
        "word_hunt_puzzles",
        sa.Column("id", sa.String(), server_default=sa.text("gen_random_uuid()::text"), nullable=False),
        sa.Column("rows", sa.SmallInteger(), nullable=False),
        sa.Column("cols", sa.SmallInteger(), nullable=False),
        sa.Column("grid", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "word_hunt_words",
        sa.Column("id", sa.String(), server_default=sa.text("gen_random_uuid()::text"), nullable=False),
        sa.Column("puzzle_id", sa.String(), nullable=False),
        sa.Column("word", sa.Text(), nullable=False),
        sa.Column("clue", sa.Text(), nullable=False),
        sa.Column("start_row", sa.SmallInteger(), nullable=False),
        sa.Column("start_col", sa.SmallInteger(), nullable=False),
        sa.Column("end_row", sa.SmallInteger(), nullable=False),
        sa.Column("end_col", sa.SmallInteger(), nullable=False),
        sa.ForeignKeyConstraint(["puzzle_id"], ["word_hunt_puzzles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("puzzle_id", "word", name="uq_word_hunt_words_puzzle_word"),
    )
    op.create_table(
        "word_hunt_finds",
        sa.Column("id", sa.String(), server_default=sa.text("gen_random_uuid()::text"), nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("word_id", sa.String(), nullable=False),
        sa.Column("start_row", sa.SmallInteger(), nullable=False),
        sa.Column("start_col", sa.SmallInteger(), nullable=False),
        sa.Column("end_row", sa.SmallInteger(), nullable=False),
        sa.Column("end_col", sa.SmallInteger(), nullable=False),
        sa.Column("found_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["game_sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["word_id"], ["word_hunt_words.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_id", "word_id", name="uq_word_hunt_finds_session_word"),
    )
    op.create_index("ix_word_hunt_finds_session_id", "word_hunt_finds", ["session_id"])


def downgrade() -> None:
    op.drop_index("ix_word_hunt_finds_session_id", table_name="word_hunt_finds")
    op.drop_table("word_hunt_finds")
    op.drop_table("word_hunt_words")
    op.drop_table("word_hunt_puzzles")

    op.drop_constraint("ck_game_sessions_game_id", "game_sessions", type_="check")
    op.create_check_constraint(
        "ck_game_sessions_game_id",
        "game_sessions",
        "game_id IN ('wiki', 'picture', 'rapid_fire', 'four_pics', 'crossword', 'pinpoint')",
    )
