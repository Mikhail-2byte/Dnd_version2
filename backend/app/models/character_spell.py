from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
import uuid
from ..database import Base
from .types import GUID


class CharacterSpell(Base):
    __tablename__ = "character_spells"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    character_id = Column(GUID(), ForeignKey("characters.id", ondelete="CASCADE"), nullable=False, index=True)
    spell_id = Column(GUID(), ForeignKey("spells.id", ondelete="CASCADE"), nullable=False)
    is_prepared = Column(Boolean, default=False, nullable=False)
    is_ritual = Column(Boolean, default=False, nullable=False)
    learned_at_level = Column(Integer, default=1)

    character = relationship("Character", backref="known_spells")
    spell = relationship("Spell")


class SpellSlotTracker(Base):
    __tablename__ = "spell_slot_trackers"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    character_id = Column(GUID(), ForeignKey("characters.id", ondelete="CASCADE"), nullable=False, index=True)
    spell_level = Column(Integer, nullable=False)  # 1-9
    max_slots = Column(Integer, nullable=False, default=0)
    used_slots = Column(Integer, nullable=False, default=0)

    character = relationship("Character", backref="spell_slots")
