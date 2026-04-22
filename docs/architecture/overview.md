# Обзор архитектуры

## Технологический стек

### Backend
- **Python 3.11+** — основной язык
- **FastAPI** — веб-фреймворк
- **SQLAlchemy** — ORM для PostgreSQL
- **Alembic** — миграции БД
- **python-socketio** — WebSocket real-time
- **Redis** — кеширование и real-time состояние
- **Pydantic** — валидация данных
- **JWT** — аутентификация

### Frontend
- **React 19** — UI-фреймворк
- **TypeScript** — типизация
- **Vite** — сборка и dev-сервер
- **Tailwind CSS** — стилизация
- **Zustand** — управление состоянием
- **React Router v6** — роути��г
- **socket.io-client** — WebSocket клиент

### Базы данных
- **PostgreSQL** — основное хранилище
- **Redis** — кеш и real-time

---

## Общая схема

```
┌─────────────────────────────────────────────────────────────┐
│                      Browser                               │
│  ┌─────────────────────────────────────────────────────┐ │
│  │                 Frontend (React)                      │ │
│  │  - UI компоненты                                    │ │
│  │  - Zustand (состояние)                               │ │
│  │  - Socket.IO Client                                  │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
           HTTP + WebSocket (Socket.IO)
                            │
┌─────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                      │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  API Endpoints                                       │ │
│  │  - Auth (регистрация, вход)                          │ │
│  │  - Games (создание, присоединение)                  │ │
│  │  - Maps (загрузка карт)                              │ │
│  │  - Dice (бросание кубиков)                           │ │
│  │  - Combat (бой)                                      │ │
│  └─────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  Services (бизнес-логика)                            │ │
│  │  - auth_service                                      │ │
│  │  - game_service                                     │ │
│  │  - dice_service                                      │ │
│  │  - combat_service                                   │ │
│  │  - character_service                                │ │
│  └─────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  Socket.IO Handlers                                 │ │
│  │  - token:move, token:create, token:delete          │ │
│  │  - game:join, dice:roll                             │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
           SQLAlchemy + Redis
                            │
┌─────────────────────────────────────────────────────────────┐
│                      Хранилища                            │
│  ┌──────────────────┐    ┌──────────────────────────┐ │
│  │   PostgreSQL     │    │         Redis               │ │
│  │  - Пользователи │    │  - Token кеш (24ч)         │ │
│  │  - Игры          │    │  - Game rooms              │ │
│  │  - Персонажи    │    │  - Connected users         │ │
│  │  - Токены        │    │                            │ │
│  │  - История куби │    │                            │ │
│  └──────────────────┘    └──────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Структура проекта

```
dnd-version2/
├── backend/              # Python FastAPI приложение
│   ├── app/
│   │   ├── api/         # HTTP роутеры
│   │   ├── services/   # Бизнес-логика
│   │   ├── models/     # SQLAlchemy модели
│   │   ├── schemas/   # Pydantic схемы
│   │   ├── sockets/   # Socket.IO обработчики
│   │   ├── middleware/ # Auth middleware
│   │   ├── utils/     # Утилиты
│   │   └── config.py  # Конфигур��ция
│   ├── data/           # Seed данные (расы, классы, заклинания)
│   └── tests/          # Тесты
│
├── frontend/            # React приложение
│   ├── src/
│   │   ├── pages/     # Страницы
│   │   ├── components/ # UI компоненты
│   │   ├── store/    # Zustand стейт
│   │   ├── services/ # API и Socket сервисы
│   │   ├── hooks/    # React хуки
│   │   └── types/   # TypeScript типы
│   └── public/       # Статические файлы
│
├── docs/              # Документация
├── docker-compose.yml # PostgreSQL + Redis
├── SETUP.md          # Инструкция по установке
└── README.md        # Общее описание
```

---

## Слои приложения

### Backend

| Слой | Описание | Примеры |
|------|----------|--------|
| `api/` | HTTP роутеры | `auth.py`, `games.py`, `dice.py` |
| `services/` | Бизнес-логика | `game_service.py`, `dice_service.py` |
| `models/` | ORM модели | `User`, `Game`, `Token` |
| `schemas/` | Валидация | `UserCreate`, `GameResponse` |
| `sockets/` | Real-time | Обработчики событий |

### Frontend

| Слой | Описание | Примеры |
|------|----------|--------|
| `pages/` | Страницы | `GameRoom.tsx`, `Login.tsx` |
| `components/` | UI компоненты | `GameMap.tsx`, `DiceRoller.tsx` |
| `store/` | Состояние | `gameStore.ts`, `authStore.ts` |
| `services/` | API/Socket | `api.ts`, `socket.ts` |
| `hooks/` | Хуки | `useTokenHandlers.ts` |

---

## Следующие шаги

- [Backend](backend.md) — подробнее о серверной части
- [Frontend](frontend.md) — подробнее о клиентской части
- [Базы данных](database.md) — модели и схема

---

## Ссылки

- [HTTP эндпоинты](../api/http-endpoints.md)
- [WebSocket события](../api/websocket.md)