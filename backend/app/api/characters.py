from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Dict, Any, List
from ..database import get_db
from ..models.user import User
from ..middleware.auth import get_current_user
from ..schemas.character import (
    CharacterCreate,
    CharacterUpdate,
    CharacterResponse,
    CharacterListResponse,
    AbilityScoresGenerationRequest,
    AbilityScoresResponse,
    GrantXPRequest,
    GrantXPResponse,
    LevelUpRequest,
    RestRequest,
    AddInventoryItemRequest,
    EquipItemRequest,
    InventoryItemResponse,
    InventoryResponse,
    AddSpellRequest,
    PrepareSpellRequest,
    UseSpellSlotRequest,
    SpellbookResponse,
)
from ..services.character_service import (
    create_character,
    get_character_by_id,
    get_user_characters,
    update_character,
    delete_character,
    validate_character_ownership,
    get_character_templates,
    get_character_template,
    generate_ability_scores,
    grant_xp,
    level_up,
    short_rest,
    long_rest,
    get_proficiency_bonus,
    get_inventory_enriched,
    add_inventory_item,
    remove_inventory_item,
    equip_inventory_item,
)


def _to_response(character) -> CharacterResponse:
    resp = CharacterResponse.model_validate(character)
    resp.proficiency_bonus = get_proficiency_bonus(character.level)
    return resp

router = APIRouter(prefix="/api/characters", tags=["characters"])


@router.get("/templates", response_model=Dict[str, Any])
async def get_character_templates_endpoint(
    current_user: User = Depends(get_current_user)
):
    """Получение всех доступных шаблонов классов персонажей"""
    templates = get_character_templates()
    return {"templates": templates}


@router.get("/templates/{class_name}", response_model=Dict[str, Any])
async def get_character_template_endpoint(
    class_name: str,
    current_user: User = Depends(get_current_user)
):
    """Получение конкретного шаблона класса по имени"""
    try:
        template = get_character_template(class_name)
        return {"template": template}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/generate-abilities", response_model=AbilityScoresResponse)
async def generate_abilities_endpoint(
    request: AbilityScoresGenerationRequest,
    current_user: User = Depends(get_current_user)
):
    """Генерация характеристик персонажа"""
    try:
        class_template = None
        if request.class_name:
            try:
                class_template = get_character_template(request.class_name)
            except ValueError:
                # Если класс не найден, игнорируем и генерируем без приоритетов
                pass
        
        scores = generate_ability_scores(request.method, class_template)
        
        return AbilityScoresResponse(
            strength=scores.get("strength", 10),
            dexterity=scores.get("dexterity", 10),
            constitution=scores.get("constitution", 10),
            intelligence=scores.get("intelligence", 10),
            wisdom=scores.get("wisdom", 10),
            charisma=scores.get("charisma", 10),
            method=request.method
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("", response_model=CharacterResponse, status_code=status.HTTP_201_CREATED)
async def create_character_endpoint(
    character_data: CharacterCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создание нового персонажа"""
    character = create_character(db, current_user.id, character_data)
    return _to_response(character)


@router.get("", response_model=CharacterListResponse)
async def get_characters_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение всех персонажей текущего пользователя"""
    characters = get_user_characters(db, current_user.id)
    return CharacterListResponse(characters=[_to_response(c) for c in characters])


@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character_endpoint(
    character_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение персонажа по ID"""
    character = get_character_by_id(db, character_id)
    if not validate_character_ownership(db, character_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have access to this character")
    return _to_response(character)


@router.put("/{character_id}", response_model=CharacterResponse)
async def update_character_endpoint(
    character_id: UUID,
    character_data: CharacterUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновление персонажа"""
    if not validate_character_ownership(db, character_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have access to this character")
    character = update_character(db, character_id, character_data)
    return _to_response(character)


@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character_endpoint(
    character_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удаление персонажа"""
    if not validate_character_ownership(db, character_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have access to this character")
    delete_character(db, character_id)
    return None


# ── Progression endpoints ──────────────────────────────────────────────────

@router.post("/{character_id}/grant-xp", response_model=GrantXPResponse)
async def grant_xp_endpoint(
    character_id: UUID,
    request: GrantXPRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Начислить XP персонажу (только владелец)"""
    if not validate_character_ownership(db, character_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have access to this character")
    character = get_character_by_id(db, character_id)
    return grant_xp(db, character, request.xp)


@router.post("/{character_id}/level-up", response_model=CharacterResponse)
async def level_up_endpoint(
    character_id: UUID,
    request: LevelUpRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Повысить уровень персонажа"""
    if not validate_character_ownership(db, character_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have access to this character")
    character = get_character_by_id(db, character_id)
    character = level_up(db, character, request.take_average)
    return _to_response(character)


@router.post("/{character_id}/rest", response_model=CharacterResponse)
async def rest_endpoint(
    character_id: UUID,
    request: RestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Отдых: short (тратит кости жизни) или long (полное восстановление HP)"""
    if not validate_character_ownership(db, character_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have access to this character")
    character = get_character_by_id(db, character_id)
    if request.type == "long":
        character = long_rest(db, character)
    elif request.type == "short":
        character = short_rest(db, character, request.hit_dice_spent)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="type must be 'short' or 'long'")
    from ..services.spell_service import recover_spell_slots
    recover_spell_slots(db, character, request.type)
    return _to_response(character)


# ── Inventory endpoints ────────────────────────────────────────────────────

@router.get("/{character_id}/inventory", response_model=InventoryResponse)
async def get_inventory_endpoint(
    character_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not validate_character_ownership(db, character_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have access to this character")
    items = get_inventory_enriched(db, character_id)
    return InventoryResponse(items=items)


@router.post("/{character_id}/inventory", response_model=InventoryItemResponse, status_code=status.HTTP_201_CREATED)
async def add_inventory_endpoint(
    character_id: UUID,
    request: AddInventoryItemRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not validate_character_ownership(db, character_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have access to this character")
    inv = add_inventory_item(db, character_id, request.item_type, request.item_id, request.quantity)
    return _enrich_inv(db, inv)


@router.delete("/{character_id}/inventory/{inv_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_inventory_endpoint(
    character_id: UUID,
    inv_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not validate_character_ownership(db, character_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have access to this character")
    remove_inventory_item(db, character_id, inv_id)


@router.put("/{character_id}/inventory/{inv_id}/equip", response_model=InventoryItemResponse)
async def equip_inventory_endpoint(
    character_id: UUID,
    inv_id: UUID,
    request: EquipItemRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not validate_character_ownership(db, character_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have access to this character")
    character = get_character_by_id(db, character_id)
    inv = equip_inventory_item(db, character, inv_id, request.is_equipped, request.slot)
    return _enrich_inv(db, inv)


def _enrich_inv(db, inv) -> InventoryItemResponse:
    from ..services.character_service import _enrich_inventory_item
    data = _enrich_inventory_item(db, inv)
    return InventoryItemResponse(**data)


# ── Spellbook endpoints ────────────────────────────────────────────────────

@router.get("/{character_id}/spellbook", response_model=SpellbookResponse)
async def get_spellbook_endpoint(
    character_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not validate_character_ownership(db, character_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have access to this character")
    from ..services.spell_service import get_spellbook
    return get_spellbook(db, character_id)


@router.post("/{character_id}/spells", status_code=status.HTTP_201_CREATED)
async def add_spell_endpoint(
    character_id: UUID,
    request: AddSpellRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not validate_character_ownership(db, character_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have access to this character")
    character = get_character_by_id(db, character_id)
    from ..services.spell_service import add_spell_to_spellbook
    cs = add_spell_to_spellbook(db, character, request.spell_id)
    return {"message": "Spell added", "id": str(cs.id)}


@router.delete("/{character_id}/spells/{spell_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_spell_endpoint(
    character_id: UUID,
    spell_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not validate_character_ownership(db, character_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have access to this character")
    from ..services.spell_service import remove_spell_from_spellbook
    remove_spell_from_spellbook(db, character_id, spell_id)


@router.put("/{character_id}/spells/{spell_id}/prepare", status_code=status.HTTP_200_OK)
async def prepare_spell_endpoint(
    character_id: UUID,
    spell_id: UUID,
    request: PrepareSpellRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not validate_character_ownership(db, character_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have access to this character")
    from ..services.spell_service import prepare_spell
    cs = prepare_spell(db, character_id, spell_id, request.is_prepared)
    return {"is_prepared": cs.is_prepared}


@router.post("/{character_id}/spell-slots/use", status_code=status.HTTP_200_OK)
async def use_spell_slot_endpoint(
    character_id: UUID,
    request: UseSpellSlotRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not validate_character_ownership(db, character_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have access to this character")
    from ..services.spell_service import use_spell_slot
    tracker = use_spell_slot(db, character_id, request.spell_level)
    return {"spell_level": tracker.spell_level, "used": tracker.used_slots, "max": tracker.max_slots}


@router.post("/{character_id}/spell-slots/initialize", status_code=status.HTTP_200_OK)
async def initialize_slots_endpoint(
    character_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Initialize spell slots based on class and level (call after level-up)."""
    if not validate_character_ownership(db, character_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have access to this character")
    character = get_character_by_id(db, character_id)
    from ..services.spell_service import initialize_spell_slots
    trackers = initialize_spell_slots(db, character)
    return {"slots_initialized": len(trackers)}

