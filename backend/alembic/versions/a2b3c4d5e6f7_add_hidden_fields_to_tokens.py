"""add hidden fields to tokens

Revision ID: a2b3c4d5e6f7
Revises: f2a3b4c5d6e7
Create Date: 2026-04-22

"""
from alembic import op
import sqlalchemy as sa

revision = 'a2b3c4d5e6f7'
down_revision = 'f2a3b4c5d6e7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('tokens', sa.Column('is_hidden', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('tokens', sa.Column('token_type', sa.String(20), nullable=False, server_default='npc'))
    op.add_column('tokens', sa.Column('token_metadata', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('tokens', 'token_metadata')
    op.drop_column('tokens', 'token_type')
    op.drop_column('tokens', 'is_hidden')
