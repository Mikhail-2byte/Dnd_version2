"""
Сервис для управления боевой системой
"""
import logging
import random
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from uuid import UUID
from ..models.combat_session import CombatSession
from ..models.combat_participant import CombatParticipant
from ..models.character import Character
from ..models.token import Token

logger = logging.getLogger(__name__)


def start_combat(
    db: Session,
    game_id: UUID,
    participant_data: list[dict],
    character_max_hp_map: Optional[dict[UUID, int]] = None,
    character_armor_class_map: Optional[dict[UUID, int]] = None,
    token_max_hp_map: Optional[dict[UUID, int]] = None,
    token_armor_class_map: Optional[dict[UUID, int]] = None
) -> CombatSession:
    """
    Начало боевой сессии
    
    Args:
        db: Сессия базы данных
        game_id: ID игры
        participant_data: Список словарей с данными участников:
            [{"character_id": UUID, "max_hp": int, "armor_class": int, "is_player_controlled": bool},
             {"token_id": UUID, "max_hp": int, "armor_class": int, "is_player_controlled": bool}]
    
    Returns:
        Созданная боевая сессия
        
    Raises:
        HTTPException: При ошибке создания
    """
    try:
        # Закрываем все активные бои в этой игре
        active_combats = db.query(CombatSession).filter(
            CombatSession.game_id == game_id,
            CombatSession.is_active == True
        ).all()
        
        for combat in active_combats:
            combat.is_active = False
            from datetime import datetime
            combat.ended_at = datetime.utcnow()
        
        # Создаем новую боевую сессию
        combat_session = CombatSession(
            game_id=game_id,
            is_active=True,
            current_turn_index=0,
            round_number=1
        )
        db.add(combat_session)
        db.flush()  # Получаем ID
        
        # Создаем участников боя
        for participant_info in participant_data:
            character_id = participant_info.get("character_id")
            token_id = participant_info.get("token_id")
            is_player_controlled = participant_info.get("is_player_controlled", True)
            
            # Определяем max_hp и armor_class
            max_hp = participant_info.get("max_hp")
            armor_class = participant_info.get("armor_class")
            
            if character_id:
                # Если это персонаж, берем из БД или из карты
                if max_hp is None:
                    if character_max_hp_map and character_id in character_max_hp_map:
                        max_hp = character_max_hp_map[character_id]
                    else:
                        max_hp = 10  # Значение по умолчанию
                if armor_class is None:
                    if character_armor_class_map and character_id in character_armor_class_map:
                        armor_class = character_armor_class_map[character_id]
                    else:
                        armor_class = 10  # Значение по умолчанию
            elif token_id:
                # Если это токен/монстр, берем из карты или используем значения по умолчанию
                if max_hp is None:
                    if token_max_hp_map and token_id in token_max_hp_map:
                        max_hp = token_max_hp_map[token_id]
                    else:
                        max_hp = participant_info.get("max_hp", 10)
                if armor_class is None:
                    if token_armor_class_map and token_id in token_armor_class_map:
                        armor_class = token_armor_class_map[token_id]
                    else:
                        armor_class = participant_info.get("armor_class", 10)
            
            participant = CombatParticipant(
                combat_id=combat_session.id,
                character_id=character_id,
                token_id=token_id,
                current_hp=max_hp,
                max_hp=max_hp,
                armor_class=armor_class,
                is_player_controlled=is_player_controlled,
                initiative=None  # Инициатива еще не брошена
            )
            db.add(participant)
        
        db.commit()
        db.refresh(combat_session)
        
        logger.info(f"Combat session {combat_session.id} started for game {game_id}")
        return combat_session
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error starting combat: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера при начале боя"
        )


def roll_initiative(db: Session, combat_id: UUID, participant_id: UUID, roll_value: Optional[int] = None) -> CombatParticipant:
    """
    Бросок инициативы для участника боя
    
    Args:
        db: Сессия базы данных
        combat_id: ID боевой сессии
        participant_id: ID участника боя
        roll_value: Значение броска (если не указано, генерируется случайно 1d20)
    
    Returns:
        Обновленный участник боя
        
    Raises:
        HTTPException: При ошибке
    """
    try:
        participant = db.query(CombatParticipant).filter(
            CombatParticipant.id == participant_id,
            CombatParticipant.combat_id == combat_id
        ).first()
        
        if not participant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Participant not found in combat"
            )
        
        # Если значение не указано, бросаем 1d20
        if roll_value is None:
            roll_value = random.randint(1, 20)
        
        participant.initiative = roll_value
        db.commit()
        db.refresh(participant)
        
        logger.info(f"Participant {participant_id} rolled initiative {roll_value} in combat {combat_id}")
        return participant
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error rolling initiative: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера при броске инициативы"
        )


def get_initiative_order(db: Session, combat_id: UUID) -> list[CombatParticipant]:
    """
    Получение порядка ходов по инициативе (сортировка по initiative DESC)
    
    Args:
        db: Сессия базы данных
        combat_id: ID боевой сессии
    
    Returns:
        Список участников, отсортированный по инициативе (от большего к меньшему)
    """
    participants = db.query(CombatParticipant).filter(
        CombatParticipant.combat_id == combat_id
    ).order_by(CombatParticipant.initiative.desc().nulls_last()).all()
    
    return participants


def get_current_combat(db: Session, game_id: UUID) -> Optional[CombatSession]:
    """
    Получение текущей активной боевой сессии для игры
    
    Args:
        db: Сессия базы данных
        game_id: ID игры
    
    Returns:
        Активная боевая сессия или None
    """
    return db.query(CombatSession).filter(
        CombatSession.game_id == game_id,
        CombatSession.is_active == True
    ).first()


def get_combat_session(db: Session, combat_id: UUID) -> CombatSession:
    """
    Получение боевой сессии по ID
    
    Args:
        db: Сессия базы данных
        combat_id: ID боевой сессии
    
    Returns:
        Боевая сессия
        
    Raises:
        HTTPException: Если сессия не найдена
    """
    combat = db.query(CombatSession).filter(CombatSession.id == combat_id).first()
    
    if not combat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Combat session not found"
        )
    
    return combat


def end_combat(db: Session, combat_id: UUID) -> CombatSession:
    """
    Завершение боевой сессии
    
    Args:
        db: Сессия базы данных
        combat_id: ID боевой сессии
    
    Returns:
        Завершенная боевая сессия
        
    Raises:
        HTTPException: При ошибке
    """
    try:
        combat = get_combat_session(db, combat_id)
        combat.is_active = False
        from datetime import datetime
        combat.ended_at = datetime.utcnow()
        
        db.commit()
        db.refresh(combat)
        
        logger.info(f"Combat session {combat_id} ended")
        return combat
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error ending combat: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера при завершении боя"
        )


def apply_damage(db: Session, combat_id: UUID, participant_id: UUID, damage: int, damage_type: Optional[str] = None) -> CombatParticipant:
    """
    Применение урона к участнику боя
    
    Args:
        db: Сессия базы данных
        combat_id: ID боевой сессии
        participant_id: ID участника
        damage: Количество урона
    
    Returns:
        Обновленный участник боя
        
    Raises:
        HTTPException: При ошибке
    """
    try:
        participant = db.query(CombatParticipant).filter(
            CombatParticipant.id == participant_id,
            CombatParticipant.combat_id == combat_id
        ).first()
        
        if not participant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Participant not found in combat"
            )
        
        # Apply resistance/immunity/vulnerability if damage_type provided
        if damage_type and damage > 0:
            dt = damage_type.lower()
            immunities = [i.lower() for i in (participant.damage_immunities or [])]
            resistances = [r.lower() for r in (participant.damage_resistances or [])]
            vulnerabilities = [v.lower() for v in (participant.damage_vulnerabilities or [])]
            if dt in immunities:
                damage = 0
            elif dt in resistances:
                damage = damage // 2
            elif dt in vulnerabilities:
                damage = damage * 2

        # Уменьшаем HP
        participant.current_hp = max(0, participant.current_hp - damage)
        
        # Если HP <= 0, добавляем условие
        if participant.current_hp <= 0:
            conditions = participant.conditions or []
            if "unconscious" not in conditions:
                conditions.append("unconscious")
            participant.conditions = conditions
        
        db.commit()
        db.refresh(participant)
        
        logger.info(
            f"Applied {damage} damage to participant {participant_id} in combat {combat_id}. "
            f"New HP: {participant.current_hp}/{participant.max_hp}"
        )
        
        return participant
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error applying damage: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера при нанесении урона"
        )


def apply_healing(db: Session, combat_id: UUID, participant_id: UUID, healing: int) -> CombatParticipant:
    """Apply healing to a combat participant."""
    try:
        participant = db.query(CombatParticipant).filter(
            CombatParticipant.id == participant_id,
            CombatParticipant.combat_id == combat_id
        ).first()
        if not participant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found in combat")

        participant.current_hp = min(participant.max_hp, participant.current_hp + healing)

        if participant.current_hp > 0:
            conditions = [c for c in (participant.conditions or []) if c != "unconscious"]
            participant.conditions = conditions if conditions else None
            participant.death_saves_success = 0
            participant.death_saves_failure = 0

        db.commit()
        db.refresh(participant)
        return participant

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error applying healing: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка при применении исцеления")


def next_turn(db: Session, combat_id: UUID) -> CombatSession:
    """Advance to the next participant in initiative order. Increments round when it wraps."""
    combat = get_combat_session(db, combat_id)
    if not combat.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Combat is not active")

    participants = get_initiative_order(db, combat_id)
    alive = [p for p in participants if not p.is_dead]
    if not alive:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No alive participants")

    # Reset actions for participant who just ended their turn
    if 0 <= combat.current_turn_index < len(alive):
        current = alive[combat.current_turn_index]
        current.actions_used = 0
        current.bonus_actions_used = 0
        current.reaction_used = False

    next_index = combat.current_turn_index + 1
    if next_index >= len(alive):
        next_index = 0
        combat.round_number += 1

    combat.current_turn_index = next_index
    db.commit()
    db.refresh(combat)
    return combat


def apply_condition(db: Session, combat_id: UUID, participant_id: UUID, condition: str) -> CombatParticipant:
    """Add a condition to a participant."""
    participant = db.query(CombatParticipant).filter(
        CombatParticipant.id == participant_id,
        CombatParticipant.combat_id == combat_id
    ).first()
    if not participant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found")

    conditions = list(participant.conditions or [])
    if condition not in conditions:
        conditions.append(condition)
    participant.conditions = conditions
    db.commit()
    db.refresh(participant)
    return participant


def remove_condition(db: Session, combat_id: UUID, participant_id: UUID, condition: str) -> CombatParticipant:
    """Remove a condition from a participant."""
    participant = db.query(CombatParticipant).filter(
        CombatParticipant.id == participant_id,
        CombatParticipant.combat_id == combat_id
    ).first()
    if not participant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found")

    conditions = [c for c in (participant.conditions or []) if c != condition]
    participant.conditions = conditions if conditions else None
    db.commit()
    db.refresh(participant)
    return participant


def roll_death_save(db: Session, combat_id: UUID, participant_id: UUID) -> dict:
    """Roll a death saving throw for an unconscious participant."""
    participant = db.query(CombatParticipant).filter(
        CombatParticipant.id == participant_id,
        CombatParticipant.combat_id == combat_id
    ).first()
    if not participant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found")
    if participant.current_hp > 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Participant is not unconscious")

    roll = random.randint(1, 20)
    result = {"roll": roll, "success": False, "failure": False, "stabilized": False, "died": False}

    if roll == 20:
        # Natural 20: regain 1 HP, remove unconscious
        participant.current_hp = 1
        participant.death_saves_success = 0
        participant.death_saves_failure = 0
        conditions = [c for c in (participant.conditions or []) if c != "unconscious"]
        participant.conditions = conditions or None
        result["success"] = True
        result["stabilized"] = True
        result["regained_hp"] = 1
    elif roll == 1:
        # Natural 1: count as 2 failures
        participant.death_saves_failure = min(3, (participant.death_saves_failure or 0) + 2)
        result["failure"] = True
    elif roll >= 10:
        participant.death_saves_success = min(3, (participant.death_saves_success or 0) + 1)
        result["success"] = True
    else:
        participant.death_saves_failure = min(3, (participant.death_saves_failure or 0) + 1)
        result["failure"] = True

    if (participant.death_saves_success or 0) >= 3 and not result.get("regained_hp"):
        participant.death_saves_success = 0
        participant.death_saves_failure = 0
        result["stabilized"] = True

    if (participant.death_saves_failure or 0) >= 3:
        participant.is_dead = True
        conditions = list(participant.conditions or [])
        if "unconscious" not in conditions:
            conditions.append("unconscious")
        if "dead" not in conditions:
            conditions.append("dead")
        participant.conditions = conditions
        result["died"] = True

    result["death_saves_success"] = participant.death_saves_success or 0
    result["death_saves_failure"] = participant.death_saves_failure or 0
    db.commit()
    db.refresh(participant)
    return result


def perform_attack(
    db: Session,
    combat_id: UUID,
    attacker_id: UUID,
    target_id: UUID,
    attack_roll: Optional[int] = None,
    modifier: int = 0,
    advantage: Optional[str] = None,
    damage_dice: str = "1d6",
    damage_modifier: int = 0,
) -> dict:
    """Roll an attack against a target and compute damage on hit."""
    target = db.query(CombatParticipant).filter(
        CombatParticipant.id == target_id,
        CombatParticipant.combat_id == combat_id,
    ).first()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target not found in combat")

    # Determine roll(s)
    if attack_roll is not None:
        rolls = [attack_roll]
    else:
        if advantage == "advantage":
            rolls = [random.randint(1, 20), random.randint(1, 20)]
        elif advantage == "disadvantage":
            rolls = [random.randint(1, 20), random.randint(1, 20)]
        else:
            rolls = [random.randint(1, 20)]

    if advantage == "advantage":
        natural_roll = max(rolls)
    elif advantage == "disadvantage":
        natural_roll = min(rolls)
    else:
        natural_roll = rolls[0]

    auto_miss = natural_roll == 1
    critical = natural_roll == 20
    total_attack = natural_roll + modifier
    hit = critical or (not auto_miss and total_attack >= target.armor_class)

    damage = None
    if hit:
        try:
            parts = damage_dice.lower().split("d")
            num_dice = int(parts[0]) if parts[0] else 1
            die_size = int(parts[1])
        except Exception:
            num_dice, die_size = 1, 6

        dice_count = num_dice * 2 if critical else num_dice
        damage = max(0, sum(random.randint(1, die_size) for _ in range(dice_count)) + damage_modifier)

    return {
        "hit": hit,
        "attack_roll": natural_roll,
        "rolls": rolls,
        "modifier": modifier,
        "total_attack": total_attack,
        "target_ac": target.armor_class,
        "critical": critical,
        "auto_miss": auto_miss,
        "advantage": advantage,
        "damage": damage,
        "damage_dice": damage_dice,
    }


ABILITY_TO_ATTR = {
    "strength": "strength",
    "dexterity": "dexterity",
    "constitution": "constitution",
    "intelligence": "intelligence",
    "wisdom": "wisdom",
    "charisma": "charisma",
}

PROFICIENCY_BONUS = {1: 2, 2: 2, 3: 2, 4: 2, 5: 3, 6: 3, 7: 3, 8: 3,
                     9: 4, 10: 4, 11: 4, 12: 4, 13: 5, 14: 5, 15: 5, 16: 5,
                     17: 6, 18: 6, 19: 6, 20: 6}


def roll_saving_throw(
    db: Session, combat_id: UUID, participant_id: UUID, ability: str, dc: int
) -> dict:
    """Roll a saving throw for a combat participant."""
    from ..models.character import Character

    participant = db.query(CombatParticipant).filter(
        CombatParticipant.id == participant_id,
        CombatParticipant.combat_id == combat_id
    ).first()
    if not participant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found")

    ability = ability.lower()
    if ability not in ABILITY_TO_ATTR:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unknown ability: {ability}")

    score = 10
    proficiency_bonus = 2
    has_proficiency = False

    if participant.character_id:
        char = db.query(Character).filter(Character.id == participant.character_id).first()
        if char:
            score = getattr(char, ABILITY_TO_ATTR[ability], 10)
            proficiency_bonus = PROFICIENCY_BONUS.get(char.level, 2)
            profs = char.saving_throw_proficiencies or []
            has_proficiency = ability in profs

    modifier = (score - 10) // 2
    if has_proficiency:
        modifier += proficiency_bonus

    roll = random.randint(1, 20)
    total = roll + modifier

    return {
        "participant_id": str(participant_id),
        "ability": ability,
        "dc": dc,
        "roll": roll,
        "modifier": modifier,
        "total": total,
        "success": total >= dc,
    }

