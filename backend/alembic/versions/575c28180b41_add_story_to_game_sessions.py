"""add_story_to_game_sessions

Revision ID: 575c28180b41
Revises: 8a9f72318502
Create Date: 2025-12-24 22:05:45.358404

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '575c28180b41'
down_revision = '8a9f72318502'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('game_sessions', sa.Column('story', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('game_sessions', 'story')

