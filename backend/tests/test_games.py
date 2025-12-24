import pytest
from fastapi import status
from uuid import uuid4


def test_create_game_success(authenticated_client, test_user):
    """Тест успешного создания игры"""
    response = authenticated_client.post(
        "/api/games",
        json={"name": "Test Adventure"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Test Adventure"
    assert "id" in data
    assert "invite_code" in data
    assert len(data["invite_code"]) == 6
    assert data["master_id"] == str(test_user.id)
    assert "created_at" in data


def test_create_game_unauthorized(client):
    """Тест создания игры без авторизации"""
    response = client.post(
        "/api/games",
        json={"name": "Test Adventure"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_game_by_invite_code(client, db_session, test_game):
    """Тест получения игры по invite-коду"""
    response = client.get(f"/api/games/{test_game.invite_code}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(test_game.id)
    assert data["name"] == test_game.name
    assert data["invite_code"] == test_game.invite_code
    assert data["master_id"] == str(test_game.master_id)


def test_get_game_invalid_invite_code(client, db_session):
    """Тест получения игры с несуществующим invite-кодом"""
    response = client.get("/api/games/INVALID")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Game not found" in response.json()["detail"]


def test_join_game_success(client, db_session, test_game, test_user2):
    """Тест успешного присоединения к игре"""
    # Создаем токен для второго пользователя
    from app.utils.jwt import create_access_token
    from datetime import timedelta
    from app.config import settings
    
    token = create_access_token(
        data={"sub": str(test_user2.id), "email": test_user2.email},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    client.headers.update({"Authorization": f"Bearer {token}"})
    
    response = client.post(f"/api/games/{test_game.id}/join")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(test_game.id)


def test_join_game_nonexistent(authenticated_client):
    """Тест присоединения к несуществующей игре"""
    fake_game_id = uuid4()
    response = authenticated_client.post(f"/api/games/{fake_game_id}/join")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Game not found" in response.json()["detail"]


def test_get_game_info(authenticated_client, test_game):
    """Тест получения деталей игры"""
    response = authenticated_client.get(f"/api/games/{test_game.id}/info")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(test_game.id)
    assert data["name"] == test_game.name
    assert data["invite_code"] == test_game.invite_code


def test_generate_unique_invite_code(client, db_session, authenticated_client, test_user):
    """Тест генерации уникального invite-кода"""
    # Создаем несколько игр и проверяем, что invite-коды уникальны
    invite_codes = set()
    for i in range(5):
        response = authenticated_client.post(
            "/api/games",
            json={"name": f"Test Game {i}"}
        )
        assert response.status_code == status.HTTP_201_CREATED
        invite_code = response.json()["invite_code"]
        assert invite_code not in invite_codes, "Invite codes must be unique"
        invite_codes.add(invite_code)
        assert len(invite_code) == 6

