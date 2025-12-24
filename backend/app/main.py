from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import socketio as sio_lib
import os
from .config import settings
from .database import engine, Base
from .api import auth, games, maps, dice, characters
from .sockets.game_events import register_socket_handlers

# Создаем таблицы (в продакшене используйте миграции)
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="D&D Virtual Table API", version="1.0.0")

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

# Статические файлы для карт
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

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


@app.get("/")
async def root():
    return {"message": "D&D Virtual Table API"}


@app.get("/health")
async def health():
    return {"status": "ok"}


# Экспортируем socket_app для запуска через uvicorn
app = socket_app

