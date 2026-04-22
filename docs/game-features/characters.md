# Персонажи

Персонажи — это игровые персонажи (PC) и неигровые персонажи (NPC).

---

## Создание персонажа

### Через UI

1. Перейдите в "Мои персонажи"
2. Нажмите "Создать персонажа"
3. Заполните данные:
   - Имя
   - Раса
   - Класс
   - Предыстория
   - Статы (генерируются автоматически или вручную)

### Через HTTP

```bash
curl -X POST http://localhost:8000/api/characters \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Aragorn",
    "race_id": 1,
    "class_id": 2,
    "level": 5,
    "game_id": 1
  }'
```

---

## Атрибуты

### Базовая статистика (D&D 5e)

| Атрибут | Сокращение |
|---------|------------|
| Strength | STR |
| Dexterity | DEX |
| Constitution | CON |
| Intelligence | INT |
| Wisdom | WIS |
| Charisma | CHA |

### Модификаторы

Модификатор вычисляется по формуле:

```
модификатор = floor((значение - 10) / 2)
```

| Значение | Модификатор |
|----------|-------------|
| 8 | -1 |
| 10 | +0 |
| 12 | +1 |
| 14 | +2 |
| 16 | +3 |

---

## Данные персонажа

```json
{
  "id": 1,
  "name": "Aragorn",
  "race": "Human",
  "class": "Ranger",
  "level": 5,
  "hp": {
    "current": 42,
    "max": 45
  },
  "stats": {
    "str": 13,
    "dex": 14,
    "con": 12,
    "int": 10,
    "wis": 13,
    "cha": 11
  },
  "speed": 30,
  "armor_class": 15,
  "proficiency_bonus": 3,
  "saving_throws": ["dex", "wis"],
  "skills": ["athletics", "survival", "perception"],
  "equipment": ["Longsword", "Longbow", "Leather armor"],
  "features": ["Ranger Favored Enemy", "Natural Explorer"],
  "spells": ["Hunter's Mark", "Cure Wounds"]
}
```

---

## Справочные данные

### Расы

```bash
GET http://localhost:8000/api/game-data/races
```

Доступны: Human, Elf, Dwarf, Halfling, Dragonborn, Gnome, Half-Elf, Half-Orc, Tiefling

### Классы

```bash
GET http://localhost:8000/api/game-data/classes
```

Доступны: Fighter, Wizard, Rogue, Cleric, Ranger, Paladin, Barbarian, Bard, Druid, Monk, Sorcerer, Warlock

### Предыстории

```bash
GET http://localhost:8000/api/game-data/backgrounds
```

### Заклинания

```bash
GET http://localhost:8000/api/game-data/spells
```

---

## Персонажи и токены

Персонаж привязывается к токену на карте:

1. Создайте персонажа
2. Перетащите персонажа на карту
3. Создастся токен с данными персонажа

Изменения HP персонажа отображаются на токене.

---

## События

### Сервер → Клиент

При изменении персонажа все игроки получают обновление через game state.

---

## Смотрите также

- [Токены](tokens.md) — токены на карте
- [Бой](combat.md) — боевая система