import redis
import logging
from redis.exceptions import ConnectionError, TimeoutError
from .config import settings

logger = logging.getLogger(__name__)

try:
    redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    # Проверка подключения
    redis_client.ping()
    logger.info("✅ Подключение к Redis успешно установлено")
except (ConnectionError, TimeoutError) as e:
    logger.error(f"⚠️  ВНИМАНИЕ: Не удалось подключиться к Redis: {e}")
    logger.error(
        "Убедитесь, что:\n"
        "1. Docker Desktop запущен\n"
        "2. Контейнеры запущены: docker-compose up -d\n"
        "3. Проверьте статус: docker-compose ps\n"
        "4. Проверьте REDIS_URL в файле .env"
    )
    # Создаем клиент в любом случае, но операции могут падать
    redis_client = redis.from_url(settings.redis_url, decode_responses=True)
except Exception as e:
    logger.error(f"Неожиданная ошибка при подключении к Redis: {e}")
    redis_client = redis.from_url(settings.redis_url, decode_responses=True)

