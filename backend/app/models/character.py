from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from ..database import Base
from .types import GUID


class Character(Base):
    __tablename__ = "characters"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    race = Column(String(100), nullable=False)
    char_class = Column("class", String(100), nullable=False)
    level = Column(Integer, default=1, nullable=False)

    # D&D ability scores
    strength = Column(Integer, default=10, nullable=False)
    dexterity = Column(Integer, default=10, nullable=False)
    constitution = Column(Integer, default=10, nullable=False)
    intelligence = Column(Integer, default=10, nullable=False)
    wisdom = Column(Integer, default=10, nullable=False)
    charisma = Column(Integer, default=10, nullable=False)

    # Combat stats (computed on creation, can be updated)
    max_hp = Column(Integer, nullable=True)
    current_hp = Column(Integer, nullable=True)
    armor_class = Column(Integer, nullable=True)

    # Proficiencies
    skill_proficiencies = Column(JSON, nullable=True)
    saving_throw_proficiencies = Column(JSON, nullable=True)

    # Progression
    experience_points = Column(Integer, default=0, nullable=True)

    # References to game data tables
    race_id = Column(GUID(), ForeignKey("races.id", ondelete="SET NULL"), nullable=True, index=True)
    background_id = Column(GUID(), ForeignKey("backgrounds.id", ondelete="SET NULL"), nullable=True, index=True)

    # Narrative fields
    character_history = Column(Text, nullable=True)
    equipment_and_features = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="characters")

    def to_dict(self) -> dict:
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'name': self.name,
            'race': self.race,
            'class': self.char_class,
            'level': self.level,
            'strength': self.strength,
            'dexterity': self.dexterity,
            'constitution': self.constitution,
            'intelligence': self.intelligence,
            'wisdom': self.wisdom,
            'charisma': self.charisma,
            'max_hp': self.max_hp,
            'current_hp': self.current_hp,
            'armor_class': self.armor_class,
            'skill_proficiencies': self.skill_proficiencies,
            'saving_throw_proficiencies': self.saving_throw_proficiencies,
            'experience_points': self.experience_points,
            'character_history': self.character_history,
            'equipment_and_features': self.equipment_and_features,
            'avatar_url': self.avatar_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
