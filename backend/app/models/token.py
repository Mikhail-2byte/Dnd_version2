from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from ..database import Base


class Token(Base):
    __tablename__ = "tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_id = Column(UUID(as_uuid=True), ForeignKey("game_sessions.id"), nullable=False)
    name = Column(String(255), nullable=False)
    x = Column(Float, nullable=False)  # Позиция X в процентах (0-100)
    y = Column(Float, nullable=False)  # Позиция Y в процентах (0-100)
    image_url = Column(String(500), nullable=True)
    character_id = Column(UUID(as_uuid=True), nullable=True)  # Для будущего использования
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    game = relationship("GameSession", back_populates="tokens")

