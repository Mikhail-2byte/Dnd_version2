import pytest
from uuid import uuid4
from app.services.game_service import (
    generate_invite_code,
    create_game,
    get_game_by_invite_code,
    get_game_by_id,
    join_game,
    is_master,
    create_token,
    update_token_position,
    delete_token,
    get_game_tokens,
)
from app.schemas.game import GameCreate
from app.schemas.token import TokenCreate, TokenUpdate
from app.models.game_session import GameSession
from app.models.game_participant import GameParticipant
from app.models.token import Token
from fastapi import HTTPException, status


def test_generate_invite_code():
    """Тест генерации invite-кода"""
    code = generate_invite_code()
    assert len(code) == 6
    assert code.isalnum()
    assert code.isupper() or any(c.isdigit() for c in code)


def test_create_game(db_session, test_user):
    """Тест создания игры через сервис"""
    game_data = GameCreate(name="Test Game", story="Test story")
    game = create_game(db_session, game_data, test_user.id)
    
    assert game.name == "Test Game"
    assert game.story == "Test story"
    assert game.master_id == test_user.id
    assert len(game.invite_code) == 6
    
    # Проверяем что мастер добавлен как участник
    participant = db_session.query(GameParticipant).filter(
        GameParticipant.game_id == game.id,
        GameParticipant.user_id == test_user.id
    ).first()
    assert participant is not None
    assert participant.role == "master"


def test_get_game_by_invite_code(db_session, test_game):
    """Тест получения игры по invite-коду через сервис"""
    game = get_game_by_invite_code(db_session, test_game.invite_code)
    assert game.id == test_game.id
    assert game.invite_code == test_game.invite_code


def test_get_game_by_invite_code_not_found(db_session):
    """Тест получения несуществующей игры по invite-коду"""
    with pytest.raises(HTTPException) as exc_info:
        get_game_by_invite_code(db_session, "NONEXIST")
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


def test_get_game_by_id(db_session, test_game):
    """Тест получения игры по ID через сервис"""
    game = get_game_by_id(db_session, test_game.id)
    assert game.id == test_game.id


def test_get_game_by_id_not_found(db_session):
    """Тест получения несуществующей игры по ID"""
    fake_id = uuid4()
    with pytest.raises(HTTPException) as exc_info:
        get_game_by_id(db_session, fake_id)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


def test_join_game(db_session, test_game, test_user2):
    """Тест присоединения к игре через сервис"""
    game = join_game(db_session, test_game.id, test_user2.id)
    
    # Проверяем что пользователь добавлен как участник
    participant = db_session.query(GameParticipant).filter(
        GameParticipant.game_id == test_game.id,
        GameParticipant.user_id == test_user2.id
    ).first()
    assert participant is not None
    assert participant.role == "player"


def test_join_game_already_participant(db_session, test_game, test_user):
    """Тест присоединения к игре если уже участник"""
    # Мастер уже участник
    game = join_game(db_session, test_game.id, test_user.id)
    assert game.id == test_game.id
    
    # Проверяем что участник не дублируется
    participants = db_session.query(GameParticipant).filter(
        GameParticipant.game_id == test_game.id,
        GameParticipant.user_id == test_user.id
    ).all()
    assert len(participants) == 1


def test_is_master(db_session, test_game, test_user, test_user2):
    """Тест проверки является ли пользователь мастером"""
    assert is_master(db_session, test_game.id, test_user.id) == True
    assert is_master(db_session, test_game.id, test_user2.id) == False


def test_create_token(db_session, test_game):
    """Тест создания токена через сервис"""
    token_data = TokenCreate(name="Test Token", x=25.5, y=30.0)
    token = create_token(db_session, test_game.id, token_data)
    
    assert token.name == "Test Token"
    assert token.x == 25.5
    assert token.y == 30.0
    assert token.game_id == test_game.id


def test_update_token_position(db_session, test_token):
    """Тест обновления позиции токена через сервис"""
    token_update = TokenUpdate(x=60.0, y=70.0)
    updated_token = update_token_position(db_session, test_token.id, token_update)
    
    assert updated_token.x == 60.0
    assert updated_token.y == 70.0
    assert updated_token.id == test_token.id


def test_delete_token(db_session, test_token):
    """Тест удаления токена через сервис"""
    token_id = test_token.id
    delete_token(db_session, token_id)
    
    # Проверяем что токен удален
    deleted_token = db_session.query(Token).filter(Token.id == token_id).first()
    assert deleted_token is None


def test_get_game_tokens(db_session, test_game, test_token):
    """Тест получения всех токенов игры через сервис"""
    tokens = get_game_tokens(db_session, test_game.id)
    assert len(tokens) >= 1
    assert any(token.id == test_token.id for token in tokens)


def test_get_game_tokens_empty(db_session, test_game):
    """Тест получения токенов игры когда их нет"""
    # Создаем новую игру без токенов
    from app.services.game_service import create_game
    from app.schemas.game import GameCreate
    game_data = GameCreate(name="Empty Game", story="No tokens")
    new_game = create_game(db_session, game_data, test_game.master_id)
    
    tokens = get_game_tokens(db_session, new_game.id)
    assert len(tokens) == 0

