from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class CharacterCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    race: str = Field(..., min_length=1, max_length=100)
    char_class: str = Field(..., alias="class", min_length=1, max_length=100)
    level: int = Field(default=1, ge=1, le=20)
    strength: int = Field(default=10, ge=1, le=30)
    dexterity: int = Field(default=10, ge=1, le=30)
    constitution: int = Field(default=10, ge=1, le=30)
    intelligence: int = Field(default=10, ge=1, le=30)
    wisdom: int = Field(default=10, ge=1, le=30)
    charisma: int = Field(default=10, ge=1, le=30)
    # Game data references (optional, used to compute stats and proficiencies)
    race_slug: Optional[str] = Field(default=None, max_length=100)
    background_slug: Optional[str] = Field(default=None, max_length=100)
    # Narrative
    character_history: Optional[str] = None
    equipment_and_features: Optional[str] = None
    avatar_url: Optional[str] = Field(default=None, max_length=500)

    model_config = {"populate_by_name": True}


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
    current_hp: Optional[int] = Field(None, ge=0)
    max_hp: Optional[int] = Field(None, ge=1)
    armor_class: Optional[int] = Field(None, ge=1)
    skill_proficiencies: Optional[List[str]] = None
    saving_throw_proficiencies: Optional[List[str]] = None
    experience_points: Optional[int] = Field(None, ge=0)
    gold: Optional[int] = Field(None, ge=0)
    silver: Optional[int] = Field(None, ge=0)
    copper: Optional[int] = Field(None, ge=0)
    character_history: Optional[str] = None
    equipment_and_features: Optional[str] = None
    avatar_url: Optional[str] = Field(None, max_length=500)

    model_config = {"populate_by_name": True}


class GrantXPRequest(BaseModel):
    xp: int = Field(..., ge=1, description="Количество XP для начисления")


class GrantXPResponse(BaseModel):
    xp_gained: int
    total_xp: int
    level_up_available: bool
    earned_level: int
    next_level_xp: Optional[int] = None


class LevelUpRequest(BaseModel):
    take_average: bool = Field(default=True, description="True — взять среднее HP, False — бросить кубик")


class RestRequest(BaseModel):
    type: str = Field(..., description="'short' или 'long'")
    hit_dice_spent: int = Field(default=1, ge=0, le=20, description="Количество костей жизни для короткого отдыха")


class AbilityScoresGenerationRequest(BaseModel):
    method: str = Field(default="standard_array")
    class_name: Optional[str] = None


class AbilityScoresResponse(BaseModel):
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int
    method: str


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
    max_hp: Optional[int] = None
    current_hp: Optional[int] = None
    armor_class: Optional[int] = None
    skill_proficiencies: Optional[List[str]] = None
    saving_throw_proficiencies: Optional[List[str]] = None
    experience_points: Optional[int] = 0
    gold: Optional[int] = 0
    silver: Optional[int] = 0
    copper: Optional[int] = 0
    proficiency_bonus: Optional[int] = None
    character_history: Optional[str] = None
    equipment_and_features: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }


class CharacterListResponse(BaseModel):
    characters: list[CharacterResponse]


# ── Inventory schemas ──────────────────────────────────────────────────────

class InventoryItemResponse(BaseModel):
    id: UUID
    character_id: UUID
    item_type: str
    item_id: UUID
    quantity: int
    is_equipped: bool
    slot: Optional[str] = None
    item_data: Optional[dict] = None

    model_config = {"from_attributes": True}


class AddInventoryItemRequest(BaseModel):
    item_type: str = Field(..., pattern="^(weapon|armor|item)$")
    item_id: UUID
    quantity: int = Field(default=1, ge=1)


class EquipItemRequest(BaseModel):
    is_equipped: bool
    slot: Optional[str] = Field(default=None, description="main_hand | off_hand | armor | shield")


class InventoryResponse(BaseModel):
    items: List[InventoryItemResponse]


# ── Spellbook schemas ──────────────────────────────────────────────────────

class AddSpellRequest(BaseModel):
    spell_id: UUID


class PrepareSpellRequest(BaseModel):
    is_prepared: bool


class UseSpellSlotRequest(BaseModel):
    spell_level: int = Field(..., ge=1, le=9)


class SpellSlotInfo(BaseModel):
    spell_level: int
    max_slots: int
    used_slots: int
    available: int


class SpellbookSpellEntry(BaseModel):
    id: UUID
    spell_id: UUID
    is_prepared: bool
    is_ritual: bool
    learned_at_level: Optional[int] = None
    name: Optional[str] = None
    level: Optional[int] = None
    school: Optional[str] = None
    concentration: Optional[bool] = None
    ritual: Optional[bool] = None
    casting_time: Optional[str] = None
    spell_range: Optional[str] = None
    components: Optional[dict] = None
    duration: Optional[str] = None
    description: Optional[str] = None


class SpellbookResponse(BaseModel):
    spells: List[SpellbookSpellEntry]
    slots: List[SpellSlotInfo]
