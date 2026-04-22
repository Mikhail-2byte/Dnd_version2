from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List, Any
from datetime import datetime


class LootEntry(BaseModel):
    item_type: str
    item_id: UUID
    quantity: int = 1


class ScenarioNPCCreate(BaseModel):
    name: str
    x: float
    y: float
    image_url: Optional[str] = None
    is_hidden: bool = True
    monster_slug: Optional[str] = None
    loot: Optional[List[LootEntry]] = None
    notes: Optional[str] = None


class ScenarioNPCUpdate(BaseModel):
    name: Optional[str] = None
    x: Optional[float] = None
    y: Optional[float] = None
    image_url: Optional[str] = None
    is_hidden: Optional[bool] = None
    monster_slug: Optional[str] = None
    loot: Optional[List[LootEntry]] = None
    notes: Optional[str] = None


class ScenarioNPCResponse(BaseModel):
    id: UUID
    scenario_id: UUID
    name: str
    x: float
    y: float
    image_url: Optional[str]
    is_hidden: bool
    monster_slug: Optional[str]
    loot: Optional[List[Any]]
    notes: Optional[str]

    class Config:
        from_attributes = True


class ScenarioHiddenItemCreate(BaseModel):
    name: str
    x: float
    y: float
    image_url: Optional[str] = None
    item_type: str
    item_id: Optional[UUID] = None
    quantity: int = 1
    notes: Optional[str] = None


class ScenarioHiddenItemUpdate(BaseModel):
    name: Optional[str] = None
    x: Optional[float] = None
    y: Optional[float] = None
    image_url: Optional[str] = None
    item_type: Optional[str] = None
    item_id: Optional[UUID] = None
    quantity: Optional[int] = None
    notes: Optional[str] = None


class ScenarioHiddenItemResponse(BaseModel):
    id: UUID
    scenario_id: UUID
    name: str
    x: float
    y: float
    image_url: Optional[str]
    item_type: str
    item_id: Optional[UUID]
    quantity: int
    notes: Optional[str]

    class Config:
        from_attributes = True


class ScenarioCreate(BaseModel):
    name: str
    story: Optional[str] = None
    map_url: Optional[str] = None


class ScenarioUpdate(BaseModel):
    name: Optional[str] = None
    story: Optional[str] = None
    map_url: Optional[str] = None


class ScenarioResponse(BaseModel):
    id: UUID
    owner_id: UUID
    name: str
    story: Optional[str]
    map_url: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    npcs: List[ScenarioNPCResponse] = []
    items: List[ScenarioHiddenItemResponse] = []

    class Config:
        from_attributes = True


class ScenarioListItem(BaseModel):
    id: UUID
    owner_id: UUID
    name: str
    story: Optional[str]
    map_url: Optional[str]
    created_at: datetime
    npc_count: int = 0
    item_count: int = 0

    class Config:
        from_attributes = True
