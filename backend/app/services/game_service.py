import string
import random
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from uuid import UUID
from ..models.game_session import GameSession
from ..models.game_participant import GameParticipant
from ..models.token import Token
from ..schemas.game import GameCreate
from ..schemas.token import TokenCreate, TokenUpdate


def generate_invite_code(length: int = 6) -> str:
    """Генерация уникального invite-кода"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def create_game(db: Session, game_data: GameCreate, master_id: UUID) -> GameSession:
    """Создание новой игровой сессии"""
    # Генерируем уникальный invite-код
    invite_code = generate_invite_code()
    while db.query(GameSession).filter(GameSession.invite_code == invite_code).first():
        invite_code = generate_invite_code()
    
    # Создаем игру
    game = GameSession(
        name=game_data.name,
        invite_code=invite_code,
        master_id=master_id
    )
    db.add(game)
    db.flush()
    
    # Добавляем мастера как участника
    participant = GameParticipant(
        game_id=game.id,
        user_id=master_id,
        role="master"
    )
    db.add(participant)
    db.commit()
    db.refresh(game)
    return game


def get_game_by_invite_code(db: Session, invite_code: str) -> GameSession:
    """Получение игры по invite-коду"""
    game = db.query(GameSession).filter(GameSession.invite_code == invite_code).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    return game


def get_game_by_id(db: Session, game_id: UUID) -> GameSession:
    """Получение игры по ID"""
    game = db.query(GameSession).filter(GameSession.id == game_id).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    return game


def join_game(db: Session, game_id: UUID, user_id: UUID) -> GameSession:
    """Присоединение к игре"""
    game = get_game_by_id(db, game_id)
    
    # Проверяем, не является ли пользователь уже участником
    existing = db.query(GameParticipant).filter(
        GameParticipant.game_id == game_id,
        GameParticipant.user_id == user_id
    ).first()
    
    if existing:
        return game
    
    # Добавляем как игрока
    participant = GameParticipant(
        game_id=game_id,
        user_id=user_id,
        role="player"
    )
    db.add(participant)
    db.commit()
    db.refresh(game)
    return game


def is_master(db: Session, game_id: UUID, user_id: UUID) -> bool:
    """Проверка, является ли пользователь мастером игры"""
    participant = db.query(GameParticipant).filter(
        GameParticipant.game_id == game_id,
        GameParticipant.user_id == user_id,
        GameParticipant.role == "master"
    ).first()
    return participant is not None


def create_token(db: Session, game_id: UUID, token_data: TokenCreate) -> Token:
    """Создание токена на карте"""
    token = Token(
        game_id=game_id,
        name=token_data.name,
        x=token_data.x,
        y=token_data.y,
        image_url=token_data.image_url
    )
    db.add(token)
    db.commit()
    db.refresh(token)
    return token


def update_token_position(db: Session, token_id: UUID, token_data: TokenUpdate) -> Token:
    """Обновление позиции токена"""
    token = db.query(Token).filter(Token.id == token_id).first()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    
    token.x = token_data.x
    token.y = token_data.y
    db.commit()
    db.refresh(token)
    return token


def delete_token(db: Session, token_id: UUID) -> None:
    """Удаление токена"""
    token = db.query(Token).filter(Token.id == token_id).first()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    db.delete(token)
    db.commit()


def get_game_tokens(db: Session, game_id: UUID) -> list[Token]:
    """Получение всех токенов игры"""
    return db.query(Token).filter(Token.game_id == game_id).all()

