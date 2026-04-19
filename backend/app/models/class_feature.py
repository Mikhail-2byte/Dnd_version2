from sqlalchemy import Column, String, Integer, Text, Boolean
from sqlalchemy.dialects.postgresql import JSON
import uuid
from ..database import Base
from .types import GUID


class ClassFeature(Base):
    __tablename__ = "class_features"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    class_slug = Column(String(100), nullable=False, index=True)
    level = Column(Integer, nullable=False, index=True)
    feature_name = Column(String(200), nullable=False)
    feature_description = Column(Text)
    is_asi = Column(Boolean, default=False)
    feature_type = Column(String(50), default="main")
    uses = Column(JSON)
    proficiency_bonus = Column(Integer)
