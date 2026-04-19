"""
Доменный сервис для броска кубиков D&D
Основан на логике из Example/roll-dice
"""
import json
import os
import random
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from uuid import UUID
from sqlalchemy.orm import Session
from pathlib import Path
from ..models.dice_roll_history import DiceRollHistory


@dataclass
class DieRoll:
    """Результат броска одного кубика"""
    die_id: str
    value: int


@dataclass
class RollResult:
    """Результат броска кубиков"""
    rolls: List[DieRoll]
    total: int
    advantage_rolls: Optional[List[DieRoll]] = None  # Дополнительные броски для advantage/disadvantage
    selected_roll: Optional[DieRoll] = None  # Выбранный бросок (для advantage/disadvantage)
    advantage_type: Optional[str] = None  # "advantage", "disadvantage", или None


class DiceRoller:
    """
    Класс для броска кубиков D&D
    
    Поддерживает стандартные D&D кубики: d4, d6, d8, d10, d12, d20
    """
    
    # Стандартные D&D кубики
    ALLOWED_FACES = (4, 6, 8, 10, 12, 20)
    
    def __init__(self, default_faces: int = 12, max_dice: int = 10):
        """
        Инициализация DiceRoller
        
        Args:
            default_faces: Количество граней по умолчанию (по умолчанию 12)
            max_dice: Максимальное количество кубиков за один бросок (по умолчанию 10)
        """
        self.default_faces = default_faces
        self.max_dice = max_dice
    
    def roll(self, count: int, faces: Optional[int] = None, advantage: Optional[bool] = None) -> RollResult:
        """
        Бросок кубиков
        
        Args:
            count: Количество кубиков (должно быть положительным и не превышать max_dice)
            faces: Количество граней (если не указано, используется default_faces)
            advantage: True = преимущество, False = помеха, None = обычный бросок
                      Применяется только если count=1
            
        Returns:
            RollResult с результатами броска
            
        Raises:
            ValueError: Если параметры невалидны
        """
        if count <= 0:
            raise ValueError("Количество кубиков должно быть положительным")
        
        if count > self.max_dice:
            raise ValueError(
                f"Количество кубиков превышает допустимый максимум ({self.max_dice})"
            )
        
        actual_faces = faces if faces is not None else self.default_faces
        
        if actual_faces < 2:
            raise ValueError("Количество граней должно быть не менее 2")
        
        if actual_faces not in self.ALLOWED_FACES:
            allowed_str = ", ".join(map(str, self.ALLOWED_FACES))
            raise ValueError(
                f"Недопустимое количество граней: {actual_faces}. "
                f"Разрешены: {allowed_str}"
            )
        
        # Обработка advantage/disadvantage (только для одного кубика)
        advantage_rolls = None
        selected_roll = None
        advantage_type = None
        
        if advantage is not None and count == 1:
            # Бросаем два кубика
            roll1 = DieRoll(die_id="d1", value=self._generate_roll(actual_faces))
            roll2 = DieRoll(die_id="d2", value=self._generate_roll(actual_faces))
            advantage_rolls = [roll1, roll2]
            
            if advantage:  # Преимущество - выбираем максимальное
                selected_roll = roll1 if roll1.value >= roll2.value else roll2
                advantage_type = "advantage"
            else:  # Помеха - выбираем минимальное
                selected_roll = roll1 if roll1.value <= roll2.value else roll2
                advantage_type = "disadvantage"
            
            # Используем выбранный бросок как основной
            rolls = [selected_roll]
            total = selected_roll.value
        else:
            # Обычный бросок
            rolls: List[DieRoll] = []
            for i in range(count):
                value = self._generate_roll(actual_faces)
                rolls.append(DieRoll(
                    die_id=f"d{i + 1}",
                    value=value
                ))
            
            # Вычисляем сумму
            total = sum(die.value for die in rolls)
        
        return RollResult(
            rolls=rolls,
            total=total,
            advantage_rolls=advantage_rolls,
            selected_roll=selected_roll,
            advantage_type=advantage_type
        )
    
    def _generate_roll(self, faces: int) -> int:
        """
        Генерация случайного значения для одного кубика
        
        Args:
            faces: Количество граней
            
        Returns:
            Случайное значение от 1 до faces (включительно)
        """
        return random.randint(1, faces)
    
    def to_dict(self, result: RollResult) -> Dict:
        """
        Преобразование RollResult в словарь для API
        
        Args:
            result: Результат броска
            
        Returns:
            Словарь с результатами броска
        """
        result_dict = {
            "rolls": [
                {"die_id": die.die_id, "value": die.value}
                for die in result.rolls
            ],
            "total": result.total
        }
        
        # Добавляем информацию о advantage/disadvantage, если есть
        if result.advantage_rolls is not None:
            result_dict["advantage_rolls"] = [
                {"die_id": die.die_id, "value": die.value}
                for die in result.advantage_rolls
            ]
            if result.selected_roll:
                result_dict["selected_roll"] = {
                    "die_id": result.selected_roll.die_id,
                    "value": result.selected_roll.value
                }
            result_dict["advantage_type"] = result.advantage_type
        
        return result_dict


def get_ability_modifier(ability_score: int) -> int:
    """
    Расчет модификатора характеристики D&D
    
    Формула: (значение - 10) / 2, округленное вниз
    
    Args:
        ability_score: Значение характеристики (обычно от 1 до 20)
        
    Returns:
        Модификатор (может быть отрицательным)
    """
    return (ability_score - 10) // 2


def get_templates() -> Dict[str, Dict[str, Any]]:
    """
    Загрузка шаблонов бросков из JSON файла
    
    Returns:
        Словарь шаблонов, где ключ - имя шаблона, значение - данные шаблона
    """
    # Путь к файлу с шаблонами
    base_dir = Path(__file__).parent.parent.parent
    templates_path = base_dir / "data" / "dice_templates.json"
    
    if not templates_path.exists():
        # Если файл не найден, возвращаем пустой словарь
        return {}
    
    with open(templates_path, "r", encoding="utf-8") as f:
        return json.load(f)


def apply_template(template_name: str, character: Optional[Any] = None) -> Dict[str, Any]:
    """
    Применение шаблона броска к персонажу
    
    Args:
        template_name: Имя шаблона из JSON файла
        character: Объект персонажа (Character) для расчета модификатора
        
    Returns:
        Словарь с параметрами броска:
        - count: количество кубиков
        - faces: количество граней
        - roll_type: тип проверки
        - modifier: модификатор (рассчитывается из характеристики персонажа)
        
    Raises:
        ValueError: Если шаблон не найден или у персонажа нет требуемой характеристики
    """
    templates = get_templates()
    
    if template_name not in templates:
        raise ValueError(f"Шаблон '{template_name}' не найден")
    
    template = templates[template_name]
    result = {
        "count": template["count"],
        "faces": template["faces"],
        "roll_type": template["roll_type"],
        "modifier": None
    }
    
    # Если указан источник модификатора и есть персонаж, рассчитываем модификатор
    if "modifier_source" in template and character:
        ability_name = template["modifier_source"]
        
        # Получаем значение характеристики из персонажа
        if hasattr(character, ability_name):
            ability_score = getattr(character, ability_name)
            result["modifier"] = get_ability_modifier(ability_score)
        else:
            raise ValueError(f"У персонажа отсутствует характеристика '{ability_name}'")
    
    return result


def save_roll_history(
    db: Session,
    game_id: UUID,
    user_id: UUID,
    count: int,
    faces: int,
    rolls: List[Dict],
    total: int,
    roll_type: Optional[str] = None,
    modifier: Optional[int] = None,
    advantage_type: Optional[str] = None,
    advantage_rolls: Optional[List[Dict]] = None,
    selected_roll: Optional[Dict] = None
) -> DiceRollHistory:
    """
    Сохранение истории броска кубиков в базу данных
    
    Args:
        db: Сессия базы данных
        game_id: ID игры
        user_id: ID пользователя
        count: Количество кубиков
        faces: Количество граней
        rolls: Результаты бросков [{"die_id": "d1", "value": 5}, ...]
        total: Сумма всех бросков
        roll_type: Тип проверки (attack, save, skill, custom)
        modifier: Примененный модификатор
        advantage_type: Тип преимущества (advantage/disadvantage)
        advantage_rolls: Дополнительные броски при преимуществе/помехе
        selected_roll: Выбранный бросок при преимуществе/помехе
        
    Returns:
        Созданная запись истории
    """
    history_entry = DiceRollHistory(
        game_id=game_id,
        user_id=user_id,
        count=count,
        faces=faces,
        rolls=rolls,
        total=total,
        roll_type=roll_type,
        modifier=modifier,
        advantage_type=advantage_type,
        advantage_rolls=advantage_rolls,
        selected_roll=selected_roll
    )
    db.add(history_entry)
    db.commit()
    db.refresh(history_entry)
    return history_entry

