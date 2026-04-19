import json
import logging
from uuid import UUID
from ..models.token import Token
from ..redis_client import redis_client

logger = logging.getLogger(__name__)


def save_game_state_to_redis(game_id: UUID, tokens: list[Token]) -> None:
    """Сохранение состояния игры в Redis"""
    tokens_key = f"game:{game_id}:tokens"
    redis_client.delete(tokens_key)

    for token in tokens:
        token_data = {
            "id": str(token.id),
            "name": token.name,
            "x": token.x,
            "y": token.y,
            "image_url": token.image_url or ""
        }
        redis_client.hset(tokens_key, str(token.id), json.dumps(token_data))

    redis_client.expire(tokens_key, 86400)


def load_game_state_from_redis(game_id: UUID) -> list[dict] | None:
    """Загрузка состояния игры из Redis"""
    tokens_key = f"game:{game_id}:tokens"
    tokens_data = redis_client.hgetall(tokens_key)

    if not tokens_data:
        return None

    tokens = []
    for token_json in tokens_data.values():
        tokens.append(json.loads(token_json))

    return tokens
