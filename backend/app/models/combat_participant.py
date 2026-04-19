from sqlalchemy import Column, Integer, Boolean, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
import uuid
from ..database import Base
from .types import GUID


class CombatParticipant(Base):
    __tablename__ = "combat_participants"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    combat_id = Column(GUID(), ForeignKey("combat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    character_id = Column(GUID(), ForeignKey("characters.id", ondelete="CASCADE"), nullable=True)
    token_id = Column(GUID(), ForeignKey("tokens.id", ondelete="CASCADE"), nullable=True)
    name = Column(String(255), nullable=True)

    # Combat stats
    initiative = Column(Integer, nullable=True)
    current_hp = Column(Integer, nullable=False)
    max_hp = Column(Integer, nullable=False)
    armor_class = Column(Integer, nullable=False)
    is_player_controlled = Column(Boolean, nullable=False, default=True)

    # Conditions: list of condition slugs e.g. ["prone", "poisoned"]
    conditions = Column(JSON, nullable=True)

    # Action economy (reset at start of each turn)
    actions_used = Column(Integer, nullable=True, default=0)
    bonus_actions_used = Column(Integer, nullable=True, default=0)
    reaction_used = Column(Boolean, nullable=True, default=False)

    # Death saves
    death_saves_success = Column(Integer, nullable=True, default=0)
    death_saves_failure = Column(Integer, nullable=True, default=0)
    is_dead = Column(Boolean, nullable=True, default=False)

    combat_session = relationship("CombatSession", back_populates="participants")
    character = relationship("Character", backref="combat_participations")
    token = relationship("Token", backref="combat_participations")
