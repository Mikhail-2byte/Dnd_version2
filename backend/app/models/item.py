from sqlalchemy import Column, String, Integer, Text, Boolean, Float
from sqlalchemy.dialects.postgresql import JSON
import uuid
from ..database import Base
from .types import GUID


class Item(Base):
    __tablename__ = "items"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    name_en = Column(String(100))
    category = Column(String(50), index=True)  # potion, gear, tool, container, etc.
    description = Column(Text)
    weight = Column(Float, default=0)
    cost_gp = Column(Float, default=0)


class Weapon(Base):
    __tablename__ = "weapons"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    name_en = Column(String(100))
    category = Column(String(50), nullable=False, index=True)
    damage_dice = Column(String(20))
    damage_type = Column(String(50))
    properties = Column(JSON)
    range_normal = Column(Integer, default=0)
    range_long = Column(Integer, default=0)
    weight = Column(Float, default=0)
    cost_gp = Column(Float, default=0)
    ability = Column(String(20), default="str")
    two_handed_damage = Column(String(20))


class Armor(Base):
    __tablename__ = "armors"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    name_en = Column(String(100))
    category = Column(String(50), nullable=False, index=True)
    base_ac = Column(Integer, nullable=False)
    dex_modifier = Column(String(20), default="full")
    min_strength = Column(Integer, default=0)
    stealth_disadvantage = Column(Boolean, default=False)
    weight = Column(Float, default=0)
    cost_gp = Column(Float, default=0)
