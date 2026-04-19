"""
Модель истории бросков кубиков
"""
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from ..database import Base
from .types import GUID


class DiceRollHistory(Base):
    """История бросков кубиков для игры"""
    __tablename__ = "dice_roll_history"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    game_id = Column(GUID(), ForeignKey("game_sessions.id"), nullable=False, index=True)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False, index=True)
    count = Column(Integer, nullable=False)  # Количество кубиков
    faces = Column(Integer, nullable=False)  # Количество граней
    rolls = Column(JSON, nullable=False)  # Результаты бросков: [{"die_id": "d1", "value": 5}, ...]
    total = Column(Integer, nullable=False)  # Сумма всех бросков
    roll_type = Column(String, nullable=True)  # Тип проверки: "attack", "save", "skill", "custom"
    modifier = Column(Integer, nullable=True)  # Примененный модификатор
    advantage_type = Column(String, nullable=True)  # "advantage", "disadvantage", или None
    advantage_rolls = Column(JSON, nullable=True)  # Дополнительные броски для advantage/disadvantage
    selected_roll = Column(JSON, nullable=True)  # Выбранный бросок {"die_id": "d1", "value": 15}
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    game = relationship("GameSession", backref="dice_rolls")
    user = relationship("User", backref="dice_rolls")

