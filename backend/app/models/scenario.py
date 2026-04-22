import uuid
from sqlalchemy import Column, String, Text, Float, Boolean, Integer, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base
from .types import GUID


class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    owner_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    story = Column(Text, nullable=True)
    map_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User")
    npcs = relationship("ScenarioNPC", back_populates="scenario", cascade="all, delete-orphan")
    items = relationship("ScenarioHiddenItem", back_populates="scenario", cascade="all, delete-orphan")


class ScenarioNPC(Base):
    __tablename__ = "scenario_npcs"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    scenario_id = Column(GUID(), ForeignKey("scenarios.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    image_url = Column(String(500), nullable=True)
    is_hidden = Column(Boolean, default=True, nullable=False)
    monster_slug = Column(String(200), nullable=True)
    loot = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)

    scenario = relationship("Scenario", back_populates="npcs")


class ScenarioHiddenItem(Base):
    __tablename__ = "scenario_hidden_items"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    scenario_id = Column(GUID(), ForeignKey("scenarios.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    image_url = Column(String(500), nullable=True)
    item_type = Column(String(20), nullable=False)
    item_id = Column(GUID(), nullable=True)
    quantity = Column(Integer, default=1, nullable=False)
    notes = Column(Text, nullable=True)

    scenario = relationship("Scenario", back_populates="items")
