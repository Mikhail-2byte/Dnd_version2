"""monsters and monster_actions tables

Revision ID: d3e4f5a6b7c8
Revises: c2d3e4f5a6b7
Create Date: 2026-04-19 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'd3e4f5a6b7c8'
down_revision = 'c2d3e4f5a6b7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'monsters',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('slug', sa.String(200), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('name_en', sa.String(200), nullable=True),
        sa.Column('monster_type', sa.String(50), nullable=True),
        sa.Column('size', sa.String(20), nullable=True),
        sa.Column('alignment', sa.String(50), nullable=True),
        sa.Column('cr', sa.Float(), nullable=True),
        sa.Column('xp_reward', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('strength', sa.Integer(), nullable=True, server_default='10'),
        sa.Column('dexterity', sa.Integer(), nullable=True, server_default='10'),
        sa.Column('constitution', sa.Integer(), nullable=True, server_default='10'),
        sa.Column('intelligence', sa.Integer(), nullable=True, server_default='10'),
        sa.Column('wisdom', sa.Integer(), nullable=True, server_default='10'),
        sa.Column('charisma', sa.Integer(), nullable=True, server_default='10'),
        sa.Column('hp_dice', sa.String(20), nullable=True),
        sa.Column('hp_average', sa.Integer(), nullable=True),
        sa.Column('armor_class', sa.Integer(), nullable=True, server_default='10'),
        sa.Column('armor_type', sa.String(50), nullable=True),
        sa.Column('speed', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('damage_resistances', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('damage_immunities', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('damage_vulnerabilities', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('condition_immunities', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('saving_throws', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('skills', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('senses', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('languages', sa.String(300), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('source', sa.String(50), nullable=True, server_default='MM'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_monsters_slug'), 'monsters', ['slug'], unique=True)
    op.create_index(op.f('ix_monsters_name'), 'monsters', ['name'])
    op.create_index(op.f('ix_monsters_cr'), 'monsters', ['cr'])
    op.create_index(op.f('ix_monsters_monster_type'), 'monsters', ['monster_type'])

    op.create_table(
        'monster_actions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('monster_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('action_type', sa.String(30), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('attack_bonus', sa.Integer(), nullable=True),
        sa.Column('damage_dice', sa.String(30), nullable=True),
        sa.Column('damage_type', sa.String(50), nullable=True),
        sa.Column('reach_ft', sa.Integer(), nullable=True, server_default='5'),
        sa.Column('targets', sa.String(50), nullable=True, server_default='one target'),
        sa.ForeignKeyConstraint(['monster_id'], ['monsters.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_monster_actions_monster_id', 'monster_actions', ['monster_id'])


def downgrade() -> None:
    op.drop_index('ix_monster_actions_monster_id', table_name='monster_actions')
    op.drop_table('monster_actions')
    op.drop_index(op.f('ix_monsters_monster_type'), table_name='monsters')
    op.drop_index(op.f('ix_monsters_cr'), table_name='monsters')
    op.drop_index(op.f('ix_monsters_name'), table_name='monsters')
    op.drop_index(op.f('ix_monsters_slug'), table_name='monsters')
    op.drop_table('monsters')
