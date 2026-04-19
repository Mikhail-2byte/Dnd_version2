from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.dialects.postgresql import JSON
import uuid
from ..database import Base
from .types import GUID


class Background(Base):
    __tablename__ = "backgrounds"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    name_en = Column(String(100))
    source = Column(String(50), default="PHB")
    skill_proficiencies = Column(JSON)
    tool_proficiencies = Column(JSON)
    languages = Column(Integer, default=0)
    equipment = Column(JSON)
    feature_name = Column(String(200))
    feature_description = Column(Text)
    description = Column(Text)
