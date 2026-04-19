from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from sqlalchemy import func
from fastapi import HTTPException, status
import logging
from uuid import UUID
from ..models.user import User
from ..models.character import Character
from ..models.game_session import GameSession
from ..models.game_participant import GameParticipant
from ..schemas.user import UserRegister, UserLogin, UserStatsResponse
from ..utils.security import verify_password, get_password_hash
from ..utils.jwt import create_access_token
from datetime import timedelta
from ..config import settings

logger = logging.getLogger(__name__)


def register_user(db: Session, user_data: UserRegister) -> User:
    """Регистрация нового пользователя"""
    try:
        # Проверка существования email
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Создание пользователя
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            password_hash=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except OperationalError as e:
        logger.error(f"Database connection error during registration: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="База данных недоступна. Убедитесь, что PostgreSQL запущен (docker-compose up -d)"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during registration: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при регистрации пользователя"
        )


def authenticate_user(db: Session, login_data: UserLogin) -> User:
    """Аутентификация пользователя"""
    try:
        user = db.query(User).filter(User.email == login_data.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        if not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        return user
    except OperationalError as e:
        logger.error(f"Database connection error during authentication: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="База данных недоступна. Убедитесь, что PostgreSQL запущен (docker-compose up -d)"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during authentication: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при аутентификации пользователя"
        )


def create_user_token(user: User) -> str:
    """Создание JWT токена для пользователя"""
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires
    )
    return access_token


def get_user_stats(db: Session, user_id: UUID) -> UserStatsResponse:
    """Получение статистики пользователя"""
    try:
        # Количество персонажей
        characters_count = db.query(func.count(Character.id)).filter(
            Character.user_id == user_id
        ).scalar() or 0
        
        # Количество игр, где пользователь мастер
        games_as_master_count = db.query(func.count(GameSession.id)).filter(
            GameSession.master_id == user_id
        ).scalar() or 0
        
        # Количество игр, где пользователь участник (исключая игры, где он мастер, чтобы избежать двойного подсчета)
        games_as_player_count = db.query(func.count(GameParticipant.game_id)).filter(
            GameParticipant.user_id == user_id,
            GameParticipant.role == "player"
        ).scalar() or 0
        
        # Общее количество игр (как мастер + как игрок)
        total_games_count = games_as_master_count + games_as_player_count
        
        return UserStatsResponse(
            characters_count=characters_count,
            games_as_master_count=games_as_master_count,
            games_as_player_count=games_as_player_count,
            total_games_count=total_games_count
        )
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении статистики пользователя"
        )

