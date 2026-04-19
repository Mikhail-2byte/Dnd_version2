from sqlalchemy import Column, String, Integer, Float, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
import uuid
from ..database import Base
from .types import GUID


class Monster(Base):
    __tablename__ = "monsters"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    slug = Column(String(200), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False, index=True)
    name_en = Column(String(200))
    monster_type = Column(String(50), index=True)   # beast, undead, dragon, etc.
    size = Column(String(20))                        # tiny, small, medium, large, huge, gargantuan
    alignment = Column(String(50))
    cr = Column(Float, index=True)                  # challenge rating (0.125, 0.25, 0.5, 1-30)
    xp_reward = Column(Integer, default=0)

    # Ability scores
    strength = Column(Integer, default=10)
    dexterity = Column(Integer, default=10)
    constitution = Column(Integer, default=10)
    intelligence = Column(Integer, default=10)
    wisdom = Column(Integer, default=10)
    charisma = Column(Integer, default=10)

    # Combat stats
    hp_dice = Column(String(20))                    # e.g. "5d8"
    hp_average = Column(Integer)
    armor_class = Column(Integer, default=10)
    armor_type = Column(String(50))
    speed = Column(JSON)                             # {"walk": 30, "fly": 60, ...}

    # Resistances / immunities
    damage_resistances = Column(JSON)
    damage_immunities = Column(JSON)
    damage_vulnerabilities = Column(JSON)
    condition_immunities = Column(JSON)

    # Skills and senses
    saving_throws = Column(JSON)                     # {"str": "+5", "dex": "+3"}
    skills = Column(JSON)                            # {"perception": "+4"}
    senses = Column(JSON)                            # {"darkvision": 60, "passive_perception": 14}
    languages = Column(String(300))

    description = Column(Text)
    source = Column(String(50), default="MM")

    actions = relationship("MonsterAction", back_populates="monster",
                           primaryjoin="and_(MonsterAction.monster_id == Monster.id, "
                                       "MonsterAction.action_type == 'action')",
                           foreign_keys="MonsterAction.monster_id",
                           overlaps="legendary_actions,reactions,all_actions")

    all_actions = relationship("MonsterAction", back_populates="monster",
                               foreign_keys="MonsterAction.monster_id",
                               overlaps="actions,legendary_actions,reactions")


class MonsterAction(Base):
    __tablename__ = "monster_actions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    monster_id = Column(GUID(), ForeignKey("monsters.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    action_type = Column(String(30), nullable=False)  # action | legendary | lair | reaction | trait
    description = Column(Text)
    attack_bonus = Column(Integer, nullable=True)
    damage_dice = Column(String(30), nullable=True)
    damage_type = Column(String(50), nullable=True)
    reach_ft = Column(Integer, default=5)
    targets = Column(String(50), default="one target")

    monster = relationship("Monster", back_populates="all_actions",
                           foreign_keys=[monster_id],
                           overlaps="actions,legendary_actions,reactions")
