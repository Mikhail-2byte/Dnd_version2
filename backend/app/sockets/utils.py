import logging
from uuid import UUID
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models.user import User
from ..models.game_participant import GameParticipant
from ..services.game_service import get_game_by_id, get_game_tokens
from ..utils.jwt import decode_access_token

logger = logging.getLogger(__name__)


def get_user_from_token(token: str) -> UUID | None:
    """Получение user_id из JWT токена"""
    payload = decode_access_token(token)
    if payload:
        return UUID(payload.get("sub"))
    return None


def get_user_from_db(user_id: UUID) -> User | None:
    """Получение пользователя из БД"""
    db = SessionLocal()
    try:
        return db.query(User).filter(User.id == user_id).first()
    finally:
        db.close()


def get_game_state(db: Session, game_id: UUID) -> dict:
    """Получение полного состояния игры"""
    game = get_game_by_id(db, game_id)
    tokens = get_game_tokens(db, game_id)
    participants = db.query(GameParticipant).filter(
        GameParticipant.game_id == game_id
    ).all()

    players = []
    for participant in participants:
        user = db.query(User).filter(User.id == participant.user_id).first()
        if user:
            players.append({
                "user_id": str(user.id),
                "username": user.username,
                "role": participant.role,
                "is_ready": participant.is_ready,
                "character_id": str(participant.character_id) if participant.character_id else None
            })

    return {
        "game": {
            "id": str(game.id),
            "name": game.name,
            "invite_code": game.invite_code,
            "map_url": game.map_url
        },
        "tokens": [
            {
                "id": str(token.id),
                "name": token.name,
                "x": token.x,
                "y": token.y,
                "image_url": token.image_url
            }
            for token in tokens
        ],
        "players": players
    }
