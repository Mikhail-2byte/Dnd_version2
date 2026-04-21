"""add monster slug and resistances to combat participants

Revision ID: f2a3b4c5d6e7
Revises: a1b2c3d4e5f6
Branch Labels: None
Depends On: None

"""
from alembic import op
import sqlalchemy as sa

revision = 'f2a3b4c5d6e7'
down_revision = ('a1b2c3d4e5f6', 'e1f2a3b4c5d6')
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('combat_participants', sa.Column('monster_slug', sa.String(255), nullable=True))
    op.add_column('combat_participants', sa.Column('damage_resistances', sa.JSON(), nullable=True))
    op.add_column('combat_participants', sa.Column('damage_immunities', sa.JSON(), nullable=True))
    op.add_column('combat_participants', sa.Column('damage_vulnerabilities', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('combat_participants', 'damage_vulnerabilities')
    op.drop_column('combat_participants', 'damage_immunities')
    op.drop_column('combat_participants', 'damage_resistances')
    op.drop_column('combat_participants', 'monster_slug')
