"""create crossword tables

Revision ID: 2961e788e9c3
Revises: a7b8c9d0e1f2
Create Date: 2026-05-30 09:57:25.417349

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2961e788e9c3'
down_revision: Union[str, Sequence[str], None] = 'a7b8c9d0e1f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Update game_sessions CHECK constraint to include 'crossword'
    op.drop_constraint("ck_game_sessions_game_id", "game_sessions", type_="check")
    op.create_check_constraint(
        "ck_game_sessions_game_id",
        "game_sessions",
        "game_id IN ('wiki', 'picture', 'rapid_fire', 'four_pics', 'word_hunt', 'pinpoint', 'crossword')",
    )

    op.create_table('crossword_puzzles',
    sa.Column('id', sa.String(), server_default=sa.text('gen_random_uuid()::text'), nullable=False),
    sa.Column('rows', sa.SmallInteger(), nullable=False),
    sa.Column('cols', sa.SmallInteger(), nullable=False),
    sa.Column('grid', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('crossword_entries',
    sa.Column('id', sa.String(), server_default=sa.text('gen_random_uuid()::text'), nullable=False),
    sa.Column('puzzle_id', sa.String(), nullable=False),
    sa.Column('number', sa.SmallInteger(), nullable=False),
    sa.Column('direction', sa.Text(), nullable=False),
    sa.Column('start_row', sa.SmallInteger(), nullable=False),
    sa.Column('start_col', sa.SmallInteger(), nullable=False),
    sa.Column('answer', sa.Text(), nullable=False),
    sa.Column('clue', sa.Text(), nullable=False),
    sa.CheckConstraint("direction IN ('across', 'down')", name='ck_crossword_entries_direction'),
    sa.ForeignKeyConstraint(['puzzle_id'], ['crossword_puzzles.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('puzzle_id', 'number', 'direction', name='uq_crossword_entries_puzzle_num_dir')
    )
    op.create_table('crossword_solves',
    sa.Column('id', sa.String(), server_default=sa.text('gen_random_uuid()::text'), nullable=False),
    sa.Column('session_id', sa.String(), nullable=False),
    sa.Column('entry_id', sa.String(), nullable=False),
    sa.Column('solved_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['entry_id'], ['crossword_entries.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['session_id'], ['game_sessions.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('session_id', 'entry_id', name='uq_crossword_solves_session_entry')
    )
    op.create_index('ix_crossword_solves_session_id', 'crossword_solves', ['session_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_crossword_solves_session_id', table_name='crossword_solves')
    op.drop_table('crossword_solves')
    op.drop_table('crossword_entries')
    op.drop_table('crossword_puzzles')

    # Revert CHECK constraint
    op.drop_constraint("ck_game_sessions_game_id", "game_sessions", type_="check")
    op.create_check_constraint(
        "ck_game_sessions_game_id",
        "game_sessions",
        "game_id IN ('wiki', 'picture', 'rapid_fire', 'four_pics', 'word_hunt', 'pinpoint')",
    )
