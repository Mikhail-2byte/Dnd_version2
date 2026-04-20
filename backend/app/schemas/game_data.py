from pydantic import BaseModel
from typing import Optional, List, Any
from uuid import UUID


class SubRaceResponse(BaseModel):
    id: UUID
    slug: str
    name: str
    name_en: Optional[str] = None
    ability_bonuses: Optional[dict] = None
    traits: Optional[list] = None
    darkvision: Optional[int] = None

    model_config = {"from_attributes": True}


class RaceResponse(BaseModel):
    id: UUID
    slug: str
    name: str
    name_en: Optional[str] = None
    source: Optional[str] = None
    speed: int
    size: str
    ability_bonuses: Optional[dict] = None
    traits: Optional[list] = None
    languages: Optional[list] = None
    darkvision: int
    description: Optional[str] = None
    subraces: List[SubRaceResponse] = []

    model_config = {"from_attributes": True}


class BackgroundResponse(BaseModel):
    id: UUID
    slug: str
    name: str
    name_en: Optional[str] = None
    source: Optional[str] = None
    skill_proficiencies: Optional[list] = None
    tool_proficiencies: Optional[list] = None
    languages: Optional[int] = None
    equipment: Optional[list] = None
    feature_name: Optional[str] = None
    feature_description: Optional[str] = None
    description: Optional[str] = None

    model_config = {"from_attributes": True}


class ClassFeatureResponse(BaseModel):
    id: UUID
    class_slug: str
    level: int
    feature_name: str
    feature_description: Optional[str] = None
    is_asi: bool
    feature_type: Optional[str] = None
    uses: Optional[Any] = None
    proficiency_bonus: Optional[int] = None

    model_config = {"from_attributes": True}


class SpellResponse(BaseModel):
    id: UUID
    slug: str
    name: str
    name_en: Optional[str] = None
    level: int
    school: Optional[str] = None
    casting_time: Optional[str] = None
    spell_range: Optional[str] = None
    components: Optional[dict] = None
    duration: Optional[str] = None
    concentration: bool
    ritual: bool
    description: Optional[str] = None
    higher_levels: Optional[str] = None
    classes: Optional[list] = None
    source: Optional[str] = None

    model_config = {"from_attributes": True}


class WeaponResponse(BaseModel):
    id: UUID
    slug: str
    name: str
    name_en: Optional[str] = None
    category: str
    damage_dice: Optional[str] = None
    damage_type: Optional[str] = None
    properties: Optional[list] = None
    range_normal: Optional[int] = None
    range_long: Optional[int] = None
    weight: Optional[float] = None
    cost_gp: Optional[float] = None
    ability: Optional[str] = None
    two_handed_damage: Optional[str] = None

    model_config = {"from_attributes": True}


class ArmorResponse(BaseModel):
    id: UUID
    slug: str
    name: str
    name_en: Optional[str] = None
    category: str
    base_ac: int
    dex_modifier: Optional[str] = None
    min_strength: Optional[int] = None
    stealth_disadvantage: Optional[bool] = None
    weight: Optional[float] = None
    cost_gp: Optional[float] = None

    model_config = {"from_attributes": True}


class MonsterActionResponse(BaseModel):
    id: UUID
    name: str
    action_type: str
    description: Optional[str] = None
    attack_bonus: Optional[int] = None
    damage_dice: Optional[str] = None
    damage_type: Optional[str] = None
    reach_ft: Optional[int] = None
    targets: Optional[str] = None

    model_config = {"from_attributes": True}


class MonsterResponse(BaseModel):
    id: UUID
    slug: str
    name: str
    name_en: Optional[str] = None
    monster_type: Optional[str] = None
    size: Optional[str] = None
    alignment: Optional[str] = None
    cr: Optional[float] = None
    xp_reward: Optional[int] = None
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10
    hp_dice: Optional[str] = None
    hp_average: Optional[int] = None
    armor_class: int = 10
    armor_type: Optional[str] = None
    speed: Optional[dict] = None
    damage_resistances: Optional[list] = None
    damage_immunities: Optional[list] = None
    damage_vulnerabilities: Optional[list] = None
    condition_immunities: Optional[list] = None
    saving_throws: Optional[dict] = None
    skills: Optional[dict] = None
    senses: Optional[dict] = None
    languages: Optional[str] = None
    description: Optional[str] = None
    source: Optional[str] = None
    all_actions: List[MonsterActionResponse] = []

    model_config = {"from_attributes": True}


class MonsterListResponse(BaseModel):
    id: UUID
    slug: str
    name: str
    name_en: Optional[str] = None
    monster_type: Optional[str] = None
    size: Optional[str] = None
    cr: Optional[float] = None
    xp_reward: Optional[int] = None
    hp_average: Optional[int] = None
    armor_class: int = 10

    model_config = {"from_attributes": True}


class ItemResponse(BaseModel):
    id: UUID
    slug: str
    name: str
    name_en: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    weight: Optional[float] = None
    cost_gp: Optional[float] = None

    model_config = {"from_attributes": True}


class SpawnMonsterRequest(BaseModel):
    monster_slug: str
    x: float = 50.0
    y: float = 50.0
    use_average_hp: bool = True
    custom_name: Optional[str] = None
