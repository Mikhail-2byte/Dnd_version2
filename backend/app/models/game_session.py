from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from ..database import Base


class GameSession(Base):
    __tablename__ = "game_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    invite_code = Column(String(6), unique=True, nullable=False, index=True)
    master_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    map_url = Column(String(500), nullable=True)
    story = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    master = relationship("User", foreign_keys=[master_id])
    participants = relationship("GameParticipant", back_populates="game", cascade="all, delete-orphan")
    tokens = relationship("Token", back_populates="game", cascade="all, delete-orphan")

