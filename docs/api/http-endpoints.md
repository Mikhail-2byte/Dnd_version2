# HTTP эндпоинты

## Аутентификация

### Регистрация

```
POST /api/auth/register
```

**Request:**
```json
{
  "email": "user@example.com",
  "username": "player1",
  "password": "secret123"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "player1"
}
```

### Вход

```
POST /api/auth/login
```

**Request:**
```json
{
  "email": "user@example.com",
  "password": "secret123"
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### Текущий пользователь

```
GET /api/auth/me
```

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "player1"
}
```

---

## Игры

### Создание игры

```
POST /api/games
```

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "name": "Dragon's Lair"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Dragon's Lair",
  "invite_code": "ABC123",
  "master_id": 1,
  "map_url": null
}
```

### Информация об игре по invite-коду

```
GET /api/games/{invite_code}
```

**Response:**
```json
{
  "id": 1,
  "name": "Dragon's Lair",
  "invite_code": "ABC123",
  "master_id": 1,
  "master_username": "master",
  "map_url": null,
  "participants": [
    {"user_id": 1, "username": "master", "role": "master"}
  ]
}
```

### Присоединение к игре

```
POST /api/games/{game_id}/join
```

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "game_id": 1,
  "role": "player"
}
```

### Детали игры

```
GET /api/games/{game_id}
```

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": 1,
  "name": "Dragon's Lair",
  "invite_code": "ABC123",
  "master_id": 1,
  "map_url": "/uploads/maps/map.jpg",
  "participants": [...],
  "tokens": [...]
}
```

---

## Карты

### Загрузка карты

```
POST /api/maps/upload
```

**Headers:** `Authorization: Bearer <token>`

**Body:** multipart/form-data

**Response:**
```json
{
  "url": "/uploads/maps/uuid.jpg"
}
```

---

## Кубики

### Бросание кубика

```
POST /api/dice/roll
```

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "dice": "2d6+3",
  "character_name": "Grog",
  "game_id": 1
}
```

**Response:**
```json
{
  "dice": "2d6+3",
  "result": [4, 6],
  "total": 13,
  "character_name": "Grog"
}
```

### История бросков

```
GET /api/dice/history/{game_id}
```

**Response:**
```json
[
  {
    "id": 1,
    "dice_string": "2d6+3",
    "result": [4, 6],
    "total": 13,
    "character_name": "Grog",
    "username": "master",
    "created_at": "2024-01-01T12:00:00"
  }
]
```

---

## Персонажи

### Создание персонажа

```
POST /api/characters
```

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "name": "Grog",
  "race_id": 1,
  "class_id": 1,
  "level": 1,
  "game_id": 1
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Grog",
  "race": "Orc",
  "class": "Barbarian",
  "level": 1,
  "hp": 12,
  "stats": {
    "str": 16,
    "dex": 10,
    "con": 14,
    "int": 8,
    "wis": 10,
    "cha": 8
  }
}
```

### Список персонажей пользователя

```
GET /api/characters
```

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
[
  {
    "id": 1,
    "name": "Grog",
    "race": "Orc",
    "class": "Barbarian",
    "level": 1
  }
]
```

---

## Бой

### Начало боя

```
POST /api/combat/{game_id}/start
```

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "participant_ids": [1, 2, 3]
}
```

**Response:**
```json
{
  "id": 1,
  "game_id": 1,
  "is_active": true,
  "round": 1,
  "participants": [
    {"token_id": 1, "initiative": 15, "hp": 30},
    {"token_id": 2, "initiative": 12, "hp": 20}
  ]
}
```

### Следующий ход

```
POST /api/combat/{combat_id}/next
```

**Response:**
```json
{
  "current_turn_token_id": 2,
  "round": 1
}
```

### Завершение боя

```
POST /api/combat/{combat_id}/end
```

---

## Game Data

### Справочные данные

```
GET /api/game-data/races
GET /api/game-data/classes
GET /api/game-data/backgrounds
GET /api/game-data/spells
GET /api/game-data/items
GET /api/game-data/monsters
```

---

## Swagger

Полная документация доступна по адресу: http://localhost:8000/docs