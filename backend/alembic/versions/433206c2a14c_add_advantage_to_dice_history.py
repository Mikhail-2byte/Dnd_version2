"""add_advantage_to_dice_history

Revision ID: 433206c2a14c
Revises: 3236ad368492
Create Date: 2025-12-26 00:43:18.760156

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '433206c2a14c'
down_revision = '3236ad368492'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Добавляем поля для advantage/disadvantage
    op.add_column('dice_roll_history', sa.Column('advantage_type', sa.String(), nullable=True))
    op.add_column('dice_roll_history', sa.Column('advantage_rolls', sa.JSON(), nullable=True))
    op.add_column('dice_roll_history', sa.Column('selected_roll', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('dice_roll_history', 'selected_roll')
    op.drop_column('dice_roll_history', 'advantage_rolls')
    op.drop_column('dice_roll_history', 'advantage_type')

