"""add_dice_roll_history

Revision ID: 3236ad368492
Revises: be71348dd92f
Create Date: 2025-12-26 00:07:40.602992

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '3236ad368492'
down_revision = 'be71348dd92f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create dice_roll_history table
    op.create_table(
        'dice_roll_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('game_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('count', sa.Integer(), nullable=False),
        sa.Column('faces', sa.Integer(), nullable=False),
        sa.Column('rolls', sa.JSON(), nullable=False),
        sa.Column('total', sa.Integer(), nullable=False),
        sa.Column('roll_type', sa.String(), nullable=True),
        sa.Column('modifier', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['game_id'], ['game_sessions.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dice_roll_history_game_id'), 'dice_roll_history', ['game_id'], unique=False)
    op.create_index(op.f('ix_dice_roll_history_user_id'), 'dice_roll_history', ['user_id'], unique=False)
    op.create_index(op.f('ix_dice_roll_history_created_at'), 'dice_roll_history', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_dice_roll_history_created_at'), table_name='dice_roll_history')
    op.drop_index(op.f('ix_dice_roll_history_user_id'), table_name='dice_roll_history')
    op.drop_index(op.f('ix_dice_roll_history_game_id'), table_name='dice_roll_history')
    op.drop_table('dice_roll_history')

