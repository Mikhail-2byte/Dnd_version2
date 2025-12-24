"""add_characters

Revision ID: 8a9f72318502
Revises: e7dfa838beb2
Create Date: 2024-12-24 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8a9f72318502'
down_revision: Union[str, None] = 'e7dfa838beb2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create characters table
    op.create_table(
        'characters',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('race', sa.String(length=100), nullable=False),
        sa.Column('class', sa.String(length=100), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('strength', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('dexterity', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('constitution', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('intelligence', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('wisdom', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('charisma', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('character_history', sa.Text(), nullable=True),
        sa.Column('equipment_and_features', sa.Text(), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_characters_user_id'), 'characters', ['user_id'], unique=False)
    op.create_index(op.f('ix_characters_name'), 'characters', ['name'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_characters_name'), table_name='characters')
    op.drop_index(op.f('ix_characters_user_id'), table_name='characters')
    op.drop_table('characters')
