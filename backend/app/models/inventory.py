from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
import uuid
from ..database import Base
from .types import GUID


class CharacterInventory(Base):
    __tablename__ = "character_inventory"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    character_id = Column(GUID(), ForeignKey("characters.id", ondelete="CASCADE"), nullable=False, index=True)
    item_type = Column(String(20), nullable=False)  # "weapon" | "armor" | "item"
    item_id = Column(GUID(), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    is_equipped = Column(Boolean, default=False, nullable=False)
    slot = Column(String(30), nullable=True)  # main_hand | off_hand | armor | shield

    __table_args__ = (
        CheckConstraint("item_type IN ('weapon', 'armor', 'item')", name="ck_inventory_item_type"),
    )

    character = relationship("Character", backref="inventory_items")
