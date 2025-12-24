from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class CharacterCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Имя персонажа")
    race: str = Field(..., min_length=1, max_length=100, description="Раса")
    char_class: str = Field(..., alias="class", min_length=1, max_length=100, description="Класс")
    level: int = Field(default=1, ge=1, le=20, description="Уровень")
    strength: int = Field(default=10, ge=1, le=30, description="Сила")
    dexterity: int = Field(default=10, ge=1, le=30, description="Ловкость")
    constitution: int = Field(default=10, ge=1, le=30, description="Телосложение")
    intelligence: int = Field(default=10, ge=1, le=30, description="Интеллект")
    wisdom: int = Field(default=10, ge=1, le=30, description="Мудрость")
    charisma: int = Field(default=10, ge=1, le=30, description="Харизма")
    character_history: Optional[str] = Field(default=None, description="История персонажа")
    equipment_and_features: Optional[str] = Field(default=None, description="Снаряжение и особенности")
    avatar_url: Optional[str] = Field(default=None, max_length=500, description="URL аватара")

    class Config:
        populate_by_name = True


class CharacterUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    race: Optional[str] = Field(None, min_length=1, max_length=100)
    char_class: Optional[str] = Field(None, alias="class", min_length=1, max_length=100)
    level: Optional[int] = Field(None, ge=1, le=20)
    strength: Optional[int] = Field(None, ge=1, le=30)
    dexterity: Optional[int] = Field(None, ge=1, le=30)
    constitution: Optional[int] = Field(None, ge=1, le=30)
    intelligence: Optional[int] = Field(None, ge=1, le=30)
    wisdom: Optional[int] = Field(None, ge=1, le=30)
    charisma: Optional[int] = Field(None, ge=1, le=30)
    character_history: Optional[str] = None
    equipment_and_features: Optional[str] = None
    avatar_url: Optional[str] = Field(None, max_length=500)

    class Config:
        populate_by_name = True


class CharacterResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    race: str
    char_class: str = Field(..., validation_alias="char_class", serialization_alias="class")
    level: int
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int
    character_history: Optional[str]
    equipment_and_features: Optional[str]
    avatar_url: Optional[str]
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }


class CharacterListResponse(BaseModel):
    characters: list[CharacterResponse]

