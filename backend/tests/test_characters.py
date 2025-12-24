import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
from app.models.character import Character
from app.schemas.character import CharacterCreate, CharacterUpdate


def test_create_character(client: TestClient, auth_headers: dict, test_user_id):
    """Тест создания персонажа"""
    character_data = {
        "name": "Торин Железная Борода",
        "race": "Дворф",
        "class": "Воин",
        "level": 5,
        "strength": 18,
        "dexterity": 12,
        "constitution": 16,
        "intelligence": 10,
        "wisdom": 13,
        "charisma": 8,
        "character_history": "Ветеран многих битв",
        "equipment_and_features": "Боевой топор, кольчуга"
    }
    
    response = client.post(
        "/api/characters",
        json=character_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == character_data["name"]
    assert data["race"] == character_data["race"]
    assert data["class"] == character_data["class"]
    assert data["level"] == character_data["level"]
    assert data["strength"] == character_data["strength"]
    assert "id" in data
    assert "user_id" in data
    assert "created_at" in data


def test_create_character_invalid_data(client: TestClient, auth_headers: dict):
    """Тест создания персонажа с невалидными данными"""
    # Недостаточно данных
    response = client.post(
        "/api/characters",
        json={"name": "Test"},
        headers=auth_headers
    )
    assert response.status_code == 422
    
    # Невалидные характеристики
    character_data = {
        "name": "Test",
        "race": "Human",
        "class": "Warrior",
        "strength": 35  # Превышает максимум
    }
    response = client.post(
        "/api/characters",
        json=character_data,
        headers=auth_headers
    )
    assert response.status_code == 422


def test_get_characters(client: TestClient, auth_headers: dict, test_user_id, db_session):
    """Тест получения всех персонажей пользователя"""
    # Создаем персонажа
    character = Character(
        user_id=test_user_id,
        name="Test Character",
        race="Human",
        char_class="Warrior",
        level=1
    )
    db_session.add(character)
    db_session.commit()
    
    response = client.get("/api/characters", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "characters" in data
    assert len(data["characters"]) >= 1
    assert any(c["name"] == "Test Character" for c in data["characters"])


def test_get_character_by_id(client: TestClient, auth_headers: dict, test_user_id, db_session):
    """Тест получения персонажа по ID"""
    character = Character(
        user_id=test_user_id,
        name="Test Character",
        race="Human",
        char_class="Warrior",
        level=1
    )
    db_session.add(character)
    db_session.commit()
    character_id = character.id
    
    response = client.get(f"/api/characters/{character_id}", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(character_id)
    assert data["name"] == "Test Character"


def test_get_character_not_found(client: TestClient, auth_headers: dict):
    """Тест получения несуществующего персонажа"""
    fake_id = uuid4()
    response = client.get(f"/api/characters/{fake_id}", headers=auth_headers)
    assert response.status_code == 404


def test_get_character_unauthorized_access(client: TestClient, auth_headers: dict, db_session):
    """Тест получения персонажа другого пользователя"""
    # Создаем другого пользователя
    from app.models.user import User
    from app.utils.security import get_password_hash
    
    other_user = User(
        email="other@test.com",
        username="other_user",
        password_hash=get_password_hash("password")
    )
    db_session.add(other_user)
    db_session.commit()
    
    # Создаем персонажа для другого пользователя
    character = Character(
        user_id=other_user.id,
        name="Other User Character",
        race="Elf",
        char_class="Mage",
        level=1
    )
    db_session.add(character)
    db_session.commit()
    character_id = character.id
    
    # Пытаемся получить персонажа другого пользователя
    response = client.get(f"/api/characters/{character_id}", headers=auth_headers)
    assert response.status_code == 403


def test_update_character(client: TestClient, auth_headers: dict, test_user_id, db_session):
    """Тест обновления персонажа"""
    character = Character(
        user_id=test_user_id,
        name="Test Character",
        race="Human",
        char_class="Warrior",
        level=1,
        strength=10
    )
    db_session.add(character)
    db_session.commit()
    character_id = character.id
    
    update_data = {
        "name": "Updated Character",
        "level": 5,
        "strength": 18
    }
    
    response = client.put(
        f"/api/characters/{character_id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Character"
    assert data["level"] == 5
    assert data["strength"] == 18
    # Проверяем, что остальные поля не изменились
    assert data["race"] == "Human"
    assert data["class"] == "Warrior"


def test_update_character_unauthorized(client: TestClient, auth_headers: dict, db_session):
    """Тест обновления персонажа другого пользователя"""
    from app.models.user import User
    from app.utils.security import get_password_hash
    
    other_user = User(
        email="other2@test.com",
        username="other_user2",
        password_hash=get_password_hash("password")
    )
    db_session.add(other_user)
    db_session.commit()
    
    character = Character(
        user_id=other_user.id,
        name="Other Character",
        race="Elf",
        char_class="Mage",
        level=1
    )
    db_session.add(character)
    db_session.commit()
    character_id = character.id
    
    response = client.put(
        f"/api/characters/{character_id}",
        json={"name": "Hacked"},
        headers=auth_headers
    )
    assert response.status_code == 403


def test_delete_character(client: TestClient, auth_headers: dict, test_user_id, db_session):
    """Тест удаления персонажа"""
    character = Character(
        user_id=test_user_id,
        name="To Delete",
        race="Human",
        char_class="Warrior",
        level=1
    )
    db_session.add(character)
    db_session.commit()
    character_id = character.id
    
    response = client.delete(f"/api/characters/{character_id}", headers=auth_headers)
    assert response.status_code == 204
    
    # Проверяем, что персонаж удален
    response = client.get(f"/api/characters/{character_id}", headers=auth_headers)
    assert response.status_code == 404


def test_delete_character_unauthorized(client: TestClient, auth_headers: dict, db_session):
    """Тест удаления персонажа другого пользователя"""
    from app.models.user import User
    from app.utils.security import get_password_hash
    
    other_user = User(
        email="other3@test.com",
        username="other_user3",
        password_hash=get_password_hash("password")
    )
    db_session.add(other_user)
    db_session.commit()
    
    character = Character(
        user_id=other_user.id,
        name="Other Character",
        race="Elf",
        char_class="Mage",
        level=1
    )
    db_session.add(character)
    db_session.commit()
    character_id = character.id
    
    response = client.delete(f"/api/characters/{character_id}", headers=auth_headers)
    assert response.status_code == 403


def test_character_without_auth(client: TestClient):
    """Тест доступа к персонажам без аутентификации"""
    response = client.get("/api/characters")
    assert response.status_code == 401
    
    response = client.post("/api/characters", json={"name": "Test"})
    assert response.status_code == 401

