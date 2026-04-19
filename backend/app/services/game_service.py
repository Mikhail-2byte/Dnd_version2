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
        master_id=master_id,
        story=game_data.story,
        map_url=game_data.map_url
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


def is_participant(db: Session, game_id: UUID, user_id: UUID) -> bool:
    """Проверка, является ли пользователь участником игры"""
    participant = db.query(GameParticipant).filter(
        GameParticipant.game_id == game_id,
        GameParticipant.user_id == user_id
    ).first()
    return participant is not None


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


def set_participant_ready(db: Session, game_id: UUID, user_id: UUID, is_ready: bool) -> GameParticipant:
    """Установка статуса готовности участника"""
    participant = db.query(GameParticipant).filter(
        GameParticipant.game_id == game_id,
        GameParticipant.user_id == user_id
    ).first()
    
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found"
        )
    
    participant.is_ready = is_ready
    db.commit()
    db.refresh(participant)
    return participant


def set_participant_character(db: Session, game_id: UUID, user_id: UUID, character_id: UUID | None) -> GameParticipant:
    """Установка выбранного персонажа для участника"""
    participant = db.query(GameParticipant).filter(
        GameParticipant.game_id == game_id,
        GameParticipant.user_id == user_id
    ).first()
    
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found"
        )
    
    participant.character_id = character_id
    db.commit()
    db.refresh(participant)
    return participant


def get_game_participants(db: Session, game_id: UUID) -> list[dict]:
    """Получение списка участников игры с информацией о готовности и выбранном персонаже"""
    from ..models.user import User
    
    participants = db.query(GameParticipant).filter(
        GameParticipant.game_id == game_id
    ).all()
    
    result = []
    for participant in participants:
        user = db.query(User).filter(User.id == participant.user_id).first()
        if user:
            result.append({
                "user_id": str(user.id),
                "username": user.username,
                "role": participant.role,
                "is_ready": participant.is_ready,
                "character_id": str(participant.character_id) if participant.character_id else None
            })
    
    return result


def join_as_spectator(db: Session, game_id: UUID, user_id: UUID) -> GameSession:
    """Присоединение к игре как наблюдатель"""
    game = get_game_by_id(db, game_id)
    
    # Проверяем, не является ли пользователь уже участником
    existing = db.query(GameParticipant).filter(
        GameParticipant.game_id == game_id,
        GameParticipant.user_id == user_id
    ).first()
    
    if existing:
        # Если уже участник, просто возвращаем игру
        return game
    
    # Добавляем как наблюдателя
    participant = GameParticipant(
        game_id=game_id,
        user_id=user_id,
        role="spectator"
    )
    db.add(participant)
    db.commit()
    db.refresh(game)
    return game


def transfer_master_role(db: Session, game_id: UUID, from_user_id: UUID, to_user_id: UUID) -> GameSession:
    """Передача роли мастера другому игроку"""
    # Проверяем, что игра существует
    game = get_game_by_id(db, game_id)
    
    # Проверяем, что текущий пользователь является мастером
    from_participant = db.query(GameParticipant).filter(
        GameParticipant.game_id == game_id,
        GameParticipant.user_id == from_user_id,
        GameParticipant.role == "master"
    ).first()
    
    if not from_participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only current master can transfer master role"
        )
    
    # Проверяем, что целевой пользователь является участником игры
    to_participant = db.query(GameParticipant).filter(
        GameParticipant.game_id == game_id,
        GameParticipant.user_id == to_user_id
    ).first()
    
    if not to_participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target user is not a participant of this game"
        )
    
    # Нельзя передать роль самому себе
    if from_user_id == to_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot transfer master role to yourself"
        )
    
    # Меняем роли
    from_participant.role = "player"
    to_participant.role = "master"
    
    # Обновляем master_id в GameSession
    game.master_id = to_user_id
    
    db.commit()
    db.refresh(game)
    return game