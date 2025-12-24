from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class TokenCreate(BaseModel):
    name: str
    x: float
    y: float
    image_url: Optional[str] = None


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
    
    class Config:
        from_attributes = True

