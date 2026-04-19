"""add_ready_status_to_participants

Revision ID: 70ec5d28f7a8
Revises: 575c28180b41
Create Date: 2025-12-25 22:04:20.963330

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '70ec5d28f7a8'
down_revision = '575c28180b41'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('game_participants', sa.Column('is_ready', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    op.drop_column('game_participants', 'is_ready')

