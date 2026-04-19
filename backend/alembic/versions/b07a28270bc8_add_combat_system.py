"""add_combat_system

Revision ID: b07a28270bc8
Revises: 433206c2a14c
Create Date: 2025-12-26 00:42:18.123456

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql  # <-- ЭТА СТРОКА ВАЖНА!

# revision identifiers, used by Alembic.
revision = 'b07a28270bc8'
down_revision = '433206c2a14c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Создание таблицы combat_sessions
    op.create_table('combat_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('game_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('current_turn_index', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('round_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['game_id'], ['game_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_combat_sessions_game_id'), 'combat_sessions', ['game_id'], unique=False)
    op.create_index(op.f('ix_combat_sessions_is_active'), 'combat_sessions', ['is_active'], unique=False)

    # Создание таблицы combat_participants
    op.create_table('combat_participants',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('combat_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('character_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('token_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('initiative', sa.Integer(), nullable=True),
        sa.Column('current_hp', sa.Integer(), nullable=False),
        sa.Column('max_hp', sa.Integer(), nullable=False),
        sa.Column('armor_class', sa.Integer(), nullable=False),
        sa.Column('conditions', sa.JSON(), nullable=True),
        sa.Column('is_player_controlled', sa.Boolean(), nullable=False, server_default='true'),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ),
        sa.ForeignKeyConstraint(['combat_id'], ['combat_sessions.id'], ),
        sa.ForeignKeyConstraint(['token_id'], ['tokens.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('combat_id', 'character_id', name='unique_character_in_combat'),
        sa.UniqueConstraint('combat_id', 'token_id', name='unique_token_in_combat')
    )
    op.create_index(op.f('ix_combat_participants_combat_id'), 'combat_participants', ['combat_id'], unique=False)
    op.create_index(op.f('ix_combat_participants_character_id'), 'combat_participants', ['character_id'], unique=False)
    op.create_index(op.f('ix_combat_participants_token_id'), 'combat_participants', ['token_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_combat_participants_token_id'), table_name='combat_participants')
    op.drop_index(op.f('ix_combat_participants_character_id'), table_name='combat_participants')
    op.drop_index(op.f('ix_combat_participants_combat_id'), table_name='combat_participants')
    op.drop_table('combat_participants')
    op.drop_index(op.f('ix_combat_sessions_is_active'), table_name='combat_sessions')
    op.drop_index(op.f('ix_combat_sessions_game_id'), table_name='combat_sessions')
    op.drop_table('combat_sessions')