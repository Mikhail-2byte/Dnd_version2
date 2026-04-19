"""
Seed-скрипт для заполнения таблиц weapons и armors.
Данные взяты из Player's Handbook D&D 5e / https://dnd.su/equipment/
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.item import Weapon, Armor

WEAPONS = [
    # ───────────── ПРОСТОЕ РУКОПАШНОЕ ОРУЖИЕ ─────────────
    {
        "slug": "club", "name": "Дубина", "name_en": "Club",
        "category": "Simple Melee", "damage_dice": "1d4", "damage_type": "Дробящий",
        "properties": ["Лёгкое"], "weight": 2.0, "cost_gp": 0.1, "ability": "str",
    },
    {
        "slug": "dagger", "name": "Кинжал", "name_en": "Dagger",
        "category": "Simple Melee", "damage_dice": "1d4", "damage_type": "Колющий",
        "properties": ["Фехтовальное", "Лёгкое", "Метательное"],
        "range_normal": 20, "range_long": 60, "weight": 0.5, "cost_gp": 2.0, "ability": "str",
    },
    {
        "slug": "greatclub", "name": "Большая дубина", "name_en": "Greatclub",
        "category": "Simple Melee", "damage_dice": "1d8", "damage_type": "Дробящий",
        "properties": ["Двуручное"], "weight": 5.0, "cost_gp": 0.2, "ability": "str",
    },
    {
        "slug": "handaxe", "name": "Ручной топор", "name_en": "Handaxe",
        "category": "Simple Melee", "damage_dice": "1d6", "damage_type": "Рубящий",
        "properties": ["Лёгкое", "Метательное"],
        "range_normal": 20, "range_long": 60, "weight": 1.0, "cost_gp": 5.0, "ability": "str",
    },
    {
        "slug": "javelin", "name": "Метательное копьё", "name_en": "Javelin",
        "category": "Simple Melee", "damage_dice": "1d6", "damage_type": "Колющий",
        "properties": ["Метательное"],
        "range_normal": 30, "range_long": 120, "weight": 1.0, "cost_gp": 0.5, "ability": "str",
    },
    {
        "slug": "light-hammer", "name": "Лёгкий молот", "name_en": "Light Hammer",
        "category": "Simple Melee", "damage_dice": "1d4", "damage_type": "Дробящий",
        "properties": ["Лёгкое", "Метательное"],
        "range_normal": 20, "range_long": 60, "weight": 1.0, "cost_gp": 2.0, "ability": "str",
    },
    {
        "slug": "mace", "name": "Булава", "name_en": "Mace",
        "category": "Simple Melee", "damage_dice": "1d6", "damage_type": "Дробящий",
        "properties": [], "weight": 2.0, "cost_gp": 5.0, "ability": "str",
    },
    {
        "slug": "quarterstaff", "name": "Боевой посох", "name_en": "Quarterstaff",
        "category": "Simple Melee", "damage_dice": "1d6", "damage_type": "Дробящий",
        "properties": ["Универсальное"], "two_handed_damage": "1d8",
        "weight": 2.0, "cost_gp": 0.2, "ability": "str",
    },
    {
        "slug": "spear", "name": "Копьё", "name_en": "Spear",
        "category": "Simple Melee", "damage_dice": "1d6", "damage_type": "Колющий",
        "properties": ["Метательное", "Универсальное"],
        "range_normal": 20, "range_long": 60,
        "two_handed_damage": "1d8", "weight": 1.5, "cost_gp": 1.0, "ability": "str",
    },
    # ───────────── ПРОСТОЕ ДАЛЬНОБОЙНОЕ ОРУЖИЕ ─────────────
    {
        "slug": "light-crossbow", "name": "Лёгкий арбалет", "name_en": "Light Crossbow",
        "category": "Simple Ranged", "damage_dice": "1d8", "damage_type": "Колющий",
        "properties": ["Боеприпасы", "Двуручное", "Перезарядка"],
        "range_normal": 80, "range_long": 320, "weight": 2.5, "cost_gp": 25.0, "ability": "dex",
    },
    {
        "slug": "shortbow", "name": "Короткий лук", "name_en": "Shortbow",
        "category": "Simple Ranged", "damage_dice": "1d6", "damage_type": "Колющий",
        "properties": ["Боеприпасы", "Двуручное"],
        "range_normal": 80, "range_long": 320, "weight": 1.0, "cost_gp": 25.0, "ability": "dex",
    },
    {
        "slug": "sling", "name": "Праща", "name_en": "Sling",
        "category": "Simple Ranged", "damage_dice": "1d4", "damage_type": "Дробящий",
        "properties": ["Боеприпасы"],
        "range_normal": 30, "range_long": 120, "weight": 0.0, "cost_gp": 0.1, "ability": "dex",
    },
    # ───────────── ВОИНСКОЕ РУКОПАШНОЕ ОРУЖИЕ ─────────────
    {
        "slug": "battleaxe", "name": "Боевой топор", "name_en": "Battleaxe",
        "category": "Martial Melee", "damage_dice": "1d8", "damage_type": "Рубящий",
        "properties": ["Универсальное"], "two_handed_damage": "1d10",
        "weight": 2.0, "cost_gp": 10.0, "ability": "str",
    },
    {
        "slug": "greataxe", "name": "Секира", "name_en": "Greataxe",
        "category": "Martial Melee", "damage_dice": "1d12", "damage_type": "Рубящий",
        "properties": ["Тяжёлое", "Двуручное"], "weight": 3.5, "cost_gp": 30.0, "ability": "str",
    },
    {
        "slug": "greatsword", "name": "Двуручный меч", "name_en": "Greatsword",
        "category": "Martial Melee", "damage_dice": "2d6", "damage_type": "Рубящий",
        "properties": ["Тяжёлое", "Двуручное"], "weight": 3.0, "cost_gp": 50.0, "ability": "str",
    },
    {
        "slug": "longsword", "name": "Длинный меч", "name_en": "Longsword",
        "category": "Martial Melee", "damage_dice": "1d8", "damage_type": "Рубящий",
        "properties": ["Универсальное"], "two_handed_damage": "1d10",
        "weight": 1.5, "cost_gp": 15.0, "ability": "str",
    },
    {
        "slug": "rapier", "name": "Рапира", "name_en": "Rapier",
        "category": "Martial Melee", "damage_dice": "1d8", "damage_type": "Колющий",
        "properties": ["Фехтовальное"], "weight": 1.0, "cost_gp": 25.0, "ability": "dex",
    },
    {
        "slug": "shortsword", "name": "Короткий меч", "name_en": "Shortsword",
        "category": "Martial Melee", "damage_dice": "1d6", "damage_type": "Колющий",
        "properties": ["Фехтовальное", "Лёгкое"], "weight": 1.0, "cost_gp": 10.0, "ability": "dex",
    },
    {
        "slug": "warhammer", "name": "Боевой молот", "name_en": "Warhammer",
        "category": "Martial Melee", "damage_dice": "1d8", "damage_type": "Дробящий",
        "properties": ["Универсальное"], "two_handed_damage": "1d10",
        "weight": 2.0, "cost_gp": 15.0, "ability": "str",
    },
    {
        "slug": "maul", "name": "Молот", "name_en": "Maul",
        "category": "Martial Melee", "damage_dice": "2d6", "damage_type": "Дробящий",
        "properties": ["Тяжёлое", "Двуручное"], "weight": 5.0, "cost_gp": 10.0, "ability": "str",
    },
    # ───────────── ВОИНСКОЕ ДАЛЬНОБОЙНОЕ ОРУЖИЕ ─────────────
    {
        "slug": "longbow", "name": "Длинный лук", "name_en": "Longbow",
        "category": "Martial Ranged", "damage_dice": "1d8", "damage_type": "Колющий",
        "properties": ["Боеприпасы", "Тяжёлое", "Двуручное"],
        "range_normal": 150, "range_long": 600, "weight": 1.0, "cost_gp": 50.0, "ability": "dex",
    },
    {
        "slug": "heavy-crossbow", "name": "Тяжёлый арбалет", "name_en": "Heavy Crossbow",
        "category": "Martial Ranged", "damage_dice": "1d10", "damage_type": "Колющий",
        "properties": ["Боеприпасы", "Тяжёлое", "Двуручное", "Перезарядка"],
        "range_normal": 100, "range_long": 400, "weight": 4.5, "cost_gp": 50.0, "ability": "dex",
    },
    {
        "slug": "hand-crossbow", "name": "Ручной арбалет", "name_en": "Hand Crossbow",
        "category": "Martial Ranged", "damage_dice": "1d6", "damage_type": "Колющий",
        "properties": ["Боеприпасы", "Лёгкое", "Перезарядка"],
        "range_normal": 30, "range_long": 120, "weight": 1.5, "cost_gp": 75.0, "ability": "dex",
    },
]

ARMORS = [
    # ───────────── ЛЁГКАЯ БРОНЯ ─────────────
    {
        "slug": "padded", "name": "Стёганая броня", "name_en": "Padded Armor",
        "category": "Light", "base_ac": 11, "dex_modifier": "full",
        "min_strength": 0, "stealth_disadvantage": True, "weight": 4.0, "cost_gp": 5.0,
    },
    {
        "slug": "leather", "name": "Кожаная броня", "name_en": "Leather Armor",
        "category": "Light", "base_ac": 11, "dex_modifier": "full",
        "min_strength": 0, "stealth_disadvantage": False, "weight": 5.0, "cost_gp": 10.0,
    },
    {
        "slug": "studded-leather", "name": "Клёпаная кожаная броня", "name_en": "Studded Leather",
        "category": "Light", "base_ac": 12, "dex_modifier": "full",
        "min_strength": 0, "stealth_disadvantage": False, "weight": 6.5, "cost_gp": 45.0,
    },
    # ───────────── СРЕДНЯЯ БРОНЯ ─────────────
    {
        "slug": "hide", "name": "Шкурная броня", "name_en": "Hide Armor",
        "category": "Medium", "base_ac": 12, "dex_modifier": "max2",
        "min_strength": 0, "stealth_disadvantage": False, "weight": 6.0, "cost_gp": 10.0,
    },
    {
        "slug": "chain-shirt", "name": "Кольчужная рубашка", "name_en": "Chain Shirt",
        "category": "Medium", "base_ac": 13, "dex_modifier": "max2",
        "min_strength": 0, "stealth_disadvantage": False, "weight": 10.0, "cost_gp": 50.0,
    },
    {
        "slug": "scale-mail", "name": "Чешуйчатый доспех", "name_en": "Scale Mail",
        "category": "Medium", "base_ac": 14, "dex_modifier": "max2",
        "min_strength": 0, "stealth_disadvantage": True, "weight": 22.5, "cost_gp": 50.0,
    },
    {
        "slug": "breastplate", "name": "Нагрудник", "name_en": "Breastplate",
        "category": "Medium", "base_ac": 14, "dex_modifier": "max2",
        "min_strength": 0, "stealth_disadvantage": False, "weight": 10.0, "cost_gp": 400.0,
    },
    {
        "slug": "half-plate", "name": "Полулаты", "name_en": "Half Plate",
        "category": "Medium", "base_ac": 15, "dex_modifier": "max2",
        "min_strength": 0, "stealth_disadvantage": True, "weight": 20.0, "cost_gp": 750.0,
    },
    # ───────────── ТЯЖЁЛАЯ БРОНЯ ─────────────
    {
        "slug": "ring-mail", "name": "Кольчуга-сетка", "name_en": "Ring Mail",
        "category": "Heavy", "base_ac": 14, "dex_modifier": "none",
        "min_strength": 0, "stealth_disadvantage": True, "weight": 20.0, "cost_gp": 30.0,
    },
    {
        "slug": "chain-mail", "name": "Кольчуга", "name_en": "Chain Mail",
        "category": "Heavy", "base_ac": 16, "dex_modifier": "none",
        "min_strength": 13, "stealth_disadvantage": True, "weight": 27.5, "cost_gp": 75.0,
    },
    {
        "slug": "splint", "name": "Ламеллярный доспех", "name_en": "Splint Armor",
        "category": "Heavy", "base_ac": 17, "dex_modifier": "none",
        "min_strength": 15, "stealth_disadvantage": True, "weight": 30.0, "cost_gp": 200.0,
    },
    {
        "slug": "plate", "name": "Латный доспех", "name_en": "Plate Armor",
        "category": "Heavy", "base_ac": 18, "dex_modifier": "none",
        "min_strength": 15, "stealth_disadvantage": True, "weight": 32.5, "cost_gp": 1500.0,
    },
    # ───────────── ЩИТ ─────────────
    {
        "slug": "shield", "name": "Щит", "name_en": "Shield",
        "category": "Shield", "base_ac": 2, "dex_modifier": "none",
        "min_strength": 0, "stealth_disadvantage": False, "weight": 3.0, "cost_gp": 10.0,
    },
]


def seed_weapons(db):
    existing = db.query(Weapon).count()
    if existing > 0:
        print(f"  Оружие: уже заполнено ({existing} записей), пропускаем.")
        return 0

    count = 0
    for data in WEAPONS:
        weapon = Weapon(**data)
        db.add(weapon)
        count += 1
    db.commit()
    print(f"  Оружие: добавлено {count} записей.")
    return count


def seed_armors(db):
    existing = db.query(Armor).count()
    if existing > 0:
        print(f"  Броня: уже заполнена ({existing} записей), пропускаем.")
        return 0

    count = 0
    for data in ARMORS:
        armor = Armor(**data)
        db.add(armor)
        count += 1
    db.commit()
    print(f"  Броня: добавлено {count} записей.")
    return count


if __name__ == "__main__":
    db = SessionLocal()
    try:
        print("Заполнение таблиц оружия и брони...")
        seed_weapons(db)
        seed_armors(db)
        print("Готово!")
    finally:
        db.close()
