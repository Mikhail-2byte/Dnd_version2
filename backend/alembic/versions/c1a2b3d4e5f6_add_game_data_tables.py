"""add_game_data_tables

Revision ID: c1a2b3d4e5f6
Revises: b07a28270bc8
Create Date: 2026-04-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'c1a2b3d4e5f6'
down_revision = 'b07a28270bc8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'races',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('name_en', sa.String(100), nullable=True),
        sa.Column('source', sa.String(50), nullable=True),
        sa.Column('speed', sa.Integer(), nullable=True),
        sa.Column('size', sa.String(20), nullable=True),
        sa.Column('ability_bonuses', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('traits', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('languages', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('darkvision', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_races_slug'), 'races', ['slug'], unique=True)

    op.create_table(
        'subraces',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('race_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('name_en', sa.String(100), nullable=True),
        sa.Column('ability_bonuses', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('traits', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('darkvision', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['race_id'], ['races.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_subraces_slug'), 'subraces', ['slug'], unique=True)
    op.create_index(op.f('ix_subraces_race_id'), 'subraces', ['race_id'], unique=False)

    op.create_table(
        'backgrounds',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('name_en', sa.String(100), nullable=True),
        sa.Column('source', sa.String(50), nullable=True),
        sa.Column('skill_proficiencies', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('tool_proficiencies', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('languages', sa.Integer(), nullable=True),
        sa.Column('equipment', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('feature_name', sa.String(200), nullable=True),
        sa.Column('feature_description', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_backgrounds_slug'), 'backgrounds', ['slug'], unique=True)

    op.create_table(
        'class_features',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('class_slug', sa.String(100), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('feature_name', sa.String(200), nullable=False),
        sa.Column('feature_description', sa.Text(), nullable=True),
        sa.Column('is_asi', sa.Boolean(), nullable=True),
        sa.Column('feature_type', sa.String(50), nullable=True),
        sa.Column('uses', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('proficiency_bonus', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_class_features_class_slug'), 'class_features', ['class_slug'], unique=False)
    op.create_index(op.f('ix_class_features_level'), 'class_features', ['level'], unique=False)

    op.create_table(
        'spells',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('slug', sa.String(200), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('name_en', sa.String(200), nullable=True),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('school', sa.String(50), nullable=True),
        sa.Column('casting_time', sa.String(100), nullable=True),
        sa.Column('spell_range', sa.String(100), nullable=True),
        sa.Column('components', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('duration', sa.String(100), nullable=True),
        sa.Column('concentration', sa.Boolean(), nullable=True),
        sa.Column('ritual', sa.Boolean(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('higher_levels', sa.Text(), nullable=True),
        sa.Column('classes', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('source', sa.String(50), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_spells_slug'), 'spells', ['slug'], unique=True)
    op.create_index(op.f('ix_spells_name'), 'spells', ['name'], unique=False)
    op.create_index(op.f('ix_spells_level'), 'spells', ['level'], unique=False)
    op.create_index(op.f('ix_spells_school'), 'spells', ['school'], unique=False)

    op.create_table(
        'weapons',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('name_en', sa.String(100), nullable=True),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('damage_dice', sa.String(20), nullable=True),
        sa.Column('damage_type', sa.String(50), nullable=True),
        sa.Column('properties', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('range_normal', sa.Integer(), nullable=True),
        sa.Column('range_long', sa.Integer(), nullable=True),
        sa.Column('weight', sa.Float(), nullable=True),
        sa.Column('cost_gp', sa.Float(), nullable=True),
        sa.Column('ability', sa.String(20), nullable=True),
        sa.Column('two_handed_damage', sa.String(20), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_weapons_slug'), 'weapons', ['slug'], unique=True)
    op.create_index(op.f('ix_weapons_category'), 'weapons', ['category'], unique=False)

    op.create_table(
        'armors',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('name_en', sa.String(100), nullable=True),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('base_ac', sa.Integer(), nullable=False),
        sa.Column('dex_modifier', sa.String(20), nullable=True),
        sa.Column('min_strength', sa.Integer(), nullable=True),
        sa.Column('stealth_disadvantage', sa.Boolean(), nullable=True),
        sa.Column('weight', sa.Float(), nullable=True),
        sa.Column('cost_gp', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_armors_slug'), 'armors', ['slug'], unique=True)
    op.create_index(op.f('ix_armors_category'), 'armors', ['category'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_armors_category'), table_name='armors')
    op.drop_index(op.f('ix_armors_slug'), table_name='armors')
    op.drop_table('armors')

    op.drop_index(op.f('ix_weapons_category'), table_name='weapons')
    op.drop_index(op.f('ix_weapons_slug'), table_name='weapons')
    op.drop_table('weapons')

    op.drop_index(op.f('ix_spells_school'), table_name='spells')
    op.drop_index(op.f('ix_spells_level'), table_name='spells')
    op.drop_index(op.f('ix_spells_name'), table_name='spells')
    op.drop_index(op.f('ix_spells_slug'), table_name='spells')
    op.drop_table('spells')

    op.drop_index(op.f('ix_class_features_level'), table_name='class_features')
    op.drop_index(op.f('ix_class_features_class_slug'), table_name='class_features')
    op.drop_table('class_features')

    op.drop_index(op.f('ix_backgrounds_slug'), table_name='backgrounds')
    op.drop_table('backgrounds')

    op.drop_index(op.f('ix_subraces_race_id'), table_name='subraces')
    op.drop_index(op.f('ix_subraces_slug'), table_name='subraces')
    op.drop_table('subraces')

    op.drop_index(op.f('ix_races_slug'), table_name='races')
    op.drop_table('races')
