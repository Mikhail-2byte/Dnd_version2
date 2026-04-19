"""update_characters_game_data_fields

Revision ID: d2e3f4a5b6c7
Revises: c1a2b3d4e5f6
Create Date: 2026-04-19 12:01:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'd2e3f4a5b6c7'
down_revision = 'c1a2b3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('characters', sa.Column('race_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('characters', sa.Column('background_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('characters', sa.Column('skill_proficiencies', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('characters', sa.Column('saving_throw_proficiencies', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('characters', sa.Column('experience_points', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('characters', sa.Column('max_hp', sa.Integer(), nullable=True))

    op.create_foreign_key(
        'fk_characters_race_id', 'characters', 'races', ['race_id'], ['id'], ondelete='SET NULL'
    )
    op.create_foreign_key(
        'fk_characters_background_id', 'characters', 'backgrounds', ['background_id'], ['id'], ondelete='SET NULL'
    )
    op.create_index(op.f('ix_characters_race_id'), 'characters', ['race_id'], unique=False)
    op.create_index(op.f('ix_characters_background_id'), 'characters', ['background_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_characters_background_id'), table_name='characters')
    op.drop_index(op.f('ix_characters_race_id'), table_name='characters')
    op.drop_constraint('fk_characters_background_id', 'characters', type_='foreignkey')
    op.drop_constraint('fk_characters_race_id', 'characters', type_='foreignkey')
    op.drop_column('characters', 'max_hp')
    op.drop_column('characters', 'experience_points')
    op.drop_column('characters', 'saving_throw_proficiencies')
    op.drop_column('characters', 'skill_proficiencies')
    op.drop_column('characters', 'background_id')
    op.drop_column('characters', 'race_id')
