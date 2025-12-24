import pytest
from fastapi.testclient import TestClient


def test_roll_dice_success(client: TestClient, auth_headers: dict):
    """Тест успешного броска кубиков"""
    response = client.post(
        "/api/dice/roll",
        json={"count": 2, "faces": 20},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "rolls" in data
    assert "total" in data
    assert len(data["rolls"]) == 2
    assert all(1 <= roll["value"] <= 20 for roll in data["rolls"])
    assert data["total"] == sum(roll["value"] for roll in data["rolls"])


def test_roll_dice_single_die(client: TestClient, auth_headers: dict):
    """Тест броска одного кубика"""
    response = client.post(
        "/api/dice/roll",
        json={"count": 1, "faces": 6},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["rolls"]) == 1
    assert 1 <= data["rolls"][0]["value"] <= 6
    assert data["total"] == data["rolls"][0]["value"]


def test_roll_dice_multiple_dice(client: TestClient, auth_headers: dict):
    """Тест броска нескольких кубиков"""
    response = client.post(
        "/api/dice/roll",
        json={"count": 5, "faces": 6},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["rolls"]) == 5
    assert all(1 <= roll["value"] <= 6 for roll in data["rolls"])
    assert data["total"] == sum(roll["value"] for roll in data["rolls"])


def test_roll_dice_allowed_faces(client: TestClient, auth_headers: dict):
    """Тест броска всех разрешенных типов кубиков"""
    allowed_faces = [4, 6, 8, 10, 12, 20]
    
    for faces in allowed_faces:
        response = client.post(
            "/api/dice/roll",
            json={"count": 1, "faces": faces},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert 1 <= data["rolls"][0]["value"] <= faces


def test_roll_dice_invalid_count(client: TestClient, auth_headers: dict):
    """Тест броска с невалидным количеством кубиков"""
    # Слишком мало
    response = client.post(
        "/api/dice/roll",
        json={"count": 0, "faces": 20},
        headers=auth_headers
    )
    assert response.status_code == 422
    
    # Слишком много
    response = client.post(
        "/api/dice/roll",
        json={"count": 11, "faces": 20},
        headers=auth_headers
    )
    assert response.status_code == 422


def test_roll_dice_invalid_faces(client: TestClient, auth_headers: dict):
    """Тест броска с невалидным количеством граней"""
    # Слишком мало граней
    response = client.post(
        "/api/dice/roll",
        json={"count": 1, "faces": 1},
        headers=auth_headers
    )
    assert response.status_code == 422
    
    # Неразрешенное количество граней
    response = client.post(
        "/api/dice/roll",
        json={"count": 1, "faces": 7},
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "Недопустимое количество граней" in response.json()["detail"]


def test_roll_dice_without_auth(client: TestClient):
    """Тест броска кубиков без аутентификации"""
    response = client.post(
        "/api/dice/roll",
        json={"count": 1, "faces": 20}
    )
    assert response.status_code == 401


def test_roll_dice_missing_fields(client: TestClient, auth_headers: dict):
    """Тест броска кубиков с отсутствующими полями"""
    response = client.post(
        "/api/dice/roll",
        json={"count": 1},
        headers=auth_headers
    )
    assert response.status_code == 422
    
    response = client.post(
        "/api/dice/roll",
        json={"faces": 20},
        headers=auth_headers
    )
    assert response.status_code == 422

