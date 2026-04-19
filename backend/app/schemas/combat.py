from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class CombatParticipantResponse(BaseModel):
    id: UUID
    combat_id: UUID
    character_id: Optional[UUID] = None
    token_id: Optional[UUID] = None
    name: Optional[str] = None
    initiative: Optional[int] = None
    current_hp: int
    max_hp: int
    armor_class: int
    conditions: Optional[List[str]] = None
    is_player_controlled: bool
    # Action economy
    actions_used: Optional[int] = 0
    bonus_actions_used: Optional[int] = 0
    reaction_used: Optional[bool] = False
    # Death saves
    death_saves_success: Optional[int] = 0
    death_saves_failure: Optional[int] = 0
    is_dead: Optional[bool] = False
    character_name: Optional[str] = None
    token_name: Optional[str] = None

    model_config = {"from_attributes": True}


class CombatSessionResponse(BaseModel):
    id: UUID
    game_id: UUID
    is_active: bool
    current_turn_index: int
    round_number: int
    started_at: datetime
    ended_at: Optional[datetime] = None
    participants: List[CombatParticipantResponse] = []

    model_config = {"from_attributes": True}


class StartCombatRequest(BaseModel):
    participant_ids: List[UUID] = Field(..., description="ID участников (character_id или token_id)")


class RollInitiativeRequest(BaseModel):
    participant_id: UUID
    initiative_roll: Optional[int] = Field(None)


class AttackRequest(BaseModel):
    attacker_id: UUID
    target_id: UUID
    attack_roll: Optional[int] = None
    modifier: int = Field(0)
    advantage: Optional[str] = Field(None, description="'advantage' | 'disadvantage' | null")
    damage_dice: str = Field("1d6", description="Кости урона, напр. '1d8', '2d6'")
    damage_modifier: int = Field(0)


class DamageRequest(BaseModel):
    target_id: UUID
    damage: int = Field(..., ge=0)
    damage_type: Optional[str] = None


class HealRequest(BaseModel):
    target_id: UUID
    healing: int = Field(..., ge=0)


class EndTurnRequest(BaseModel):
    pass


class AttackResponse(BaseModel):
    hit: bool
    attack_roll: int
    rolls: Optional[List[int]] = None
    modifier: int
    total_attack: int
    target_ac: int
    critical: Optional[bool] = False
    auto_miss: Optional[bool] = False
    advantage: Optional[str] = None
    damage: Optional[int] = None
    damage_dice: Optional[str] = None


class ConditionRequest(BaseModel):
    action: str = Field(..., description="'add' | 'remove'")
    condition: str = Field(..., description="Название состояния: prone, stunned, poisoned, ...")


class DeathSaveResult(BaseModel):
    roll: int
    success: bool
    failure: bool
    stabilized: bool
    died: bool
    death_saves_success: int
    death_saves_failure: int
    regained_hp: Optional[int] = None
