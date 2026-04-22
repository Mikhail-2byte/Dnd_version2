from pydantic import BaseModel
from uuid import UUID
from typing import Optional, Any, Dict
from datetime import datetime


class TokenCreate(BaseModel):
    name: str
    x: float
    y: float
    image_url: Optional[str] = None
    is_hidden: bool = False
    token_type: str = 'npc'
    token_metadata: Optional[Dict[str, Any]] = None


class TokenUpdate(BaseModel):
    x: float
    y: float


class TokenResponse(BaseModel):
    id: UUID
    game_id: UUID
    name: str
    x: float
    y: float
    image_url: Optional[str]
    is_hidden: bool = False
    token_type: str = 'npc'
    token_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True

