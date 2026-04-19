import logging
import json
import random
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, status
from uuid import UUID
from ..models.character import Character
from ..models.race import Race
from ..models.background import Background
from ..models.inventory import CharacterInventory
from ..models.item import Weapon, Armor
from ..schemas.character import CharacterCreate, CharacterUpdate

logger = logging.getLogger(__name__)

# XP thresholds to reach each level (PHB table)
XP_THRESHOLDS: Dict[int, int] = {
    1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500,
    6: 14000, 7: 23000, 8: 34000, 9: 48000, 10: 64000,
    11: 85000, 12: 100000, 13: 120000, 14: 140000, 15: 165000,
    16: 195000, 17: 225000, 18: 265000, 19: 305000, 20: 355000,
}

PROFICIENCY_BONUS: Dict[int, int] = {
    1: 2, 2: 2, 3: 2, 4: 2, 5: 3, 6: 3, 7: 3, 8: 3,
    9: 4, 10: 4, 11: 4, 12: 4, 13: 5, 14: 5, 15: 5, 16: 5,
    17: 6, 18: 6, 19: 6, 20: 6,
}


def get_level_for_xp(xp: int) -> int:
    level = 1
    for lvl in range(2, 21):
        if xp >= XP_THRESHOLDS[lvl]:
            level = lvl
        else:
            break
    return level


def get_proficiency_bonus(level: int) -> int:
    return PROFICIENCY_BONUS.get(max(1, min(20, level)), 2)


# Hit dice per class (Russian and English names)
_HIT_DICE: Dict[str, int] = {
    "Варвар": 12, "barbarian": 12,
    "Воин": 10, "fighter": 10, "Паладин": 10, "paladin": 10, "Следопыт": 10, "ranger": 10,
    "Бард": 8, "bard": 8, "Жрец": 8, "cleric": 8, "Друид": 8, "druid": 8,
    "Монах": 8, "monk": 8, "Плут": 8, "rogue": 8, "Колдун": 8, "warlock": 8,
    "Чародей": 6, "sorcerer": 6, "Маг": 6, "wizard": 6,
}

# Saving throw proficiencies per class
_SAVING_THROWS: Dict[str, List[str]] = {
    "Варвар": ["strength", "constitution"], "barbarian": ["strength", "constitution"],
    "Воин": ["strength", "constitution"], "fighter": ["strength", "constitution"],
    "Паладин": ["wisdom", "charisma"], "paladin": ["wisdom", "charisma"],
    "Следопыт": ["strength", "dexterity"], "ranger": ["strength", "dexterity"],
    "Бард": ["dexterity", "charisma"], "bard": ["dexterity", "charisma"],
    "Жрец": ["wisdom", "charisma"], "cleric": ["wisdom", "charisma"],
    "Друид": ["intelligence", "wisdom"], "druid": ["intelligence", "wisdom"],
    "Монах": ["strength", "dexterity"], "monk": ["strength", "dexterity"],
    "Плут": ["dexterity", "intelligence"], "rogue": ["dexterity", "intelligence"],
    "Колдун": ["wisdom", "charisma"], "warlock": ["wisdom", "charisma"],
    "Чародей": ["constitution", "charisma"], "sorcerer": ["constitution", "charisma"],
    "Маг": ["intelligence", "wisdom"], "wizard": ["intelligence", "wisdom"],
}


def _mod(score: int) -> int:
    return (score - 10) // 2


def compute_character_stats(
    char_class: str,
    level: int,
    strength: int,
    dexterity: int,
    constitution: int,
    intelligence: int,
    wisdom: int,
    charisma: int,
) -> Tuple[int, int, int, List[str]]:
    """Returns (max_hp, current_hp, armor_class, saving_throw_proficiencies)."""
    hit_die = _HIT_DICE.get(char_class, 8)
    con_mod = _mod(constitution)
    dex_mod = _mod(dexterity)

    # Level 1: max hit die + CON mod; subsequent levels: (hit_die//2 + 1) + CON mod
    max_hp = max(1, hit_die + con_mod + (level - 1) * (hit_die // 2 + 1 + con_mod))

    # AC: class-specific starting armor
    if char_class in ("Варвар", "barbarian"):
        ac = 10 + dex_mod + _mod(constitution)  # Unarmored Defense
    elif char_class in ("Маг", "wizard", "Чародей", "sorcerer", "Колдун", "warlock"):
        ac = 10 + dex_mod  # No armor proficiency
    elif char_class in ("Плут", "rogue", "Бард", "bard", "Следопыт", "ranger", "Монах", "monk", "Друид", "druid"):
        ac = 11 + min(dex_mod, 6)  # Leather armor
    else:
        ac = 16  # Chain mail (Воин, Паладин, Жрец)

    saving_throws = _SAVING_THROWS.get(char_class, ["strength", "constitution"])
    return max_hp, max_hp, ac, saving_throws


def create_character(db: Session, user_id: UUID, character_data: CharacterCreate) -> Character:
    """
    Создание нового персонажа
    
    Args:
        db: Сессия базы данных
        user_id: ID пользователя
        character_data: Данные для создания персонажа
        
    Returns:
        Созданный персонаж
        
    Raises:
        HTTPException: При ошибке создания
    """
    try:
        logger.info(f"Создание персонажа для пользователя {user_id}: {character_data.name}")

        max_hp, current_hp, armor_class, saving_throws = compute_character_stats(
            char_class=character_data.char_class,
            level=character_data.level,
            strength=character_data.strength,
            dexterity=character_data.dexterity,
            constitution=character_data.constitution,
            intelligence=character_data.intelligence,
            wisdom=character_data.wisdom,
            charisma=character_data.charisma,
        )

        race_id = None
        skill_proficiencies: List[str] = []

        if character_data.race_slug:
            race = db.query(Race).filter(Race.slug == character_data.race_slug).first()
            if race:
                race_id = race.id

        background_id = None
        if character_data.background_slug:
            bg = db.query(Background).filter(Background.slug == character_data.background_slug).first()
            if bg:
                background_id = bg.id
                if bg.skill_proficiencies:
                    skill_proficiencies = list(bg.skill_proficiencies)

        db_character = Character(
            user_id=user_id,
            name=character_data.name,
            race=character_data.race,
            char_class=character_data.char_class,
            level=character_data.level,
            strength=character_data.strength,
            dexterity=character_data.dexterity,
            constitution=character_data.constitution,
            intelligence=character_data.intelligence,
            wisdom=character_data.wisdom,
            charisma=character_data.charisma,
            max_hp=max_hp,
            current_hp=current_hp,
            armor_class=armor_class,
            skill_proficiencies=skill_proficiencies or None,
            saving_throw_proficiencies=saving_throws,
            experience_points=0,
            race_id=race_id,
            background_id=background_id,
            character_history=character_data.character_history,
            equipment_and_features=character_data.equipment_and_features,
            avatar_url=character_data.avatar_url,
        )
        db.add(db_character)
        db.commit()
        db.refresh(db_character)
        
        logger.info(f"Персонаж создан успешно: ID={db_character.id}, имя={character_data.name}")
        return db_character
        
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Ошибка целостности данных при создании персонажа: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка при создании персонажа. Проверьте данные."
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Ошибка базы данных при создании персонажа: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера при создании персонажа"
        )


def grant_xp(db: Session, character: Character, xp: int) -> Dict[str, Any]:
    """Add XP to character. Returns result with level_up flag."""
    old_level = character.level
    new_xp = (character.experience_points or 0) + xp
    character.experience_points = new_xp

    earned_level = get_level_for_xp(new_xp)
    level_up_available = earned_level > old_level

    db.commit()
    db.refresh(character)

    next_level_xp = XP_THRESHOLDS.get(old_level + 1) if old_level < 20 else None
    return {
        "xp_gained": xp,
        "total_xp": new_xp,
        "level_up_available": level_up_available,
        "earned_level": earned_level,
        "next_level_xp": next_level_xp,
    }


def level_up(db: Session, character: Character, take_average: bool = True) -> Character:
    """Increase character level by 1, recalculate HP."""
    if character.level >= 20:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already max level")

    hit_die = _HIT_DICE.get(character.char_class, 8)
    con_mod = _mod(character.constitution)

    if take_average:
        hp_gain = hit_die // 2 + 1 + con_mod
    else:
        hp_gain = max(1, random.randint(1, hit_die) + con_mod)

    character.level += 1
    character.max_hp = (character.max_hp or 0) + hp_gain
    character.current_hp = (character.current_hp or 0) + hp_gain

    # Sync level to XP if needed
    earned_level = get_level_for_xp(character.experience_points or 0)
    if character.level > earned_level:
        # Milestone: grant minimum XP for this level
        character.experience_points = XP_THRESHOLDS.get(character.level, 0)

    db.commit()
    db.refresh(character)
    return character


def short_rest(db: Session, character: Character, hit_dice_spent: int) -> Character:
    """Short rest: spend hit dice to recover HP."""
    hit_dice_spent = max(0, min(hit_dice_spent, character.level))
    if hit_dice_spent == 0:
        return character

    hit_die = _HIT_DICE.get(character.char_class, 8)
    con_mod = _mod(character.constitution)

    healed = sum(max(1, random.randint(1, hit_die) + con_mod) for _ in range(hit_dice_spent))
    max_hp = character.max_hp or 1
    character.current_hp = min(max_hp, (character.current_hp or 0) + healed)

    db.commit()
    db.refresh(character)
    return character


def long_rest(db: Session, character: Character) -> Character:
    """Long rest: fully restore HP."""
    character.current_hp = character.max_hp or 1
    db.commit()
    db.refresh(character)
    return character


def get_character_by_id(db: Session, character_id: UUID) -> Character:
    """
    Получение персонажа по ID

    Args:
        db: Сессия базы данных
        character_id: ID персонажа

    Returns:
        Персонаж

    Raises:
        HTTPException: Если персонаж не найден
    """
    try:
        character = db.query(Character).filter(Character.id == character_id).first()
        if not character:
            logger.warning(f"Персонаж с ID {character_id} не найден")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Character not found"
            )
        return character
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Ошибка базы данных при получении персонажа {character_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера при получении персонажа"
        )


def get_user_characters(db: Session, user_id: UUID) -> list[Character]:
    """
    Получение всех персонажей пользователя
    
    Args:
        db: Сессия базы данных
        user_id: ID пользователя
        
    Returns:
        Список персонажей пользователя
    """
    try:
        characters = db.query(Character).filter(Character.user_id == user_id).all()
        logger.debug(f"Найдено {len(characters)} персонажей для пользователя {user_id}")
        return characters
    except SQLAlchemyError as e:
        logger.error(f"Ошибка базы данных при получении персонажей пользователя {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера при получении списка персонажей"
        )


def update_character(db: Session, character_id: UUID, character_data: CharacterUpdate) -> Character:
    """
    Обновление персонажа
    
    Args:
        db: Сессия базы данных
        character_id: ID персонажа
        character_data: Данные для обновления
        
    Returns:
        Обновленный персонаж
        
    Raises:
        HTTPException: При ошибке обновления
    """
    try:
        logger.info(f"Обновление персонажа {character_id}")
        
        character = get_character_by_id(db, character_id)
        
        update_data = character_data.model_dump(exclude_unset=True, by_alias=False)
        # Преобразуем char_class из alias "class" если есть
        if "char_class" in update_data:
            character.char_class = update_data.pop("char_class")
        
        for field, value in update_data.items():
            if hasattr(character, field):
                setattr(character, field, value)
        
        db.commit()
        db.refresh(character)
        
        logger.info(f"Персонаж {character_id} обновлен успешно")
        return character
        
    except HTTPException:
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Ошибка целостности данных при обновлении персонажа {character_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка при обновлении персонажа. Проверьте данные."
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Ошибка базы данных при обновлении персонажа {character_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера при обновлении персонажа"
        )


def delete_character(db: Session, character_id: UUID) -> None:
    """
    Удаление персонажа
    
    Args:
        db: Сессия базы данных
        character_id: ID персонажа
        
    Raises:
        HTTPException: При ошибке удаления
    """
    try:
        logger.info(f"Удаление персонажа {character_id}")
        
        character = get_character_by_id(db, character_id)
        db.delete(character)
        db.commit()
        
        logger.info(f"Персонаж {character_id} удален успешно")
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Ошибка базы данных при удалении персонажа {character_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера при удалении персонажа"
        )


def validate_character_ownership(db: Session, character_id: UUID, user_id: UUID) -> bool:
    """
    Проверка, что персонаж принадлежит пользователю
    
    Args:
        db: Сессия базы данных
        character_id: ID персонажа
        user_id: ID пользователя
        
    Returns:
        True если персонаж принадлежит пользователю, False иначе
    """
    try:
        character = get_character_by_id(db, character_id)
        return character.user_id == user_id
    except HTTPException:
        return False


def get_character_templates() -> Dict[str, Dict[str, Any]]:
    """
    Загрузка шаблонов классов персонажей из JSON файла
    
    Returns:
        Словарь шаблонов, где ключ - имя класса, значение - данные шаблона
    """
    base_dir = Path(__file__).parent.parent.parent
    templates_path = base_dir / "data" / "character_templates.json"
    
    if not templates_path.exists():
        logger.warning(f"Файл шаблонов персонажей не найден: {templates_path}")
        return {}
    
    try:
        with open(templates_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка парсинга JSON шаблонов персонажей: {e}")
        return {}


def get_character_template(class_name: str) -> Dict[str, Any]:
    """
    Получение конкретного шаблона класса по имени
    
    Args:
        class_name: Имя класса (например, "warrior", "wizard")
        
    Returns:
        Данные шаблона класса
        
    Raises:
        ValueError: Если шаблон не найден
    """
    templates = get_character_templates()
    
    if class_name not in templates:
        available = ", ".join(templates.keys())
        raise ValueError(f"Шаблон класса '{class_name}' не найден. Доступные шаблоны: {available}")
    
    return templates[class_name]


def generate_ability_scores(
    method: str = "standard_array",
    class_template: Optional[Dict[str, Any]] = None
) -> Dict[str, int]:
    """
    Генерация характеристик персонажа различными методами
    
    Args:
        method: Метод генерации ("point_buy", "standard_array", "random")
        class_template: Опциональный шаблон класса для приоритизации характеристик
        
    Returns:
        Словарь с характеристиками: {"strength": 15, "dexterity": 14, ...}
        
    Raises:
        ValueError: Если указан неверный метод
    """
    if method == "standard_array":
        # Стандартный массив D&D 5e: [15, 14, 13, 12, 10, 8]
        scores = [15, 14, 13, 12, 10, 8]
        random.shuffle(scores)
        
    elif method == "point_buy":
        # Point Buy система: 27 очков для распределения
        # Каждая характеристика стоит очки в зависимости от значения:
        # 8-13: (значение - 8) очков
        # 14-15: (значение - 8) + 1 очко
        scores = []
        points_remaining = 27
        
        # Начинаем с базового значения 8 для всех характеристик
        base_scores = [8, 8, 8, 8, 8, 8]
        
        # Распределяем очки до достижения лимита
        while points_remaining > 0 and any(s < 15 for s in base_scores):
            # Выбираем случайную характеристику
            idx = random.randint(0, 5)
            
            if base_scores[idx] >= 15:
                continue
            
            # Рассчитываем стоимость повышения
            current = base_scores[idx]
            if current < 13:
                cost = 1
            elif current < 15:
                cost = 2
            else:
                cost = float('inf')
            
            if cost <= points_remaining:
                base_scores[idx] += 1
                points_remaining -= cost
        
        scores = base_scores
        random.shuffle(scores)
        
    elif method == "random":
        # Метод 4d6 drop lowest: бросаем 4d6, отбрасываем минимальный, повторяем 6 раз
        scores = []
        for _ in range(6):
            # Бросаем 4d6
            rolls = [random.randint(1, 6) for _ in range(4)]
            # Отбрасываем минимальный
            rolls.remove(min(rolls))
            # Суммируем оставшиеся 3
            scores.append(sum(rolls))
        
        # Сортируем по убыванию для лучшего распределения
        scores.sort(reverse=True)
        random.shuffle(scores)
        
    else:
        raise ValueError(f"Неверный метод генерации: {method}. Доступные: point_buy, standard_array, random")
    
    # Применяем приоритеты класса, если указан шаблон
    if class_template and "default_stats" in class_template:
        priority_stats = _get_class_stat_priorities(class_template["default_stats"])
        scores = _assign_scores_by_priority(scores, priority_stats)
    else:
        # Без шаблона - случайное распределение
        stat_names = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        random.shuffle(stat_names)
        scores = dict(zip(stat_names, scores))
    
    return scores


def _get_class_stat_priorities(default_stats: Dict[str, int]) -> List[str]:
    """
    Определяет приоритеты характеристик на основе шаблона класса
    Возвращает список характеристик от самой важной к наименее важной
    """
    # Сортируем характеристики по значению (от большего к меньшему)
    sorted_stats = sorted(default_stats.items(), key=lambda x: x[1], reverse=True)
    return [stat_name for stat_name, _ in sorted_stats]


def _assign_scores_by_priority(
    scores: List[int],
    priorities: List[str]
) -> Dict[str, int]:
    """
    Назначает значения характеристик согласно приоритетам класса
    Большие значения идут на приоритетные характеристики
    """
    sorted_scores = sorted(scores, reverse=True)
    result = {}
    for i, stat_name in enumerate(priorities):
        if i < len(sorted_scores):
            result[stat_name] = sorted_scores[i]
        else:
            result[stat_name] = 8
    return result


# ── Inventory ──────────────────────────────────────────────────────────────

def _mod(score: int) -> int:
    return (score - 10) // 2


def _compute_ac_from_armor(armor: Armor, dex: int) -> int:
    dex_mod = _mod(dex)
    if armor.dex_modifier == "full":
        return armor.base_ac + dex_mod
    elif armor.dex_modifier == "max2":
        return armor.base_ac + min(dex_mod, 2)
    else:
        return armor.base_ac


def get_inventory(db: Session, character_id: UUID) -> List[CharacterInventory]:
    return db.query(CharacterInventory).filter(
        CharacterInventory.character_id == character_id
    ).all()


def _enrich_inventory_item(db: Session, item: CharacterInventory) -> dict:
    data = {
        "id": str(item.id),
        "character_id": str(item.character_id),
        "item_type": item.item_type,
        "item_id": str(item.item_id),
        "quantity": item.quantity,
        "is_equipped": item.is_equipped,
        "slot": item.slot,
        "item_data": None,
    }
    if item.item_type == "weapon":
        weapon = db.query(Weapon).filter(Weapon.id == item.item_id).first()
        if weapon:
            data["item_data"] = {
                "name": weapon.name, "category": weapon.category,
                "damage_dice": weapon.damage_dice, "damage_type": weapon.damage_type,
                "properties": weapon.properties, "ability": weapon.ability,
                "weight": weapon.weight, "cost_gp": weapon.cost_gp,
            }
    elif item.item_type == "armor":
        armor = db.query(Armor).filter(Armor.id == item.item_id).first()
        if armor:
            data["item_data"] = {
                "name": armor.name, "category": armor.category,
                "base_ac": armor.base_ac, "dex_modifier": armor.dex_modifier,
                "min_strength": armor.min_strength,
                "stealth_disadvantage": armor.stealth_disadvantage,
                "weight": armor.weight, "cost_gp": armor.cost_gp,
            }
    return data


def get_inventory_enriched(db: Session, character_id: UUID) -> List[dict]:
    items = get_inventory(db, character_id)
    return [_enrich_inventory_item(db, item) for item in items]


def add_inventory_item(
    db: Session, character_id: UUID, item_type: str, item_id: UUID, quantity: int
) -> CharacterInventory:
    # Validate item exists
    if item_type == "weapon":
        if not db.query(Weapon).filter(Weapon.id == item_id).first():
            raise HTTPException(status_code=404, detail="Weapon not found")
    elif item_type == "armor":
        if not db.query(Armor).filter(Armor.id == item_id).first():
            raise HTTPException(status_code=404, detail="Armor not found")

    inv = CharacterInventory(
        character_id=character_id,
        item_type=item_type,
        item_id=item_id,
        quantity=quantity,
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv


def remove_inventory_item(db: Session, character_id: UUID, inv_id: UUID) -> None:
    item = db.query(CharacterInventory).filter(
        CharacterInventory.id == inv_id,
        CharacterInventory.character_id == character_id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    db.delete(item)
    db.commit()


def equip_inventory_item(
    db: Session, character: Character, inv_id: UUID, is_equipped: bool, slot: Optional[str]
) -> CharacterInventory:
    item = db.query(CharacterInventory).filter(
        CharacterInventory.id == inv_id,
        CharacterInventory.character_id == character.id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    item.is_equipped = is_equipped
    item.slot = slot if is_equipped else None

    # Recalculate AC when equipping/unequipping armor
    if item.item_type == "armor":
        if is_equipped:
            armor = db.query(Armor).filter(Armor.id == item.item_id).first()
            if armor:
                # Unequip any other armor first
                db.query(CharacterInventory).filter(
                    CharacterInventory.character_id == character.id,
                    CharacterInventory.item_type == "armor",
                    CharacterInventory.is_equipped == True,
                    CharacterInventory.id != inv_id,
                ).update({"is_equipped": False, "slot": None})
                character.armor_class = _compute_ac_from_armor(armor, character.dexterity)
        else:
            # Revert to base AC (10 + dex)
            character.armor_class = 10 + _mod(character.dexterity)

    db.commit()
    db.refresh(item)
    return item

