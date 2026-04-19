"""
Тесты для API шаблонов бросков
"""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
from app.models.user import User
from app.models.game_session import GameSession
from app.models.game_participant import GameParticipant
from app.models.character import Character


@pytest.fixture
def auth_headers(test_user_token):
    """Получение заголовков авторизации"""
    return {"Authorization": f"Bearer {test_user_token}"}


@pytest.fixture
def test_character(authenticated_client, auth_headers: dict):
    """Создание тестового персонажа"""
    response = authenticated_client.post(
        "/api/characters",
        json={
            "name": "Test Fighter",
            "race": "Human",
            "char_class": "Fighter",
            "level": 1,
            "strength": 16,
            "dexterity": 14,
            "constitution": 12,
            "intelligence": 10,
            "wisdom": 8,
            "charisma": 6
        },
        headers=auth_headers
    )
    return response.json()


class TestDiceTemplatesAPI:
    """Тесты для API шаблонов бросков"""
    
    def test_get_templates(self, authenticated_client):
        """Получение списка шаблонов"""
        response = authenticated_client.get("/api/dice/templates")
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        templates = data["templates"]
        assert isinstance(templates, dict)
        assert len(templates) > 0
        # Проверяем наличие основных шаблонов
        assert "attack_melee" in templates
        assert "strength_save" in templates
    
    def test_get_templates_unauthorized(self, client: TestClient):
        """Получение шаблонов без авторизации"""
        response = client.get("/api/dice/templates")
        assert response.status_code == 401
    
    def test_apply_template_without_character(self, authenticated_client):
        """Применение шаблона без персонажа"""
        response = authenticated_client.post(
            "/api/dice/templates/apply",
            json={"template_name": "attack_melee"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["faces"] == 20
        assert data["roll_type"] == "attack"
        assert data["modifier"] is None
    
    def test_apply_template_with_character(self, authenticated_client, test_character: dict):
        """Применение шаблона с персонажем"""
        response = authenticated_client.post(
            "/api/dice/templates/apply",
            json={
                "template_name": "attack_melee",
                "character_id": test_character["id"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["faces"] == 20
        assert data["roll_type"] == "attack"
        # Сила персонажа = 16, модификатор = +3
        assert data["modifier"] == 3
    
    def test_apply_template_invalid_template(self, authenticated_client):
        """Применение несуществующего шаблона"""
        response = authenticated_client.post(
            "/api/dice/templates/apply",
            json={"template_name": "invalid_template"}
        )
        assert response.status_code == 400
    
    def test_apply_template_invalid_character(self, authenticated_client):
        """Применение шаблона с несуществующим персонажем"""
        response = authenticated_client.post(
            "/api/dice/templates/apply",
            json={
                "template_name": "attack_melee",
                "character_id": str(uuid4())
            }
        )
        assert response.status_code == 404


class TestDiceHistoryAPI:
    """Тесты для API истории бросков"""
    
    def test_get_dice_history_empty(self, authenticated_client, test_game):
        """Получение пустой истории бросков"""
        game_id = test_game.id
        response = authenticated_client.get(
            f"/api/games/{game_id}/dice-history"
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_dice_history_not_participant(self, authenticated_client):
        """Получение истории бросков без участия в игре"""
        game_id = str(uuid4())
        response = authenticated_client.get(
            f"/api/games/{game_id}/dice-history"
        )
        assert response.status_code == 403
    
    def test_get_dice_history_with_filters(self, authenticated_client, test_game):
        """Получение истории бросков с фильтрами"""
        game_id = test_game.id
        response = authenticated_client.get(
            f"/api/games/{game_id}/dice-history",
            params={"roll_type": "attack", "limit": 10}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

