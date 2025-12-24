from sqlalchemy import Column, String, DateTime, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from ..database import Base


class GameParticipant(Base):
    __tablename__ = "game_participants"
    
    game_id = Column(UUID(as_uuid=True), ForeignKey("game_sessions.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role = Column(String(20), nullable=False, default="player")  # 'master' or 'player'
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        PrimaryKeyConstraint('game_id', 'user_id'),
    )
    
    # Relationships
    game = relationship("GameSession", back_populates="participants")
    user = relationship("User")

