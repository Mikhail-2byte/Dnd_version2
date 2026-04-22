from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from ..database import Base
from .types import GUID


class Token(Base):
    __tablename__ = "tokens"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    game_id = Column(GUID(), ForeignKey("game_sessions.id"), nullable=False)
    name = Column(String(255), nullable=False)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    image_url = Column(String(500), nullable=True)
    character_id = Column(GUID(), nullable=True)
    is_hidden = Column(Boolean, default=False, nullable=False)
    token_type = Column(String(20), default='npc', nullable=False)
    token_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    game = relationship("GameSession", back_populates="tokens")

