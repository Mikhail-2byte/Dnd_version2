from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class GameCreate(BaseModel):
    name: str
    story: Optional[str] = None
    map_url: Optional[str] = None


class GameJoin(BaseModel):
    invite_code: str


class GameResponse(BaseModel):
    id: UUID
    name: str
    invite_code: str
    master_id: UUID
    map_url: Optional[str]
    story: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

