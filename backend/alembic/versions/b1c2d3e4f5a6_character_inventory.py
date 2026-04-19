"""character inventory table

Revision ID: b1c2d3e4f5a6
Revises: a1b2c3d4e5f6
Create Date: 2026-04-19 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'b1c2d3e4f5a6'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'character_inventory',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('character_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('item_type', sa.String(20), nullable=False),
        sa.Column('item_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_equipped', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('slot', sa.String(30), nullable=True),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("item_type IN ('weapon', 'armor', 'item')", name='ck_inventory_item_type'),
    )
    op.create_index('ix_character_inventory_character_id', 'character_inventory', ['character_id'])


def downgrade() -> None:
    op.drop_index('ix_character_inventory_character_id', table_name='character_inventory')
    op.drop_table('character_inventory')
