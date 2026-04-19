"""
Seed-скрипт для заполнения таблиц races и subraces.
Данные взяты с https://dnd.su/races/
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.race import Race, SubRace

RACES = [
    {
        "slug": "human",
        "name": "Человек",
        "name_en": "Human",
        "source": "PHB",
        "speed": 30,
        "size": "Medium",
        "darkvision": 0,
        "ability_bonuses": {"str": 1, "dex": 1, "con": 1, "int": 1, "wis": 1, "cha": 1},
        "traits": [
            {"name": "Универсальность", "description": "Люди получают дополнительный навык владения одним навыком по выбору."},
        ],
        "languages": ["Общий", "Один язык на выбор"],
        "description": "Люди — самая распространённая раса в большинстве миров D&D. Их адаптивность, изобретательность и амбиции делают их доминирующей расой.",
        "subraces": [],
    },
    {
        "slug": "elf",
        "name": "Эльф",
        "name_en": "Elf",
        "source": "PHB",
        "speed": 30,
        "size": "Medium",
        "darkvision": 60,
        "ability_bonuses": {"dex": 2},
        "traits": [
            {"name": "Острые чувства", "description": "Владение навыком Внимательность."},
            {"name": "Наследие фей", "description": "Преимущество на спасброски против очарования, иммунитет к магическому усыплению."},
            {"name": "Транс", "description": "Эльфы не спят. Вместо этого они медитируют 4 часа в день."},
        ],
        "languages": ["Общий", "Эльфийский"],
        "description": "Эльфы — магический народ неземной красоты, живущий в мире, но не принадлежащий ему полностью.",
        "subraces": [
            {
                "slug": "high-elf",
                "name": "Высший эльф",
                "name_en": "High Elf",
                "ability_bonuses": {"int": 1},
                "darkvision": 60,
                "traits": [
                    {"name": "Владение оружием эльфов", "description": "Владение длинным мечом, коротким мечом, коротким луком и длинным луком."},
                    {"name": "Заговор", "description": "Знает один заговор из списка заклинаний волшебника. Характеристика — Интеллект."},
                    {"name": "Дополнительный язык", "description": "Знает один дополнительный язык на выбор."},
                ],
            },
            {
                "slug": "wood-elf",
                "name": "Лесной эльф",
                "name_en": "Wood Elf",
                "ability_bonuses": {"wis": 1},
                "darkvision": 60,
                "traits": [
                    {"name": "Владение оружием эльфов", "description": "Владение длинным мечом, коротким мечом, коротким луком и длинным луком."},
                    {"name": "Быстрые ноги", "description": "Скорость передвижения увеличена до 35 футов."},
                    {"name": "Маскировка в дикой природе", "description": "Можно скрываться, даже когда вас лишь слегка закрывают листва, сильный дождь, снегопад, туман и другие природные явления."},
                ],
            },
            {
                "slug": "drow",
                "name": "Дроу (Тёмный эльф)",
                "name_en": "Drow",
                "ability_bonuses": {"cha": 1},
                "darkvision": 120,
                "traits": [
                    {"name": "Превосходное тёмное зрение", "description": "Тёмное зрение 120 футов."},
                    {"name": "Чувствительность к солнечному свету", "description": "Помеха на броски атаки и проверки Внимательности, основанные на зрении, при ярком солнечном свете."},
                    {"name": "Магия дроу", "description": "Знает заговор Огни святилища. На 3-м уровне — Танцующие огни, на 5-м — Тьма. Характеристика — Харизма."},
                ],
            },
        ],
    },
    {
        "slug": "dwarf",
        "name": "Дварф",
        "name_en": "Dwarf",
        "source": "PHB",
        "speed": 25,
        "size": "Medium",
        "darkvision": 60,
        "ability_bonuses": {"con": 2},
        "traits": [
            {"name": "Дварфийская стойкость", "description": "Преимущество на спасброски от яда, сопротивление урону ядом."},
            {"name": "Дварфийское боевое обучение", "description": "Владение боевым топором, ручным топором, лёгким молотом и боевым молотом."},
            {"name": "Знание камня", "description": "Вдвое больше бонуса мастерства на проверки Истории, связанные с происхождением каменной работы."},
            {"name": "Инструментальное мастерство", "description": "Владение одним набором инструментов ремесленника."},
            {"name": "Устойчивость", "description": "Преимущество на спасброски против яда."},
        ],
        "languages": ["Общий", "Дварфийский"],
        "description": "Отважные и выносливые, дварфы известны как умелые воины, шахтёры и мастера по камню и металлу.",
        "subraces": [
            {
                "slug": "hill-dwarf",
                "name": "Холмовой дварф",
                "name_en": "Hill Dwarf",
                "ability_bonuses": {"wis": 1},
                "darkvision": 60,
                "traits": [
                    {"name": "Дварфийская живучесть", "description": "Максимум хитов увеличивается на 1, и увеличивается ещё на 1 каждый раз при получении уровня."},
                ],
            },
            {
                "slug": "mountain-dwarf",
                "name": "Горный дварф",
                "name_en": "Mountain Dwarf",
                "ability_bonuses": {"str": 2},
                "darkvision": 60,
                "traits": [
                    {"name": "Дварфийское боевое обучение", "description": "Владение лёгкими и средними доспехами."},
                ],
            },
        ],
    },
    {
        "slug": "halfling",
        "name": "Полурослик",
        "name_en": "Halfling",
        "source": "PHB",
        "speed": 25,
        "size": "Small",
        "darkvision": 0,
        "ability_bonuses": {"dex": 2},
        "traits": [
            {"name": "Удачливость", "description": "При выпадении 1 на кости атаки, проверки характеристик или спасброска, перебросьте кость и используйте новый результат."},
            {"name": "Храбрость", "description": "Преимущество на спасброски от испуга."},
            {"name": "Проворство полурослика", "description": "Можно свободно перемещаться сквозь пространство любого существа, размер которого больше вашего."},
        ],
        "languages": ["Общий", "Полуросличий"],
        "description": "Полурослики — жизнерадостный народ, ценящий спокойный образ жизни.",
        "subraces": [
            {
                "slug": "lightfoot-halfling",
                "name": "Легконогий полурослик",
                "name_en": "Lightfoot Halfling",
                "ability_bonuses": {"cha": 1},
                "darkvision": 0,
                "traits": [
                    {"name": "Природная скрытность", "description": "Можно предпринять попытку скрыться, даже когда вас закрывает лишь существо с размером не меньше Среднего."},
                ],
            },
            {
                "slug": "stout-halfling",
                "name": "Коренастый полурослик",
                "name_en": "Stout Halfling",
                "ability_bonuses": {"con": 1},
                "darkvision": 0,
                "traits": [
                    {"name": "Коренастая стойкость", "description": "Преимущество на спасброски против яда, сопротивление урону ядом."},
                ],
            },
        ],
    },
    {
        "slug": "gnome",
        "name": "Гном",
        "name_en": "Gnome",
        "source": "PHB",
        "speed": 25,
        "size": "Small",
        "darkvision": 60,
        "ability_bonuses": {"int": 2},
        "traits": [
            {"name": "Гномья хитрость", "description": "Преимущество на спасброски по Интеллекту, Мудрости и Харизме против магии."},
        ],
        "languages": ["Общий", "Гномий"],
        "description": "Гномы — энергичный и живой народ, обожающий жизнь во всей её полноте.",
        "subraces": [
            {
                "slug": "forest-gnome",
                "name": "Лесной гном",
                "name_en": "Forest Gnome",
                "ability_bonuses": {"dex": 1},
                "darkvision": 60,
                "traits": [
                    {"name": "Природная иллюзионист", "description": "Знает заговор Малая иллюзия. Интеллект — используемая характеристика."},
                    {"name": "Разговор с маленькими зверями", "description": "Может общаться с маленькими или меньшими зверями."},
                ],
            },
            {
                "slug": "rock-gnome",
                "name": "Скальный гном",
                "name_en": "Rock Gnome",
                "ability_bonuses": {"con": 1},
                "darkvision": 60,
                "traits": [
                    {"name": "Гномья смекалка", "description": "Вдвое больше бонуса мастерства на проверки Истории, связанные с магическими, алхимическими или технологическими предметами."},
                    {"name": "Мастер-иллюзионист", "description": "Может создавать небольшие механические устройства."},
                ],
            },
        ],
    },
    {
        "slug": "half-elf",
        "name": "Полуэльф",
        "name_en": "Half-Elf",
        "source": "PHB",
        "speed": 30,
        "size": "Medium",
        "darkvision": 60,
        "ability_bonuses": {"cha": 2},
        "traits": [
            {"name": "Бонус к двум характеристикам", "description": "+1 к двум характеристикам на выбор (не Харизма)."},
            {"name": "Наследие фей", "description": "Преимущество на спасброски против очарования, иммунитет к магическому усыплению."},
            {"name": "Универсальность навыков", "description": "Владение двумя навыками на выбор."},
        ],
        "languages": ["Общий", "Эльфийский", "Один язык на выбор"],
        "description": "Полуэльфы объединяют человеческую амбицию с утончённостью эльфов.",
        "subraces": [],
    },
    {
        "slug": "half-orc",
        "name": "Полуорк",
        "name_en": "Half-Orc",
        "source": "PHB",
        "speed": 30,
        "size": "Medium",
        "darkvision": 60,
        "ability_bonuses": {"str": 2, "con": 1},
        "traits": [
            {"name": "Угрожающий", "description": "Владение навыком Запугивание."},
            {"name": "Непоколебимая стойкость", "description": "Когда хиты должны упасть до 0, но не ниже, можно опуститься до 1 хита (раз в день)."},
            {"name": "Свирепые атаки", "description": "При крите в рукопашной атаке добавьте одну кость урона оружия."},
        ],
        "languages": ["Общий", "Орочий"],
        "description": "Некоторые полуорки поднимаются выше своего рождения, доказывая доблесть в приключениях.",
        "subraces": [],
    },
    {
        "slug": "tiefling",
        "name": "Тифлинг",
        "name_en": "Tiefling",
        "source": "PHB",
        "speed": 30,
        "size": "Medium",
        "darkvision": 60,
        "ability_bonuses": {"cha": 2, "int": 1},
        "traits": [
            {"name": "Адское сопротивление", "description": "Сопротивление урону огнём."},
            {"name": "Адское наследие", "description": "Знает заговор Огни святилища. На 3-м уровне — Адское возмездие (1/день). На 5-м — Тьма (1/день). Характеристика — Харизма."},
        ],
        "languages": ["Общий", "Инфернальный"],
        "description": "Тифлинги несут на себе печать дьявольской крови в качестве наследия давнего союза предков с демонами.",
        "subraces": [],
    },
    {
        "slug": "dragonborn",
        "name": "Драконорождённый",
        "name_en": "Dragonborn",
        "source": "PHB",
        "speed": 30,
        "size": "Medium",
        "darkvision": 0,
        "ability_bonuses": {"str": 2, "cha": 1},
        "traits": [
            {"name": "Драконье происхождение", "description": "Выбор одного из 10 видов дракона, определяющего тип урона и форму оружия дыхания."},
            {"name": "Оружие дыхания", "description": "Использует действие, чтобы выдохнуть разрушительную энергию. Урон: 2d6 (1-5 ур.), 3d6 (6-10), 4d6 (11-15), 5d6 (16-20). Спасбросок: КС 8 + Тел + Бонус мастерства."},
            {"name": "Сопротивление к урону", "description": "Сопротивление к типу урона, соответствующему происхождению."},
        ],
        "languages": ["Общий", "Драконий"],
        "description": "Драконорождённые походят на драконов, стоящих на двух ногах, и их происхождение берёт начало от дракона или бога дракона.",
        "subraces": [],
    },
]


def seed_races(db):
    existing = db.query(Race).count()
    if existing > 0:
        print(f"  Расы уже заполнены ({existing} записей), пропускаем.")
        return

    for race_data in RACES:
        subraces_data = race_data.pop("subraces", [])
        race = Race(**race_data)
        db.add(race)
        db.flush()

        for sr_data in subraces_data:
            sr_data["race_id"] = race.id
            subrace = SubRace(**sr_data)
            db.add(subrace)

    db.commit()
    print(f"  Добавлено рас: {len(RACES)}")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        print("Заполнение таблицы рас...")
        seed_races(db)
        print("Готово!")
    finally:
        db.close()
