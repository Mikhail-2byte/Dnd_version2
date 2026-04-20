"""add_items_and_currency

Revision ID: e1f2a3b4c5d6
Revises: d3e4f5a6b7c8
Branch labels: None
Depends on: None

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'e1f2a3b4c5d6'
down_revision = 'd3e4f5a6b7c8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('slug', sa.String(100), unique=True, nullable=False, index=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('name_en', sa.String(100), nullable=True),
        sa.Column('category', sa.String(50), nullable=True, index=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('weight', sa.Float(), nullable=True, server_default='0'),
        sa.Column('cost_gp', sa.Float(), nullable=True, server_default='0'),
    )

    op.add_column('characters', sa.Column('gold', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('characters', sa.Column('silver', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('characters', sa.Column('copper', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    op.drop_column('characters', 'copper')
    op.drop_column('characters', 'silver')
    op.drop_column('characters', 'gold')
    op.drop_table('items')
