"""
Тесты для описания сцен через WebSocket
"""
import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from app.models.user import User
from app.models.game_session import GameSession
from app.models.game_participant import GameParticipant


@pytest.fixture
def test_game_with_master_and_player(db_session, test_user, test_user2):
    """Создание игры с мастером и игроком"""
    game = GameSession(
        id=uuid4(),
        name="Test Game for Scene Description",
        invite_code="SCENE01",
        master_id=test_user.id
    )
    db_session.add(game)
    
    master_participant = GameParticipant(
        game_id=game.id,
        user_id=test_user.id,
        role="master"
    )
    player_participant = GameParticipant(
        game_id=game.id,
        user_id=test_user2.id,
        role="player"
    )
    db_session.add_all([master_participant, player_participant])
    db_session.commit()
    db_session.refresh(game)
    return game


class TestSceneDescriptionWebSocket:
    """Тесты для WebSocket событий описания сцен"""
    
    @pytest.mark.asyncio
    async def test_scene_description_by_master(self, test_game_with_master_and_player, test_user):
        """Мастер может отправлять описания сцен"""
        game = test_game_with_master_and_player
        
        # Имитируем WebSocket событие
        mock_sio = AsyncMock()
        mock_sid = "test_socket_id"
        
        # Настраиваем mock для auth
        mock_environ = {'HTTP_AUTHORIZATION': f'Bearer {test_user.id}'}
        
        with patch('app.sockets.game_events.get_user_from_token', return_value=test_user.id):
            with patch('app.sockets.game_events.SessionLocal') as mock_db:
                mock_db_instance = mock_db.return_value.__enter__.return_value
                
                # Настраиваем mock для проверки участника
                from app.models.game_participant import GameParticipant
                mock_participant = mock_db_instance.query.return_value.filter.return_value.first
                mock_participant.return_value = GameParticipant(
                    game_id=game.id,
                    user_id=test_user.id,
                    role="master"
                )
                
                # Настраиваем mock для проверки мастера
                with patch('app.sockets.game_events.is_master', return_value=True):
                    from app.sockets.game_events import register_socket_handlers
                    register_socket_handlers(mock_sio)
                    
                    # Вызываем обработчик
                    await mock_sio._handlers['scene:description'][0](
                        mock_sid,
                        {
                            "game_id": str(game.id),
                            "description": "Вы входите в темную пещеру...",
                            "title": "Пещера"
                        }
                    )
                    
                    # Проверяем, что событие было отправлено
                    mock_sio.emit.assert_called()
                    call_args = mock_sio.emit.call_args
                    assert call_args[0][0] == "scene:description_received"
                    assert call_args[0][1]["description"] == "Вы входите в темную пещеру..."
                    assert call_args[0][1]["title"] == "Пещера"
    
    @pytest.mark.asyncio
    async def test_scene_description_by_player_forbidden(self, test_game_with_master_and_player, test_user2):
        """Игрок не может отправлять описания сцен"""
        game = test_game_with_master_and_player
        
        mock_sio = AsyncMock()
        mock_sid = "test_socket_id"
        
        with patch('app.sockets.game_events.get_user_from_token', return_value=test_user2.id):
            with patch('app.sockets.game_events.SessionLocal') as mock_db:
                mock_db_instance = mock_db.return_value.__enter__.return_value
                
                from app.models.game_participant import GameParticipant
                mock_participant = mock_db_instance.query.return_value.filter.return_value.first
                mock_participant.return_value = GameParticipant(
                    game_id=game.id,
                    user_id=test_user2.id,
                    role="player"
                )
                
                with patch('app.sockets.game_events.is_master', return_value=False):
                    from app.sockets.game_events import register_socket_handlers
                    register_socket_handlers(mock_sio)
                    
                    await mock_sio._handlers['scene:description'][0](
                        mock_sid,
                        {
                            "game_id": str(game.id),
                            "description": "Попытка отправить описание"
                        }
                    )
                    
                    # Проверяем, что была отправлена ошибка
                    mock_sio.emit.assert_called()
                    call_args = mock_sio.emit.call_args
                    assert call_args[0][0] == "error"
                    assert "Only master" in call_args[0][1]["message"].lower() or "мастер" in call_args[0][1]["message"].lower()
    
    @pytest.mark.asyncio
    async def test_scene_description_empty_description(self, test_game_with_master_and_player, test_user):
        """Пустое описание отклоняется"""
        game = test_game_with_master_and_player
        
        mock_sio = AsyncMock()
        mock_sid = "test_socket_id"
        
        with patch('app.sockets.game_events.get_user_from_token', return_value=test_user.id):
            with patch('app.sockets.game_events.SessionLocal') as mock_db:
                mock_db_instance = mock_db.return_value.__enter__.return_value
                
                from app.models.game_participant import GameParticipant
                mock_participant = mock_db_instance.query.return_value.filter.return_value.first
                mock_participant.return_value = GameParticipant(
                    game_id=game.id,
                    user_id=test_user.id,
                    role="master"
                )
                
                with patch('app.sockets.game_events.is_master', return_value=True):
                    from app.sockets.game_events import register_socket_handlers
                    register_socket_handlers(mock_sio)
                    
                    await mock_sio._handlers['scene:description'][0](
                        mock_sid,
                        {
                            "game_id": str(game.id),
                            "description": ""
                        }
                    )
                    
                    # Проверяем, что была отправлена ошибка
                    mock_sio.emit.assert_called()
                    call_args = mock_sio.emit.call_args
                    assert call_args[0][0] == "error"
                    assert "required" in call_args[0][1]["message"].lower() or "обязательно" in call_args[0][1]["message"].lower()

