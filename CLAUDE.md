# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## D&D Rules Reference

**Основной источник правил D&D 5e:** https://dnd.su

Если нужна информация о механиках, классах, способностях, заклинаниях, снаряжении или любых игровых правилах — брать с этого сайта. Примеры страниц:
- Класс: `https://dnd.su/class/87-barbarian/`
- Способность класса: `https://dnd.su/class/87-barbarian/#feature.rage`
- Заклинания: `https://dnd.su/spells/`
- Расы: `https://dnd.su/races/`

Использовать WebFetch для получения актуальных данных перед реализацией любой игровой механики.

## Project Overview

D&D Virtual Table — браузерное приложение для игры в Dungeons & Dragons онлайн. Монорепозиторий с Python/FastAPI бэкендом и React/TypeScript фронтендом.

## Commands

### Infrastructure

```bash
# Запуск PostgreSQL + Redis (обязательно перед бэкендом)
docker-compose up -d

# Остановка
docker-compose down
```

### Backend

```bash
cd backend

# Активировать venv (Windows)
venv\Scripts\activate

# Запуск сервера (dev)
uvicorn app.main:socket_app --reload
# или
python run.py

# Миграции БД
alembic upgrade head
alembic revision --autogenerate -m "описание"

# Все тесты
python -m pytest

# Один тест / один файл
python -m pytest tests/test_auth.py
python -m pytest tests/test_auth.py::TestAuth::test_register -v

# С покрытием
python -m pytest --cov=app --cov-report=html
```

### Frontend

```bash
cd frontend

npm install
npm run dev        # Vite dev server → http://localhost:5173
npm run build      # TypeScript check + production build
npx tsc --noEmit   # Только проверка типов
```

## Architecture

### Backend

**Точка входа:** `backend/app/main.py` — FastAPI приложение оборачивается в `socketio.ASGIApp`. Uvicorn должен запускаться с `app.main:socket_app` (не `app`), иначе WebSocket не работает.

**Слои:**
- `api/` — HTTP роутеры FastAPI (auth, games, maps, dice, characters, combat)
- `services/` — бизнес-логика (game_service, character_service, combat_service, dice_service, auth_service)
- `models/` — SQLAlchemy ORM модели
- `schemas/` — Pydantic схемы для валидации запросов/ответов
- `sockets/` — Socket.IO обработчики:
  - `game_events.py` — фасад, регистрирует все обработчики
  - `state.py` — глобальное состояние (`connected_users`, `game_rooms`, `_sio_instance`)
  - `emitters.py` — функции `emit_*` для broadcast из HTTP-эндпоинтов (combat.py их вызывает)
  - `handlers/` — обработчики событий по группам (connection, token, dice, participant)
  - `utils.py`, `cache.py` — вспомогательные функции и Redis-кеш

**Аутентификация:** JWT Bearer то��ены. HTTP-эндпоинты используют `get_current_user` из `middleware/auth.py`. Socket.IO аутентифицирует через токен в `auth` payload при connect.

**Базы данных:**
- PostgreSQL (основные да��ные) — чере�� SQLAlchemy ORM + Alembic миграции
- Redis — кеш токенов карты (TTL 24ч), ключ `game:{game_id}:tokens`

**Роли:** `master` / `player`. Только мастер может двигать/создавать/удалять токены на карте.

### Frontend

**Роутинг:** React Router v6, все роуты в `App.tsx`.

**Состояние:**
- `store/gameStore.ts` (Zustand) — текущая игра, токены, игроки, роль пользователя
- `store/authStore.ts` (Zustand) — JWT токен, данные пользователя

**Real-time:** `services/socket.ts` — singleton `SocketService`. Подключается при вхо��е в игровую комнату, все WebSocket события обрабатываются в `pages/GameRoom.tsx`. Состояние синхронизируется в `gameStore` чере�� socket событ��я.

**Страницы:** `pages/GameRoom.tsx` — центральная страница игры, оркестрирует GameMap, CombatPanel, DiceRoller, PlayerList, SceneDescription.

**Компоненты карты:**
- `GameMap.tsx` — главный компонент, zoom/pan через `react-zoom-pan-pinch`
- `TokenWrapper.tsx` — токен с popover-меню (удалить, убить)
- `hooks/useTokenHandlers.ts` — операции с токенами
- `hooks/useMapDragDrop.ts` — drag&drop персонажей на карту

### Тесты (backend)

Тесты используют SQLite in-memory вместо PostgreSQL. `conftest.py` создаёт отдельный FastAPI app без Socket.IO обёртки. Redis мокируется через `mock_redis` fixture.

Есть несколько pre-existing сломанных тестов: `test_combat_system.py::test_start_combat_as_player_forbidden`, `test_dice_templates_api.py`, `test_scene_description.py` — не связаны с основным кодом.

### Переменные окружения

Backend `.env`:
```
DATABASE_URL=postgresql://dnd_user:dnd_password@localhost:5432/dnd_db
REDIS_URL=redis://localhost:6379
SECRET_KEY=<случайная строка>
```

Frontend `.env`:
```
VITE_API_URL=http://localhost:8000
VITE_WS_URL=http://localhost:8000
```
