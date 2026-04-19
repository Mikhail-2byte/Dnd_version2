from sqlalchemy import Column, String, Integer, Text, Boolean
from sqlalchemy.dialects.postgresql import JSON
import uuid
from ..database import Base
from .types import GUID


class Spell(Base):
    __tablename__ = "spells"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    slug = Column(String(200), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False, index=True)
    name_en = Column(String(200))
    level = Column(Integer, nullable=False, index=True)
    school = Column(String(50), index=True)
    casting_time = Column(String(100))
    spell_range = Column(String(100))
    components = Column(JSON)
    duration = Column(String(100))
    concentration = Column(Boolean, default=False)
    ritual = Column(Boolean, default=False)
    description = Column(Text)
    higher_levels = Column(Text)
    classes = Column(JSON)
    source = Column(String(50), default="PHB")
