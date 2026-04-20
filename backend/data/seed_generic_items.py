"""
Seed-скрипт для таблицы items (снаряжение, инструменты, зелья).
Данные взяты из Player's Handbook D&D 5e / https://dnd.su/equipment/
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.item import Item

ITEMS = [
    # ─── Зелья ───────────────────────────────────────────────────────────────
    {
        "slug": "potion-of-healing",
        "name": "Зелье лечения", "name_en": "Potion of Healing",
        "category": "potion",
        "description": "Восстанавливает 2d4+2 HP при употреблении.",
        "weight": 0.5, "cost_gp": 50.0,
    },
    {
        "slug": "potion-of-greater-healing",
        "name": "Зелье значительного лечения", "name_en": "Potion of Greater Healing",
        "category": "potion",
        "description": "Восстанавливает 4d4+4 HP при употреблении.",
        "weight": 0.5, "cost_gp": 150.0,
    },
    {
        "slug": "potion-of-superior-healing",
        "name": "Зелье превосходного лечения", "name_en": "Potion of Superior Healing",
        "category": "potion",
        "description": "Восстанавливает 8d4+8 HP при употреблении.",
        "weight": 0.5, "cost_gp": 450.0,
    },
    {
        "slug": "antitoxin",
        "name": "Антитоксин", "name_en": "Antitoxin",
        "category": "potion",
        "description": "Существо, выпившее антитоксин, получает преимущество на спасброски от яда в течение 1 часа.",
        "weight": 0.5, "cost_gp": 50.0,
    },
    {
        "slug": "potion-of-fire-breath",
        "name": "Зелье огненного дыхания", "name_en": "Potion of Fire Breath",
        "category": "potion",
        "description": "После употребления можно бонусным действием выдохнуть огонь (3d6 урона, Спасбросок Ловкости DC 13).",
        "weight": 0.5, "cost_gp": 150.0,
    },
    # ─── Снаряжение приключенца ───────────────────────────────────────────────
    {
        "slug": "backpack",
        "name": "Рюкзак", "name_en": "Backpack",
        "category": "gear",
        "description": "Вмещает 30 фунтов снаряжения.",
        "weight": 5.0, "cost_gp": 2.0,
    },
    {
        "slug": "bedroll",
        "name": "Спальный мешок", "name_en": "Bedroll",
        "category": "gear",
        "description": "Необходим для полноценного отдыха в дикой местности.",
        "weight": 7.0, "cost_gp": 1.0,
    },
    {
        "slug": "blanket",
        "name": "Одеяло", "name_en": "Blanket",
        "category": "gear",
        "description": "Тёплое одеяло.",
        "weight": 3.0, "cost_gp": 0.5,
    },
    {
        "slug": "rope-hempen-50",
        "name": "Верёвка пеньковая (50 фут.)", "name_en": "Rope, Hempen (50 feet)",
        "category": "gear",
        "description": "Имеет 2 HP и может быть разорвана проверкой Силы DC 17.",
        "weight": 10.0, "cost_gp": 1.0,
    },
    {
        "slug": "rope-silk-50",
        "name": "Верёвка шёлковая (50 фут.)", "name_en": "Rope, Silk (50 feet)",
        "category": "gear",
        "description": "Имеет 2 HP и может быть разорвана проверкой Силы DC 17. Прочнее и легче пеньковой.",
        "weight": 5.0, "cost_gp": 10.0,
    },
    {
        "slug": "torch",
        "name": "Факел", "name_en": "Torch",
        "category": "gear",
        "description": "Освещает яркий свет в радиусе 20 футов и тусклый свет ещё на 20 футов в течение 1 часа.",
        "weight": 1.0, "cost_gp": 0.01,
    },
    {
        "slug": "tinderbox",
        "name": "Огниво", "name_en": "Tinderbox",
        "category": "gear",
        "description": "Позволяет разжечь огонь за 1 действие (или минуту при неблагоприятных условиях).",
        "weight": 1.0, "cost_gp": 0.5,
    },
    {
        "slug": "lantern-hooded",
        "name": "Фонарь с крышкой", "name_en": "Lantern, Hooded",
        "category": "gear",
        "description": "Освещает яркий свет в радиусе 30 футов и тусклый ещё на 30 футов. С закрытой крышкой — тусклый свет в 5 футах.",
        "weight": 2.0, "cost_gp": 5.0,
    },
    {
        "slug": "oil-flask",
        "name": "Масло (фляга)", "name_en": "Oil (flask)",
        "category": "gear",
        "description": "Можно поджечь или залить фонарь. Горит 6 часов в фонаре.",
        "weight": 1.0, "cost_gp": 0.1,
    },
    {
        "slug": "rations-1-day",
        "name": "Паёк (1 день)", "name_en": "Rations (1 day)",
        "category": "gear",
        "description": "Сухой паёк на один день: вяленое мясо, сухофрукты, галеты.",
        "weight": 2.0, "cost_gp": 0.5,
    },
    {
        "slug": "waterskin",
        "name": "Фляга для воды", "name_en": "Waterskin",
        "category": "gear",
        "description": "Вмещает 4 пинты жидкости.",
        "weight": 5.0, "cost_gp": 0.2,
    },
    {
        "slug": "crowbar",
        "name": "Ломик", "name_en": "Crowbar",
        "category": "gear",
        "description": "При использовании даёт преимущество на проверки Силы для открывания чего-либо.",
        "weight": 5.0, "cost_gp": 2.0,
    },
    {
        "slug": "grappling-hook",
        "name": "Кошка", "name_en": "Grappling Hook",
        "category": "gear",
        "description": "Позволяет закрепиться за выступ или поверхность.",
        "weight": 4.0, "cost_gp": 2.0,
    },
    {
        "slug": "mirror-steel",
        "name": "Стальное зеркало", "name_en": "Mirror, Steel",
        "category": "gear",
        "description": "Небольшое стальное зеркало, полезное для осмотра углов и базилисков.",
        "weight": 0.5, "cost_gp": 5.0,
    },
    {
        "slug": "piton",
        "name": "Скальный крюк", "name_en": "Piton",
        "category": "gear",
        "description": "Железный крюк для альпинизма.",
        "weight": 0.25, "cost_gp": 0.05,
    },
    {
        "slug": "shovel",
        "name": "Лопата", "name_en": "Shovel",
        "category": "gear",
        "description": "Обычная лопата для копания.",
        "weight": 5.0, "cost_gp": 2.0,
    },
    # ─── Инструменты ─────────────────────────────────────────────────────────
    {
        "slug": "thieves-tools",
        "name": "Воровские инструменты", "name_en": "Thieves' Tools",
        "category": "tool",
        "description": "Отмычки, маленький пилок, набор отвёрток, клещи и небольшое зеркало. Используются для вскрытия замков и обезвреживания ловушек.",
        "weight": 1.0, "cost_gp": 25.0,
    },
    {
        "slug": "herbalism-kit",
        "name": "Набор травника", "name_en": "Herbalism Kit",
        "category": "tool",
        "description": "Содержит щипцы, ступку и пестик, мешочки и флаконы. Позволяет создавать антитоксин и зелья лечения.",
        "weight": 3.0, "cost_gp": 5.0,
    },
    {
        "slug": "alchemists-supplies",
        "name": "Алхимические принадлежности", "name_en": "Alchemist's Supplies",
        "category": "tool",
        "description": "Стеклянная посуда, весы, спиртовка и различные химикаты для создания алхимических предметов.",
        "weight": 8.0, "cost_gp": 50.0,
    },
    {
        "slug": "healers-kit",
        "name": "Набор лекаря", "name_en": "Healer's Kit",
        "category": "tool",
        "description": "Бинты, мази и шины. Действие: стабилизировать существо с 0 HP без проверки Мудрости (Медицина). 10 использований.",
        "weight": 3.0, "cost_gp": 5.0,
    },
    {
        "slug": "disguise-kit",
        "name": "Набор для грима", "name_en": "Disguise Kit",
        "category": "tool",
        "description": "Краски для лица, парики и накладки. Используется для создания маскировок.",
        "weight": 3.0, "cost_gp": 25.0,
    },
    {
        "slug": "musical-instrument-lute",
        "name": "Музыкальный инструмент (лютня)", "name_en": "Lute",
        "category": "tool",
        "description": "Струнный инструмент, традиционный для бардов.",
        "weight": 2.0, "cost_gp": 35.0,
    },
    # ─── Контейнеры ──────────────────────────────────────────────────────────
    {
        "slug": "bag-of-holding",
        "name": "Мешок хранения", "name_en": "Bag of Holding",
        "category": "container",
        "description": "Волшебный предмет. Вмещает 500 фунтов, не превышая 64 кубических фута. Весит 15 фунтов.",
        "weight": 15.0, "cost_gp": 0.0,
    },
    {
        "slug": "pouch",
        "name": "Кошелёк", "name_en": "Pouch",
        "category": "container",
        "description": "Тканевый или кожаный кошелёк на 20 монет или 0.2 кубических фута.",
        "weight": 1.0, "cost_gp": 0.5,
    },
    {
        "slug": "chest",
        "name": "Сундук", "name_en": "Chest",
        "category": "container",
        "description": "Деревянный сундук с замком. Вмещает 300 фунтов или 12 кубических футов.",
        "weight": 25.0, "cost_gp": 5.0,
    },
    # ─── Прочее ───────────────────────────────────────────────────────────────
    {
        "slug": "holy-symbol-amulet",
        "name": "Священный символ (амулет)", "name_en": "Holy Symbol (Amulet)",
        "category": "gear",
        "description": "Амулет со священным символом. Используется как фокусировка для жрецов и паладинов.",
        "weight": 1.0, "cost_gp": 5.0,
    },
    {
        "slug": "arcane-focus-crystal",
        "name": "Магическая фокусировка (кристалл)", "name_en": "Arcane Focus (Crystal)",
        "category": "gear",
        "description": "Кристалл, используемый как фокусировка для заклинателей вместо материальных компонентов.",
        "weight": 1.0, "cost_gp": 10.0,
    },
    {
        "slug": "spellbook",
        "name": "Книга заклинаний", "name_en": "Spellbook",
        "category": "gear",
        "description": "Книга с 100 страницами для записи заклинаний волшебника.",
        "weight": 3.0, "cost_gp": 50.0,
    },
    {
        "slug": "component-pouch",
        "name": "Мешочек компонентов", "name_en": "Component Pouch",
        "category": "gear",
        "description": "Кожаный мешочек с материальными компонентами заклинаний стоимостью не более 1 золотой.",
        "weight": 2.0, "cost_gp": 25.0,
    },
    {
        "slug": "book",
        "name": "Книга", "name_en": "Book",
        "category": "gear",
        "description": "Книга со знаниями по определённой теме: история, наука, религия и пр.",
        "weight": 5.0, "cost_gp": 25.0,
    },
    {
        "slug": "ink-1-ounce",
        "name": "Чернила (1 унция)", "name_en": "Ink (1 ounce bottle)",
        "category": "gear",
        "description": "Флакон чернил для письма.",
        "weight": 0.0, "cost_gp": 10.0,
    },
    {
        "slug": "parchment-1-sheet",
        "name": "Пергамент (1 лист)", "name_en": "Parchment (1 sheet)",
        "category": "gear",
        "description": "Один лист пергамента для письма.",
        "weight": 0.0, "cost_gp": 0.1,
    },
]


def seed_generic_items(db):
    count = 0
    for data in ITEMS:
        existing = db.query(Item).filter(Item.slug == data["slug"]).first()
        if existing:
            continue
        item = Item(**data)
        db.add(item)
        count += 1
    db.commit()
    print(f"  Добавлено предметов: {count}")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_generic_items(db)
    finally:
        db.close()
