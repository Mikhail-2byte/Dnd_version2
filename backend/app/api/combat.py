"""
API эндпоинты для системы боя
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
from ..database import get_db
from ..models.user import User
from ..models.character import Character
from ..models.token import Token
from ..models.monster import Monster
from ..models.combat_session import CombatSession
from ..models.combat_participant import CombatParticipant
from ..middleware.auth import get_current_user
from ..schemas.combat import (
    CombatSessionResponse,
    CombatParticipantResponse,
    StartCombatRequest,
    RollInitiativeRequest,
    EndTurnRequest,
    AttackRequest,
    AttackResponse,
    DamageRequest,
    HealRequest,
    ConditionRequest,
    DeathSaveResult,
)
from ..services.combat_service import (
    start_combat,
    roll_initiative,
    get_initiative_order,
    get_current_combat,
    get_combat_session,
    end_combat,
    next_turn,
    perform_attack,
    apply_damage,
    apply_healing,
    apply_condition,
    remove_condition,
    roll_death_save,
)
from ..services.game_service import is_master, is_participant
from ..sockets.game_events import (
    emit_combat_started,
    emit_initiative_rolled,
    emit_combat_ended,
    emit_combat_attack,
    emit_combat_damage,
    emit_combat_heal,
    emit_participant_defeated,
)

router = APIRouter(prefix="/api/games/{game_id}/combat", tags=["combat"])


def _participant_to_response(participant, db: Session) -> CombatParticipantResponse:
    """Преобразование участника боя в ответ API"""
    character_name = None
    token_name = None
    
    if participant.character_id:
        character = db.query(Character).filter(Character.id == participant.character_id).first()
        if character:
            character_name = character.name
    
    if participant.token_id:
        token = db.query(Token).filter(Token.id == participant.token_id).first()
        if token:
            token_name = token.name
    
    return CombatParticipantResponse(
        id=participant.id,
        combat_id=participant.combat_id,
        character_id=participant.character_id,
        token_id=participant.token_id,
        initiative=participant.initiative,
        current_hp=participant.current_hp,
        max_hp=participant.max_hp,
        armor_class=participant.armor_class,
        conditions=participant.conditions,
        is_player_controlled=participant.is_player_controlled,
        character_name=character_name,
        token_name=token_name
    )


@router.post("/start", response_model=CombatSessionResponse, status_code=status.HTTP_201_CREATED)
async def start_combat_endpoint(
    game_id: UUID,
    request: StartCombatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Начало боевой сессии (только мастер)"""
    # Проверяем права мастера
    if not is_master(db, game_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только мастер может начать бой"
        )
    
    # Подготавливаем данные участников
    participant_data = []
    character_max_hp_map = {}
    character_armor_class_map = {}
    token_max_hp_map = {}
    token_armor_class_map = {}
    
    for participant_id in request.participant_ids:
        # Проверяем, это персонаж или токен
        character = db.query(Character).filter(Character.id == participant_id).first()
        token = db.query(Token).filter(Token.id == participant_id).first()
        
        if character:
            max_hp = character.max_hp or character.level * 10
            armor_class = character.armor_class or (10 + (character.dexterity - 10) // 2)
            
            participant_data.append({
                "character_id": participant_id,
                "max_hp": max_hp,
                "armor_class": armor_class,
                "is_player_controlled": True
            })
            character_max_hp_map[participant_id] = max_hp
            character_armor_class_map[participant_id] = armor_class
        elif token:
            # Это токен/монстр - используем значения по умолчанию или из токена
            max_hp = 10  # Значение по умолчанию для монстров
            armor_class = 10  # Значение по умолчанию
            
            participant_data.append({
                "token_id": participant_id,
                "max_hp": max_hp,
                "armor_class": armor_class,
                "is_player_controlled": False  # Монстры контролируются мастером
            })
            token_max_hp_map[participant_id] = max_hp
            token_armor_class_map[participant_id] = armor_class
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Participant {participant_id} not found (neither character nor token)"
            )
    
    # Создаем боевую сессию
    combat_session = start_combat(
        db,
        game_id,
        participant_data,
        character_max_hp_map,
        character_armor_class_map,
        token_max_hp_map,
        token_armor_class_map
    )
    
    # Получаем участников для ответа
    participants = combat_session.participants
    participant_responses = [_participant_to_response(p, db) for p in participants]
    
    response_data = CombatSessionResponse(
        id=combat_session.id,
        game_id=combat_session.game_id,
        is_active=combat_session.is_active,
        current_turn_index=combat_session.current_turn_index,
        round_number=combat_session.round_number,
        started_at=combat_session.started_at,
        ended_at=combat_session.ended_at,
        participants=participant_responses
    )
    
    # Эмитируем WebSocket событие
    await emit_combat_started(game_id, response_data.model_dump())
    
    return response_data


@router.post("/{combat_id}/roll-initiative", response_model=CombatParticipantResponse)
async def roll_initiative_endpoint(
    game_id: UUID,
    combat_id: UUID,
    request: RollInitiativeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Бросок инициативы для участника боя"""
    # Проверяем, что пользователь является участником игры
    if not is_participant(db, game_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не являетесь участником этой игры"
        )
    
    # Проверяем, что боевая сессия существует и принадлежит игре
    combat = get_combat_session(db, combat_id)
    if combat.game_id != game_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Combat session not found for this game"
        )
    
    # Бросаем инициативу
    participant = roll_initiative(db, combat_id, request.participant_id, request.initiative_roll)
    
    participant_response = _participant_to_response(participant, db)
    
    # Эмитируем WebSocket событие
    await emit_initiative_rolled(game_id, participant_response.model_dump())
    
    return participant_response


@router.get("/current", response_model=Optional[CombatSessionResponse])
async def get_current_combat_endpoint(
    game_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение текущей активной боевой сессии"""
    # Проверяем, что пользователь является участником игры
    if not is_participant(db, game_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не являетесь участником этой игры"
        )
    
    combat = get_current_combat(db, game_id)
    
    if not combat:
        return None
    
    # Получаем участников
    participants = combat.participants
    participant_responses = [_participant_to_response(p, db) for p in participants]
    
    return CombatSessionResponse(
        id=combat.id,
        game_id=combat.game_id,
        is_active=combat.is_active,
        current_turn_index=combat.current_turn_index,
        round_number=combat.round_number,
        started_at=combat.started_at,
        ended_at=combat.ended_at,
        participants=participant_responses
    )


@router.post("/{combat_id}/end", response_model=CombatSessionResponse)
async def end_combat_endpoint(
    game_id: UUID,
    combat_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Завершение боевой сессии (только мастер)"""
    # Проверяем права мастера
    if not is_master(db, game_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только мастер может завершить бой"
        )
    
    # Проверяем, что боевая сессия существует и принадлежит игре
    combat = get_combat_session(db, combat_id)
    if combat.game_id != game_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Combat session not found for this game"
        )
    
    # Завершаем бой
    combat = end_combat(db, combat_id)
    
    # Получаем участников для ответа
    participants = combat.participants
    participant_responses = [_participant_to_response(p, db) for p in participants]
    
    response_data = CombatSessionResponse(
        id=combat.id,
        game_id=combat.game_id,
        is_active=combat.is_active,
        current_turn_index=combat.current_turn_index,
        round_number=combat.round_number,
        started_at=combat.started_at,
        ended_at=combat.ended_at,
        participants=participant_responses
    )
    
    # Эмитируем WebSocket событие
    await emit_combat_ended(game_id)
    
    return response_data


@router.post("/{combat_id}/attack", response_model=AttackResponse)
async def attack_endpoint(
    game_id: UUID,
    combat_id: UUID,
    request: AttackRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Выполнение атаки"""
    # Проверяем, что пользователь является участником игры
    if not is_participant(db, game_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не являетесь участником этой игры"
        )
    
    # Проверяем, что боевая сессия существует и принадлежит игре
    combat = get_combat_session(db, combat_id)
    if combat.game_id != game_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Combat session not found for this game"
        )
    
    if not combat.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Combat session is not active"
        )
    
    # Выполняем атаку
    attack_result = perform_attack(
        db,
        combat_id,
        request.attacker_id,
        request.target_id,
        request.attack_roll,
        request.modifier,
        advantage=request.advantage,
        damage_dice=request.damage_dice,
        damage_modifier=request.damage_modifier,
    )
    
    # Если попали, наносим урон
    was_defeated = False
    if attack_result["hit"] and attack_result["damage"]:
        target = apply_damage(db, combat_id, request.target_id, attack_result["damage"])
        
        # Если цель повержена, эмитим событие
        if target.current_hp <= 0:
            was_defeated = True
            await emit_participant_defeated(game_id, request.target_id)
        
        # Эмитим событие урона
        await emit_combat_damage(game_id, {
            "participant_id": str(request.target_id),
            "damage": attack_result["damage"],
            "current_hp": target.current_hp,
            "max_hp": target.max_hp,
            "was_defeated": was_defeated
        })
    
    # Эмитим событие атаки
    await emit_combat_attack(game_id, {
        "attacker_id": str(request.attacker_id),
        "target_id": str(request.target_id),
        **attack_result
    })
    
    return AttackResponse(**attack_result)


@router.post("/{combat_id}/damage", response_model=CombatParticipantResponse)
async def damage_endpoint(
    game_id: UUID,
    combat_id: UUID,
    request: DamageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Нанесение урона участнику боя"""
    # Проверяем, что пользователь является участником игры
    if not is_participant(db, game_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не являетесь участником этой игры"
        )
    
    # Проверяем, что боевая сессия существует и принадлежит игре
    combat = get_combat_session(db, combat_id)
    if combat.game_id != game_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Combat session not found for this game"
        )
    
    if not combat.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Combat session is not active"
        )
    
    # Наносим урон
    participant = apply_damage(db, combat_id, request.target_id, request.damage)
    
    # Если участник повержен, эмитим событие
    was_defeated = participant.current_hp <= 0
    if was_defeated:
        await emit_participant_defeated(game_id, request.target_id)
    
    # Эмитим событие урона
    await emit_combat_damage(game_id, {
        "participant_id": str(request.target_id),
        "damage": request.damage,
        "current_hp": participant.current_hp,
        "max_hp": participant.max_hp,
        "was_defeated": was_defeated
    })
    
    return _participant_to_response(participant, db)


@router.post("/{combat_id}/heal", response_model=CombatParticipantResponse)
async def heal_endpoint(
    game_id: UUID,
    combat_id: UUID,
    request: HealRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Исцеление участника боя"""
    # Проверяем, что пользователь является участником игры
    if not is_participant(db, game_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не являетесь участником этой игры"
        )
    
    # Проверяем, что боевая сессия существует и принадлежит игре
    combat = get_combat_session(db, combat_id)
    if combat.game_id != game_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Combat session not found for this game"
        )
    
    if not combat.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Combat session is not active"
        )
    
    # Применяем исцеление
    participant = apply_healing(db, combat_id, request.target_id, request.healing)

    # Эмитим событие исцеления
    await emit_combat_heal(game_id, {
        "participant_id": str(request.target_id),
        "healing": request.healing,
        "current_hp": participant.current_hp,
        "max_hp": participant.max_hp
    })

    return _participant_to_response(participant, db)


# ── New endpoints: next-turn, conditions, death saves ──────────────────────

@router.post("/{combat_id}/next-turn", response_model=CombatSessionResponse)
async def next_turn_endpoint(
    game_id: UUID,
    combat_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Следующий ход (только мастер). Сбрасывает действия текущего участника."""
    if not is_master(db, game_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Только мастер может переключать ходы")
    combat = get_combat_session(db, combat_id)
    if combat.game_id != game_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Combat not found")
    combat = next_turn(db, combat_id)
    participants = combat.participants
    participant_responses = [_participant_to_response(p, db) for p in participants]
    response_data = CombatSessionResponse(
        id=combat.id, game_id=combat.game_id, is_active=combat.is_active,
        current_turn_index=combat.current_turn_index, round_number=combat.round_number,
        started_at=combat.started_at, ended_at=combat.ended_at,
        participants=participant_responses,
    )
    from ..sockets.game_events import emit_turn_changed
    await emit_turn_changed(game_id, response_data.model_dump())
    return response_data


@router.post("/{combat_id}/participants/{participant_id}/condition", response_model=CombatParticipantResponse)
async def manage_condition_endpoint(
    game_id: UUID,
    combat_id: UUID,
    participant_id: UUID,
    request: ConditionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Добавить или снять состояние с участника (только мастер)."""
    if not is_master(db, game_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Только мастер может управлять состояниями")
    combat = get_combat_session(db, combat_id)
    if combat.game_id != game_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Combat not found")
    if request.action == "add":
        participant = apply_condition(db, combat_id, participant_id, request.condition)
    elif request.action == "remove":
        participant = remove_condition(db, combat_id, participant_id, request.condition)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="action must be 'add' or 'remove'")
    return _participant_to_response(participant, db)


@router.post("/{combat_id}/participants/{participant_id}/death-save", response_model=DeathSaveResult)
async def death_save_endpoint(
    game_id: UUID,
    combat_id: UUID,
    participant_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Бросок спасброска от смерти для участника с 0 HP."""
    if not is_participant(db, game_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Вы не участник этой игры")
    combat = get_combat_session(db, combat_id)
    if combat.game_id != game_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Combat not found")
    return roll_death_save(db, combat_id, participant_id)


@router.post("/{combat_id}/add-monster", response_model=CombatParticipantResponse, status_code=status.HTTP_201_CREATED)
async def add_monster_to_combat_endpoint(
    game_id: UUID,
    combat_id: UUID,
    monster_slug: str,
    use_average_hp: bool = True,
    x: float = 50.0,
    y: float = 50.0,
    custom_name: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Добавить монстра из бестиария в текущий бой (только мастер)."""
    import random
    import uuid

    if not is_master(db, game_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Только мастер может добавлять монстров")

    combat = get_combat_session(db, combat_id)
    if combat.game_id != game_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Combat not found")
    if not combat.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Combat is not active")

    monster = db.query(Monster).filter(Monster.slug == monster_slug).first()
    if not monster:
        raise HTTPException(status_code=404, detail=f"Monster '{monster_slug}' not found")

    # Roll or use average HP
    if use_average_hp or not monster.hp_dice:
        hp = monster.hp_average or 10
    else:
        try:
            parts = monster.hp_dice.lower().split("d")
            num_dice = int(parts[0])
            die_size = int(parts[1])
            hp = sum(random.randint(1, die_size) for _ in range(num_dice))
        except Exception:
            hp = monster.hp_average or 10

    token = Token(
        game_id=game_id,
        name=custom_name or monster.name,
        x=x,
        y=y,
        image_url=None,
    )
    db.add(token)
    db.flush()

    participant = CombatParticipant(
        combat_id=combat_id,
        token_id=token.id,
        initiative=random.randint(1, 20) + ((monster.dexterity - 10) // 2),
        current_hp=hp,
        max_hp=hp,
        armor_class=monster.armor_class or 10,
        is_player_controlled=False,
    )
    db.add(participant)
    db.commit()
    db.refresh(participant)
    return _participant_to_response(participant, db)
