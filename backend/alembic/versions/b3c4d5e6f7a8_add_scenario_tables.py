"""add scenario tables

Revision ID: b3c4d5e6f7a8
Revises: a2b3c4d5e6f7
Create Date: 2026-04-22

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'b3c4d5e6f7a8'
down_revision = 'a2b3c4d5e6f7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'scenarios',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('story', sa.Text(), nullable=True),
        sa.Column('map_url', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_scenarios_owner_id', 'scenarios', ['owner_id'])

    op.create_table(
        'scenario_npcs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('scenario_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('x', sa.Float(), nullable=False),
        sa.Column('y', sa.Float(), nullable=False),
        sa.Column('image_url', sa.String(500), nullable=True),
        sa.Column('is_hidden', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('monster_slug', sa.String(200), nullable=True),
        sa.Column('loot', sa.JSON(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['scenario_id'], ['scenarios.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_scenario_npcs_scenario_id', 'scenario_npcs', ['scenario_id'])

    op.create_table(
        'scenario_hidden_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('scenario_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('x', sa.Float(), nullable=False),
        sa.Column('y', sa.Float(), nullable=False),
        sa.Column('image_url', sa.String(500), nullable=True),
        sa.Column('item_type', sa.String(20), nullable=False),
        sa.Column('item_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['scenario_id'], ['scenarios.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_scenario_hidden_items_scenario_id', 'scenario_hidden_items', ['scenario_id'])


def downgrade() -> None:
    op.drop_index('ix_scenario_hidden_items_scenario_id', table_name='scenario_hidden_items')
    op.drop_table('scenario_hidden_items')
    op.drop_index('ix_scenario_npcs_scenario_id', table_name='scenario_npcs')
    op.drop_table('scenario_npcs')
    op.drop_index('ix_scenarios_owner_id', table_name='scenarios')
    op.drop_table('scenarios')
