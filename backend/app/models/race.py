from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
import uuid
from ..database import Base
from .types import GUID


class Race(Base):
    __tablename__ = "races"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    name_en = Column(String(100))
    source = Column(String(50), default="PHB")
    speed = Column(Integer, default=30)
    size = Column(String(20), default="Medium")
    ability_bonuses = Column(JSON)
    traits = Column(JSON)
    languages = Column(JSON)
    darkvision = Column(Integer, default=0)
    description = Column(Text)

    subraces = relationship("SubRace", back_populates="race", cascade="all, delete-orphan")


class SubRace(Base):
    __tablename__ = "subraces"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    race_id = Column(GUID(), ForeignKey("races.id", ondelete="CASCADE"), nullable=False, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    name_en = Column(String(100))
    ability_bonuses = Column(JSON)
    traits = Column(JSON)
    darkvision = Column(Integer, nullable=True)

    race = relationship("Race", back_populates="subraces")
