# Базы данных

## PostgreSQL

Основное хранилище данных.

### Подключение

```env
DATABASE_URL=postgresql://dnd_user:dnd_password@localhost:5432/dnd_db
```

### Миграции

Alembic управляет миграциями:

```bash
# Создать миграцию
alembic revision --autogenerate -m "описание"

# Применить миграции
alembic upgrade head

# Откатить
alembic downgrade -1
```

---

## Redis

Кеширование и real-time состояние.

### Подключение

```env
REDIS_URL=redis://localhost:6379
```

### Использование

- **Token кеш** — токены карты с TTL 24ч: `game:{game_id}:tokens`
- **Game rooms** — активные комнаты
- **Connected users** — подключённые пользователи

---

## Модели

### Основные сущности

| Модель | Описание |
|--------|----------|
| `User` | Пользователь (id, email, username, hashed_password) |
| `Game` | Игра (id, name, invite_code, master_id, map_url) |
| `GameParticipant` | Участник игры (user_id, game_id, role) |
| `Token` | Токен на карте (game_id, character_id, x, y, status) |
| `Character` | Персонаж (name, race, class, stats, owner_id) |
| `CombatSession` | Сессия боя (game_id, is_active, round, current_turn) |
| `CombatParticipant` | Участник боя (combat_id, token_id, initiative, hp) |
| `DiceRollHistory` | История бросков (game_id, user_id, dice_string, result) |

### Справочные данные

| Модель | Описание |
|--------|----------|
| `Race` | Расы (name, speed, abilities) |
| `Class` | Классы (name, hit_dice, saving_throws) |
| `Background` | Предыстории |
| `Spell` | Заклинания |
| `Item` | Предметы |
| `Monster` | Монстры |

Seed данные загружаются из `backend/data/`.

---

## Схема данных

```
User
├── id
├── email
├── username
└── hashed_password

Game
├── id
├── name
├── invite_code (unique)
├── master_id -> User
└── map_url

GameParticipant
├── user_id -> User
├── game_id -> Game
└── role (master/player)

Token
├── id
├── game_id -> Game
├── character_id -> Character (nullable)
├── name
├── x, y (позиция)
├── size (клетки)
└── status (active/dead)

Character
├── id
├── name
├── race -> Race
├── class -> Class
├── level
├── hp (текущее/макс)
├── stats (STR, DEX, CON, INT, WIS, CHA)
├── owner_id -> User
└── game_id -> Game

CombatSession
├── id
├── game_id -> Game
├── is_active
├── round
└── current_turn_token_id

CombatParticipant
├── id
├── combat_id -> CombatSession
├── token_id -> Token
├── initiative
├── hp
└── is_current_turn

DiceRollHistory
├── id
├── game_id -> Game
├── user_id -> User
├── character_name
├── dice_string ( напр. "2d6+3")
├── result
└── created_at
```

---

## Следующие шаги

- [HTTP эндпоинты](../api/http-endpoints.md)
- [WebSocket события](../api/websocket.md)