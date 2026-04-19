"""
Модель боевой сессии
"""
from sqlalchemy import Column, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from ..database import Base
from .types import GUID


class CombatSession(Base):
    """Боевая сессия для игры"""
    __tablename__ = "combat_sessions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    game_id = Column(GUID(), ForeignKey("game_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    is_active = Column(Boolean, nullable=False, default=True)
    current_turn_index = Column(Integer, nullable=False, default=0)  # Индекс текущего хода в порядке инициативы
    round_number = Column(Integer, nullable=False, default=1)
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    game = relationship("GameSession", backref="combat_sessions")
    participants = relationship("CombatParticipant", back_populates="combat_session", cascade="all, delete-orphan")

