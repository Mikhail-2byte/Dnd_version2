"""combat full mechanics: action economy, death saves, is_dead

Revision ID: a1b2c3d4e5f6
Revises: f1a2b3c4d5e6
Create Date: 2026-04-19

"""
from alembic import op
import sqlalchemy as sa

revision = 'a1b2c3d4e5f6'
down_revision = 'f1a2b3c4d5e6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('combat_participants', sa.Column('actions_used', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('combat_participants', sa.Column('bonus_actions_used', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('combat_participants', sa.Column('reaction_used', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('combat_participants', sa.Column('death_saves_success', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('combat_participants', sa.Column('death_saves_failure', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('combat_participants', sa.Column('is_dead', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('combat_participants', sa.Column('name', sa.String(255), nullable=True))


def downgrade() -> None:
    op.drop_column('combat_participants', 'name')
    op.drop_column('combat_participants', 'is_dead')
    op.drop_column('combat_participants', 'death_saves_failure')
    op.drop_column('combat_participants', 'death_saves_success')
    op.drop_column('combat_participants', 'reaction_used')
    op.drop_column('combat_participants', 'bonus_actions_used')
    op.drop_column('combat_participants', 'actions_used')
