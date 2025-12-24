import pytest
from fastapi import status
from uuid import uuid4


def test_create_token_master(authenticated_client, test_game, test_user):
    """Тест создания токена мастером"""
    response = authenticated_client.post(
        f"/api/games/{test_game.id}/tokens",
        json={
            "name": "Test Token",
            "x": 25.5,
            "y": 30.0,
            "image_url": None
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Test Token"
    assert data["x"] == 25.5
    assert data["y"] == 30.0
    assert data["game_id"] == str(test_game.id)
    assert "id" in data
    assert "created_at" in data


def test_create_token_player(client, db_session, test_game, test_user2):
    """Тест создания токена игроком (должна быть ошибка 403)"""
    # Создаем токен для второго пользователя (игрока)
    from app.utils.jwt import create_access_token
    from datetime import timedelta
    from app.config import settings
    
    token = create_access_token(
        data={"sub": str(test_user2.id), "email": test_user2.email},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    client.headers.update({"Authorization": f"Bearer {token}"})
    
    # Добавляем второго пользователя как игрока
    from app.services.game_service import join_game
    join_game(db_session, test_game.id, test_user2.id)
    
    response = client.post(
        f"/api/games/{test_game.id}/tokens",
        json={
            "name": "Test Token",
            "x": 25.5,
            "y": 30.0
        }
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "Only master can create tokens" in response.json()["detail"]


def test_update_token_position_master(authenticated_client, test_game, test_token):
    """Тест обновления позиции токена мастером"""
    response = authenticated_client.put(
        f"/api/games/{test_game.id}/tokens/{test_token.id}",
        json={
            "x": 75.0,
            "y": 80.0
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["x"] == 75.0
    assert data["y"] == 80.0
    assert data["id"] == str(test_token.id)


def test_update_token_position_player(client, db_session, test_game, test_token, test_user2):
    """Тест обновления позиции токена игроком (должна быть ошибка 403)"""
    # Создаем токен для второго пользователя (игрока)
    from app.utils.jwt import create_access_token
    from datetime import timedelta
    from app.config import settings
    
    token = create_access_token(
        data={"sub": str(test_user2.id), "email": test_user2.email},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    client.headers.update({"Authorization": f"Bearer {token}"})
    
    # Добавляем второго пользователя как игрока
    from app.services.game_service import join_game
    join_game(db_session, test_game.id, test_user2.id)
    
    response = client.put(
        f"/api/games/{test_game.id}/tokens/{test_token.id}",
        json={
            "x": 75.0,
            "y": 80.0
        }
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "Only master can move tokens" in response.json()["detail"]


def test_delete_token_master(authenticated_client, test_game, test_token):
    """Тест удаления токена мастером"""
    response = authenticated_client.delete(
        f"/api/games/{test_game.id}/tokens/{test_token.id}"
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Проверяем, что токен действительно удален
    get_response = authenticated_client.get(f"/api/games/{test_game.id}/tokens")
    assert get_response.status_code == status.HTTP_200_OK
    tokens = get_response.json()
    token_ids = [t["id"] for t in tokens]
    assert str(test_token.id) not in token_ids


def test_delete_token_player(client, db_session, test_game, test_token, test_user2):
    """Тест удаления токена игроком (должна быть ошибка 403)"""
    # Создаем токен для второго пользователя (игрока)
    from app.utils.jwt import create_access_token
    from datetime import timedelta
    from app.config import settings
    
    token = create_access_token(
        data={"sub": str(test_user2.id), "email": test_user2.email},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    client.headers.update({"Authorization": f"Bearer {token}"})
    
    # Добавляем второго пользователя как игрока
    from app.services.game_service import join_game
    join_game(db_session, test_game.id, test_user2.id)
    
    response = client.delete(
        f"/api/games/{test_game.id}/tokens/{test_token.id}"
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "Only master can delete tokens" in response.json()["detail"]


def test_get_game_tokens(authenticated_client, test_game, test_token):
    """Тест получения всех токенов игры"""
    response = authenticated_client.get(f"/api/games/{test_game.id}/tokens")
    assert response.status_code == status.HTTP_200_OK
    tokens = response.json()
    assert isinstance(tokens, list)
    assert len(tokens) == 1
    assert tokens[0]["id"] == str(test_token.id)
    assert tokens[0]["name"] == test_token.name
    assert tokens[0]["x"] == test_token.x
    assert tokens[0]["y"] == test_token.y

