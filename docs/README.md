# D&D Virtual Table — Документация

Виртуальный стол для игры в Dungeons & Dragons онлайн.

## Навигация по разделам

### Быстрый старт

| Раздел | Описание |
|--------|----------|
| [Установка](getting-started/installation.md) | Требования, Docker, Python, Node.js |
| [Запуск](getting-started/quick-start.md) | Запуск dev-серверов |
| [Первая игра](getting-started/first-game.md) | Регистрация, создание и присоединение к игре |

### Архитектура

| Раздел | Описание |
|--------|----------|
| [Обзор архитектуры](architecture/overview.md) | Технологический стек, общая схема |
| [Backend](architecture/backend.md) | FastAPI, Socket.IO, сервисы |
| [Frontend](architecture/frontend.md) | React, Zustand, компоненты |
| [Базы данных](architecture/database.md) | PostgreSQL, Redis, модели |

### API Reference

| Раздел | Описание |
|--------|----------|
| [HTTP эндпоинты](api/http-endpoints.md) | REST API (auth, games, maps, dice, combat) |
| [WebSocket](api/websocket.md) | События real-time синхронизации |

### Игровые функции

| Раздел | Описание |
|--------|----------|
| [Токены](game-features/tokens.md) | Токены на карте, роли master/player |
| [Кубики](game-features/dice.md) | Бросание d20, dnd-нотация, история |
| [Бой](game-features/combat.md) | Система боя, инициатива, раунды |
| [Персонажи](game-features/characters.md) | Создание, атрибуты, инвентарь |
| [Карты](game-features/maps.md) | Загрузка, zoom, pan |

### Развертывание

| Раздел | Описание |
|--------|----------|
| [Production](deployment/production.md) | Деплой на сервер |

### Решение проблем

| Раздел | Описание |
|--------|----------|
| [Частые ошибки](troubleshooting/common-issues.md) | Ошибки подключения, порты, БД |

---

## Ссылки

- **Frontend:** http://localhost:5173
- **Backend:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **D&D 5e Rules:** https://dnd.su