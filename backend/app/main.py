from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import socketio as sio_lib
import os
import logging
from .config import settings
from .database import engine, Base, check_db_connection
from .api import auth, games, maps, dice, characters, combat, game_data
from .sockets.game_events import register_socket_handlers

logger = logging.getLogger(__name__)

# Создаем таблицы (в продакшене используйте миграции)
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="D&D Virtual Table API", version="1.0.0")


@app.on_event("startup")
async def startup_event():
    """Проверка подключения к базе данных при старте приложения"""
    logger.info("Checking database connection...")
    if not check_db_connection():
        logger.error(
            "⚠️  ВНИМАНИЕ: Не удалось подключиться к базе данных PostgreSQL!\n"
            "Убедитесь, что:\n"
            "1. Docker Desktop запущен\n"
            "2. Контейнеры запущены: docker-compose up -d\n"
            "3. Проверьте статус: docker-compose ps\n"
            "4. Проверьте DATABASE_URL в файле .env"
        )
    else:
        logger.info("✅ Подключение к базе данных успешно установлено")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite и другие порты
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создаем директории для загрузок
os.makedirs(settings.maps_dir, exist_ok=True)
os.makedirs(settings.upload_dir, exist_ok=True)

# Статические файлы для карт
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

# Socket.IO
sio = sio_lib.AsyncServer(
    cors_allowed_origins=["http://localhost:5173", "http://localhost:3000"],
    async_mode="asgi"
)
socket_app = sio_lib.ASGIApp(sio, app)

# Регистрируем обработчики Socket.IO
register_socket_handlers(sio)

# Подключаем роутеры
app.include_router(auth.router)
app.include_router(games.router)
app.include_router(maps.router)
app.include_router(dice.router)
app.include_router(characters.router)
app.include_router(combat.router)
app.include_router(game_data.router)


@app.get("/")
async def root():
    return {"message": "D&D Virtual Table API"}


@app.get("/health")
async def health():
    return {"status": "ok"}


# Экспортируем socket_app для запуска через uvicorn
# Socket.IO требует обертку ASGIApp для интеграции с FastAPI
# Поэтому экспортируем socket_app вместо app, чтобы uvicorn запускал оба сервера (HTTP и WebSocket)
app = socket_app

