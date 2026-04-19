from sqlalchemy import Column, String, DateTime, ForeignKey, PrimaryKeyConstraint, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from ..database import Base
from .types import GUID


class GameParticipant(Base):
    __tablename__ = "game_participants"
    
    game_id = Column(GUID(), ForeignKey("game_sessions.id"), nullable=False)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    role = Column(String(20), nullable=False, default="player")  # 'master' or 'player'
    is_ready = Column(Boolean, nullable=False, default=False)
    character_id = Column(GUID(), ForeignKey("characters.id"), nullable=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        PrimaryKeyConstraint('game_id', 'user_id'),
    )
    
    # Relationships
    game = relationship("GameSession", back_populates="participants")
    user = relationship("User")
    character = relationship("Character")

