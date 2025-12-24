import pytest
from fastapi import status


def test_register_user_success(client, db_session):
    """Тест успешной регистрации пользователя"""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "password123"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"
    assert "user" in data
    assert data["user"]["email"] == "newuser@example.com"
    assert data["user"]["username"] == "newuser"
    assert "id" in data["user"]
    assert "created_at" in data["user"]


def test_register_user_duplicate_email(client, db_session, test_user):
    """Тест регистрации с дублирующим email"""
    response = client.post(
        "/api/auth/register",
        json={
            "email": test_user.email,  # Используем email существующего пользователя
            "username": "anotheruser",
            "password": "password123"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Email already registered" in response.json()["detail"]


def test_login_success(client, db_session, test_user):
    """Тест успешного входа"""
    response = client.post(
        "/api/auth/login",
        json={
            "email": test_user.email,
            "password": "testpassword123"  # Пароль из фикстуры test_user
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"
    assert "user" in data
    assert data["user"]["email"] == test_user.email
    assert data["user"]["username"] == test_user.username


def test_login_wrong_password(client, db_session, test_user):
    """Тест входа с неправильным паролем"""
    response = client.post(
        "/api/auth/login",
        json={
            "email": test_user.email,
            "password": "wrongpassword"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Incorrect email or password" in response.json()["detail"]


def test_login_nonexistent_user(client, db_session):
    """Тест входа несуществующего пользователя"""
    response = client.post(
        "/api/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Incorrect email or password" in response.json()["detail"]


def test_get_current_user_success(authenticated_client, test_user):
    """Тест получения текущего пользователя с валидным токеном"""
    response = authenticated_client.get("/api/auth/me")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(test_user.id)
    assert data["email"] == test_user.email
    assert data["username"] == test_user.username
    assert "created_at" in data


def test_get_current_user_no_token(client):
    """Тест получения текущего пользователя без токена"""
    response = client.get("/api/auth/me")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_current_user_invalid_token(client):
    """Тест получения текущего пользователя с невалидным токеном"""
    client.headers.update({"Authorization": "Bearer invalid_token_here"})
    response = client.get("/api/auth/me")
    assert response.status_code == status.HTTP_403_FORBIDDEN

