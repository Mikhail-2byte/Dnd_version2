import pytest
from sqlalchemy.exc import IntegrityError
from uuid import uuid4
from app.models import User, GameSession, GameParticipant, Token
from app.utils.security import get_password_hash


def test_create_user(db_session):
    """Тест создания пользователя"""
    user = User(
        id=uuid4(),
        email="model_test@example.com",
        username="modeltest",
        password_hash=get_password_hash("password123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    assert user.id is not None
    assert user.email == "model_test@example.com"
    assert user.username == "modeltest"
    assert user.password_hash is not None
    assert user.created_at is not None


def test_user_email_unique(db_session, test_user):
    """Тест уникальности email"""
    # Пытаемся создать пользователя с тем же email
    duplicate_user = User(
        id=uuid4(),
        email=test_user.email,  # Дублирующий email
        username="anotheruser",
        password_hash=get_password_hash("password123")
    )
    db_session.add(duplicate_user)
    
    with pytest.raises(IntegrityError):
        db_session.commit()
    
    db_session.rollback()


def test_create_game_session(db_session, test_user):
    """Тест создания игровой сессии"""
    game = GameSession(
        id=uuid4(),
        name="Model Test Game",
        invite_code="MODEL1",
        master_id=test_user.id
    )
    db_session.add(game)
    db_session.commit()
    db_session.refresh(game)
    
    assert game.id is not None
    assert game.name == "Model Test Game"
    assert game.invite_code == "MODEL1"
    assert game.master_id == test_user.id
    assert game.created_at is not None


def test_create_game_participant(db_session, test_user, test_game):
    """Тест создания участника игры"""
    participant = GameParticipant(
        game_id=test_game.id,
        user_id=test_user.id,
        role="player"
    )
    db_session.add(participant)
    db_session.commit()
    
    # Проверяем, что участник создан
    found = db_session.query(GameParticipant).filter(
        GameParticipant.game_id == test_game.id,
        GameParticipant.user_id == test_user.id
    ).first()
    
    assert found is not None
    assert found.role == "player"
    assert found.joined_at is not None


def test_create_token(db_session, test_game):
    """Тест создания токена"""
    token = Token(
        id=uuid4(),
        game_id=test_game.id,
        name="Model Test Token",
        x=40.0,
        y=60.0,
        image_url="http://example.com/image.jpg"
    )
    db_session.add(token)
    db_session.commit()
    db_session.refresh(token)
    
    assert token.id is not None
    assert token.game_id == test_game.id
    assert token.name == "Model Test Token"
    assert token.x == 40.0
    assert token.y == 60.0
    assert token.image_url == "http://example.com/image.jpg"
    assert token.created_at is not None


def test_model_relationships(db_session, test_user, test_game, test_token):
    """Тест проверки связей между моделями"""
    # Проверяем связь GameSession -> User (master)
    assert test_game.master_id == test_user.id
    assert test_game.master is not None
    assert test_game.master.id == test_user.id
    
    # Проверяем связь GameSession -> GameParticipant
    participants = db_session.query(GameParticipant).filter(
        GameParticipant.game_id == test_game.id
    ).all()
    assert len(participants) > 0
    assert test_game.participants is not None
    
    # Проверяем связь GameSession -> Token
    tokens = db_session.query(Token).filter(
        Token.game_id == test_game.id
    ).all()
    assert len(tokens) > 0
    assert test_game.tokens is not None
    assert test_token in test_game.tokens
    
    # Проверяем связь Token -> GameSession
    assert test_token.game_id == test_game.id
    assert test_token.game is not None
    assert test_token.game.id == test_game.id
    
    # Проверяем связь GameParticipant -> GameSession
    participant = participants[0]
    assert participant.game_id == test_game.id
    assert participant.game is not None
    assert participant.game.id == test_game.id
    
    # Проверяем связь GameParticipant -> User
    assert participant.user_id == test_user.id
    assert participant.user is not None
    assert participant.user.id == test_user.id

