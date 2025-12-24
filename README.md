# D&D Virtual Table - Прототип

Браузерное приложение для игры в Dungeons & Dragons онлайн. Прототип с базовой функциональностью: регистрация/логин, создание лобби, карта с токенами персонажей и синхронизация в реальном времени.

## Технологический стек

**Backend:**
- Python 3.11+
- FastAPI
- SQLAlchemy (PostgreSQL)
- Redis
- Socket.IO (python-socketio)

**Frontend:**
- React 19 + TypeScript
- Vite
- Tailwind CSS
- Socket.IO Client

**Базы данных:**
- PostgreSQL (основные данные)
- Redis (real-time состояние)

## Быстрый старт

### Предварительные требования

- Python 3.11+
- Node.js 18+
- Docker и Docker Compose

### Установка и запуск

1. **Клонируйте репозиторий и перейдите в папку проекта:**
```bash
cd C:\Projeck\Dungeons_dragons
```

2. **Запустите PostgreSQL и Redis:**
```bash
docker-compose up -d
```

3. **Настройте Backend:**
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Отредактируйте .env при необходимости
```

4. **Примените миграции БД:**
```bash
alembic upgrade head
```

5. **Запустите Backend:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. **Настройте Frontend:**
```bash
cd ../frontend
npm install
cp .env.example .env
# Отредактируйте .env при необходимости
```

7. **Запустите Frontend:**
```bash
npm run dev
```

8. **Откройте браузер:**
```
http://localhost:5173
```

## Структура проекта

```
dnd-prototype/
├── backend/          # Python FastAPI приложение
├── frontend/         # React приложение
├── docker-compose.yml
└── README.md
```

## API Endpoints

### Аутентификация
- `POST /api/auth/register` - регистрация
- `POST /api/auth/login` - вход
- `GET /api/auth/me` - текущий пользователь

### Игры
- `POST /api/games` - создать лобби
- `GET /api/games/{invite_code}` - информация о лобби
- `POST /api/games/{game_id}/join` - присоединиться
- `GET /api/games/{game_id}` - детали игры

### Карты
- `POST /api/maps/upload` - загрузить карту

## WebSocket события

**Клиент → Сервер:**
- `game:join` - подключиться к игре
- `token:move` - переместить токен
- `token:create` - создать токен (только мастер)
- `token:delete` - удалить токен (только мастер)

**Сервер → Клиент:**
- `game:state` - полное состояние игры
- `token:moved` - токен перемещен
- `token:created` - токен создан
- `token:deleted` - токен удален
- `player:joined` - игрок подключился
- `player:left` - игрок отключился

## Разработка

### Backend

```bash
cd backend
# Активируйте виртуальное окружение
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate      # Windows

# Создать новую миграцию
alembic revision --autogenerate -m "описание"

# Применить миграции
alembic upgrade head

# Запустить сервер
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Переменные окружения

### Backend (.env)
```env
DATABASE_URL=postgresql://dnd_user:dnd_password@localhost:5432/dnd_db
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## Документация

- [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md) - **детальный план реализации (что сделано, что нужно сделать, тесты)**
- [SETUP.md](./SETUP.md) - инструкция по установке и запуску
- [MICROSERVICES_REFERENCE.md](./MICROSERVICES_REFERENCE.md) - описание микросервисов из Example/

## Лицензия

Проект создан для образовательных целей.

