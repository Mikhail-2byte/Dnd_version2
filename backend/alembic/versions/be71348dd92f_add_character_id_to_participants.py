"""add_character_id_to_participants

Revision ID: be71348dd92f
Revises: 70ec5d28f7a8
Create Date: 2025-12-25 22:43:58.376988

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'be71348dd92f'
down_revision = '70ec5d28f7a8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('game_participants', sa.Column('character_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        'fk_game_participants_character_id',
        'game_participants',
        'characters',
        ['character_id'],
        ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    op.drop_constraint('fk_game_participants_character_id', 'game_participants', type_='foreignkey')
    op.drop_column('game_participants', 'character_id')

