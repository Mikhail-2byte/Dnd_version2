import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Добавляем путь к app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import Base, get_db
# Импортируем FastAPI app до обертки в socket_app
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, games, maps, dice, characters
import os

# Устанавливаем тестовые переменные окружения перед импортом настроек
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379")

# Создаем тестовый FastAPI app без Socket.IO
test_app = FastAPI(title="D&D Virtual Table API Test", version="1.0.0")
test_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
test_app.include_router(auth.router)
test_app.include_router(games.router)
test_app.include_router(maps.router)
test_app.include_router(dice.router)
test_app.include_router(characters.router)
from app.models import User, GameSession, GameParticipant, Token, Character
from app.utils.security import get_password_hash
from app.utils.jwt import create_access_token
from datetime import timedelta
from app.config import settings
import uuid


# Тестовая БД (SQLite в памяти)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """Создает тестовую БД для каждого теста"""
    # Создаем все таблицы
    Base.metadata.create_all(bind=test_engine)
    
    # Создаем сессию
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        # Удаляем все таблицы после теста
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Создает тестовый клиент FastAPI"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    test_app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(test_app) as test_client:
        yield test_client
    
    test_app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def mock_redis():
    """Мок для Redis"""
    with patch('app.redis_client.redis_client') as mock_redis:
        # Настраиваем мок Redis как словарь
        mock_redis_data = {}
        
        def mock_get(key):
            return mock_redis_data.get(key)
        
        def mock_set(key, value, ex=None):
            mock_redis_data[key] = value
            return True
        
        def mock_delete(key):
            if key in mock_redis_data:
                del mock_redis_data[key]
                return 1
            return 0
        
        def mock_hget(hash_key, field):
            if hash_key in mock_redis_data:
                if isinstance(mock_redis_data[hash_key], dict):
                    return mock_redis_data[hash_key].get(field)
            return None
        
        def mock_hset(hash_key, field, value):
            if hash_key not in mock_redis_data:
                mock_redis_data[hash_key] = {}
            mock_redis_data[hash_key][field] = value
            return 1
        
        def mock_hgetall(hash_key):
            if hash_key in mock_redis_data:
                if isinstance(mock_redis_data[hash_key], dict):
                    return mock_redis_data[hash_key]
            return {}
        
        def mock_hdel(hash_key, *fields):
            if hash_key in mock_redis_data and isinstance(mock_redis_data[hash_key], dict):
                deleted = 0
                for field in fields:
                    if field in mock_redis_data[hash_key]:
                        del mock_redis_data[hash_key][field]
                        deleted += 1
                return deleted
            return 0
        
        def mock_keys(pattern):
            import re
            pattern_re = pattern.replace('*', '.*')
            return [key for key in mock_redis_data.keys() if re.match(pattern_re, key)]
        
        mock_redis.get = Mock(side_effect=mock_get)
        mock_redis.set = Mock(side_effect=mock_set)
        mock_redis.delete = Mock(side_effect=mock_delete)
        mock_redis.hget = Mock(side_effect=mock_hget)
        mock_redis.hset = Mock(side_effect=mock_hset)
        mock_redis.hgetall = Mock(side_effect=mock_hgetall)
        mock_redis.hdel = Mock(side_effect=mock_hdel)
        mock_redis.keys = Mock(side_effect=mock_keys)
        
        yield mock_redis


@pytest.fixture
def test_user(db_session):
    """Создает тестового пользователя"""
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        username="testuser",
        password_hash=get_password_hash("testpassword123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user_token(test_user):
    """Создает JWT токен для тестового пользователя"""
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    token = create_access_token(
        data={"sub": str(test_user.id), "email": test_user.email},
        expires_delta=access_token_expires
    )
    return token


@pytest.fixture
def authenticated_client(client, test_user_token):
    """Клиент с аутентификацией"""
    client.headers.update({"Authorization": f"Bearer {test_user_token}"})
    return client


@pytest.fixture
def test_game(db_session, test_user):
    """Создает тестовую игру"""
    game = GameSession(
        id=uuid.uuid4(),
        name="Test Game",
        invite_code="TEST01",
        master_id=test_user.id
    )
    db_session.add(game)
    
    # Добавляем мастера как участника
    participant = GameParticipant(
        game_id=game.id,
        user_id=test_user.id,
        role="master"
    )
    db_session.add(participant)
    
    db_session.commit()
    db_session.refresh(game)
    return game


@pytest.fixture
def test_token(db_session, test_game):
    """Создает тестовый токен"""
    token = Token(
        id=uuid.uuid4(),
        game_id=test_game.id,
        name="Test Token",
        x=50.0,
        y=50.0
    )
    db_session.add(token)
    db_session.commit()
    db_session.refresh(token)
    return token


@pytest.fixture
def test_user2(db_session):
    """Создает второго тестового пользователя"""
    user = User(
        id=uuid.uuid4(),
        email="test2@example.com",
        username="testuser2",
        password_hash=get_password_hash("testpassword123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user2_token(test_user2):
    """Создает JWT токен для второго тестового пользователя"""
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    token = create_access_token(
        data={"sub": str(test_user2.id), "email": test_user2.email},
        expires_delta=access_token_expires
    )
    return token


@pytest.fixture
def auth_headers(test_user_token):
    """Заголовки с токеном для аутентификации"""
    return {"Authorization": f"Bearer {test_user_token}"}


@pytest.fixture
def test_user_id(test_user):
    """ID тестового пользователя"""
    return test_user.id

