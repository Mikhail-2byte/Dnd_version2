"""
Единый скрипт для заполнения всех таблиц игровых данных.
Запуск: python backend/data/seed_all.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from seed_races import seed_races
from seed_classes import seed_class_features
from seed_spells import seed_spells
from seed_backgrounds import seed_backgrounds
from seed_items import seed_weapons, seed_armors
from seed_generic_items import seed_generic_items
from seed_monsters import seed_monsters


def seed_all():
    db = SessionLocal()
    try:
        print("=" * 50)
        print("Заполнение базы данных игровыми данными D&D 5e")
        print("=" * 50)

        print("\n[1/8] Расы...")
        seed_races(db)

        print("[2/8] Предыстории...")
        seed_backgrounds(db)

        print("[3/8] Способности классов...")
        seed_class_features(db)

        print("[4/8] Заклинания...")
        seed_spells(db)

        print("[5/8] Оружие...")
        seed_weapons(db)

        print("[6/8] Броня...")
        seed_armors(db)

        print("[7/8] Снаряжение и предметы...")
        seed_generic_items(db)

        print("[8/8] Монстры...")
        seed_monsters(db)

        print("\n" + "=" * 50)
        print("База данных успешно заполнена!")
        print("=" * 50)
    except Exception as e:
        print(f"\nОшибка при заполнении: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_all()
