"""add rapid_fire_answers selected_option and unique constraint

Revision ID: f3a8b1c2d4e5
Revises: e21296ea2b2c
Create Date: 2026-05-13

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f3a8b1c2d4e5"
down_revision: Union[str, Sequence[str], None] = "e21296ea2b2c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "rapid_fire_answers",
        sa.Column("selected_option", sa.Integer(), nullable=True),
    )
    op.create_unique_constraint(
        "uq_rfa_session_question",
        "rapid_fire_answers",
        ["game_session_id", "question_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_rfa_session_question", "rapid_fire_answers", type_="unique")
    op.drop_column("rapid_fire_answers", "selected_option")
