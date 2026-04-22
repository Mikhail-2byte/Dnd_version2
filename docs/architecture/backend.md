# Backend

## Точка входа

`backend/app/main.py` — основной файл приложения.

```python
app = FastAPI(...)
socket_app = sio_lib.ASGIApp(sio, app)
```

FastAPI оборачивается в `socketio.ASGIApp` для WebSocket поддержки.

**Запуск:** `uvicorn app.main:socket_app --reload`

---

## Слои приложения

### API Routers

| Файл | Описание |
|------|----------|
| `api/auth.py` | Регистрация, вход, текущий пользователь |
| `api/games.py` | Создание игры, присоединение, invite-коды |
| `api/maps.py` | Загрузка карт |
| `api/dice.py` | Бросание кубиков |
| `api/characters.py` | Управление персонажами |
| `api/combat.py` | Система боя |
| `api/game_data.py` | Справочные данные (расы, классы, заклинания) |

### Services

| Файл | Описание |
|------|----------|
| `services/auth_service.py` | Аутентификация, JWT токены |
| `services/game_service.py` | Логика игровых комнат |
| `services/dice_service.py` | Бросание кубиков, dnd-нотация |
| `services/combat_service.py` | Инициатива, раунды, HP |
| `services/character_service.py` | Персонажи, атрибуты |
| `services/game_data_service.py` | Справочные данные |

### Models

SQLAlchemy ORM модели в `models/`:
- `User` — пользователи
- `Game` — игры
- `GameParticipant` — участники игры
- `Token` — токены на карте
- `Character` — персонажи
- `CombatSession` — сессии боя
- `CombatParticipant` — участники боя
- `DiceRollHistory` — история бросков

### Schemas

Pydantic схемы для валидации в `schemas/`:
- `UserCreate`, `UserResponse`
- `GameCreate`, `GameResponse`
- `TokenCreate`, `TokenUpdate`
- `DiceRollRequest`, `DiceRollResponse`

---

## Socket.IO

### Регистрация обработчиков

`app/sockets/game_events.py` — фасад, регистрирует все обработчики:

```python
def register_socket_handlers(sio):
    from .handlers import connection, token, dice, participant
    sio.on("game:join", handler=connection.join_game)
    sio.on("token:move", handler=token.move_token)
    # ...
```

### Состояние

`app/sockets/state.py` — глобальное состояние:

```python
connected_users = {}      # sid -> {user_id, username}
game_rooms = {}          # game_id -> {participants, tokens}
_sio_instance = None     # Reference to Socket.IO server
```

### Emitters

`app/sockets/emitters.py` — функции для broadcast из HTTP:

```python
async def emit_token_moved(game_id, token_id, x, y):
    await sio.emit("token:moved", {...}, room=f"game:{game_id}")
```

### Handlers

Обработчики событий в `sockets/handlers/`:
- `connection/` — подключение, отключение, game:join
- `token/` — move, create, delete
- `dice/` — roll
- `participant/` — присоединение к бою

---

## Аутентификация

### HTTP

`middleware/auth.py` — `get_current_user`:

```python
def get_current_user(credentials = Depends(HTTPBearer)):
    token = credentials.credentials
    payload = jwt.decode(token, SECRET_KEY)
    user = db.query(User).get(payload["sub"])
    return user
```

### WebSocket

Аутентификация через токен в payload при connect:

```python
@sio.on("connect")
async def connect(sid, environ):
    token = environ.get("auth", {}).get("token")
    # Проверка токена и установка user в session
```

---

## Роли

| Роль | Права |
|------|-------|
| `master` | Создание/удаление/перемещение любых токенов, управление боем |
| `player` | Перемещение только своих токенов, бросание кубиков |

Роль определяется при создании/присоединении к игре.

---

## Конфигурация

`app/config.py` — настройки из переменных окружения:

```python
class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str
    # ...
```

---

## Следующие шаги

- [Frontend](frontend.md) — клиентская часть
- [Базы данных](database.md) — модели и схема

---

## Ссылки

- [HTTP эндпоинты](../api/http-endpoints.md)
- [WebSocket события](../api/websocket.md)