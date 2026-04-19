from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from fastapi import HTTPException, status
import logging
from .config import settings

logger = logging.getLogger(__name__)

# Создаем engine с настройками для лучшей обработки ошибок
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Проверка соединения перед использованием
    pool_recycle=3600,   # Переиспользование соединений
    echo=False
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Получение сессии базы данных с обработкой ошибок подключения"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except OperationalError as e:
        db.rollback()
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="База данных недоступна. Убедитесь, что PostgreSQL запущен (docker-compose up -d)"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        # Если это уже HTTPException, пробрасываем его дальше
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при работе с базой данных"
        )
    finally:
        db.close()


def check_db_connection():
    """Проверка подключения к базе данных"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        return True
    except OperationalError as e:
        logger.error(f"Database connection failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during database connection check: {e}")
        return False

