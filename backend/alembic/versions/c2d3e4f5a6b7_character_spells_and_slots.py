"""character spells and spell slot trackers

Revision ID: c2d3e4f5a6b7
Revises: b1c2d3e4f5a6
Create Date: 2026-04-19 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'c2d3e4f5a6b7'
down_revision = 'b1c2d3e4f5a6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'character_spells',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('character_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('spell_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('is_prepared', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_ritual', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('learned_at_level', sa.Integer(), nullable=True, server_default='1'),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['spell_id'], ['spells.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_character_spells_character_id', 'character_spells', ['character_id'])

    op.create_table(
        'spell_slot_trackers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('character_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('spell_level', sa.Integer(), nullable=False),
        sa.Column('max_slots', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('used_slots', sa.Integer(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_spell_slot_trackers_character_id', 'spell_slot_trackers', ['character_id'])


def downgrade() -> None:
    op.drop_index('ix_spell_slot_trackers_character_id', table_name='spell_slot_trackers')
    op.drop_table('spell_slot_trackers')
    op.drop_index('ix_character_spells_character_id', table_name='character_spells')
    op.drop_table('character_spells')
