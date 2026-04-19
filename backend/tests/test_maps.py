import pytest
from fastapi import status
from fastapi.testclient import TestClient
from io import BytesIO
from uuid import uuid4


def test_upload_map_success(authenticated_client, test_game, test_user, tmp_path):
    """Тест успешной загрузки карты мастером"""
    # Временно меняем директорию для сохранения карт
    import os
    from unittest.mock import patch
    
    # Создаем временную директорию для тестовых файлов
    test_maps_dir = tmp_path / "maps"
    test_maps_dir.mkdir()
    
    with patch('app.config.settings.maps_dir', str(test_maps_dir)):
        # Создаем тестовое изображение
        image_data = BytesIO(b'\x89PNG\r\n\x1a\nfake_png_data')
        image_data.name = "test_map.png"
        
        response = authenticated_client.post(
            f"/api/maps/upload?game_id={test_game.id}",
            files={"file": ("test_map.png", image_data, "image/png")}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "map_url" in data
        assert "message" in data
        assert data["message"] == "Map uploaded successfully"
        assert data["map_url"].startswith("/uploads/maps/")
        assert data["map_url"].endswith(".png")


def test_upload_map_not_master(client, db_session, test_game, test_user2):
    """Тест загрузки карты не мастером (должна быть ошибка 403)"""
    from app.utils.jwt import create_access_token
    from datetime import timedelta
    from app.config import settings
    from app.services.game_service import join_game
    
    # Создаем токен для второго пользователя
    token = create_access_token(
        data={"sub": str(test_user2.id), "email": test_user2.email},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    client.headers.update({"Authorization": f"Bearer {token}"})
    
    # Добавляем второго пользователя как игрока
    join_game(db_session, test_game.id, test_user2.id)
    
    # Пытаемся загрузить карту
    image_data = BytesIO(b'\x89PNG\r\n\x1a\nfake_png_data')
    image_data.name = "test_map.png"
    
    response = client.post(
        f"/api/maps/upload?game_id={test_game.id}",
        files={"file": ("test_map.png", image_data, "image/png")}
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "Only master can upload maps" in response.json()["detail"]


def test_upload_map_unauthorized(client, test_game):
    """Тест загрузки карты без авторизации"""
    image_data = BytesIO(b'\x89PNG\r\n\x1a\nfake_png_data')
    image_data.name = "test_map.png"
    
    response = client.post(
        f"/api/maps/upload?game_id={test_game.id}",
        files={"file": ("test_map.png", image_data, "image/png")}
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_upload_map_invalid_file_type(authenticated_client, test_game, tmp_path):
    """Тест загрузки файла неверного типа"""
    import os
    from unittest.mock import patch
    
    test_maps_dir = tmp_path / "maps"
    test_maps_dir.mkdir()
    
    with patch('app.config.settings.maps_dir', str(test_maps_dir)):
        # Пытаемся загрузить текстовый файл вместо изображения
        text_data = BytesIO(b"this is not an image")
        text_data.name = "test_file.txt"
        
        response = authenticated_client.post(
            f"/api/maps/upload?game_id={test_game.id}",
            files={"file": ("test_file.txt", text_data, "text/plain")}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid file type" in response.json()["detail"]


def test_upload_map_file_too_large(authenticated_client, test_game, tmp_path):
    """Тест загрузки слишком большого файла"""
    import os
    from unittest.mock import patch
    
    test_maps_dir = tmp_path / "maps"
    test_maps_dir.mkdir()
    
    with patch('app.config.settings.maps_dir', str(test_maps_dir)):
        with patch('app.config.settings.max_upload_size', 100):  # Устанавливаем очень маленький лимит
            # Создаем файл больше лимита
            large_data = BytesIO(b'\x89PNG\r\n\x1a\n' + b'x' * 200)
            large_data.name = "large_map.png"
            
            response = authenticated_client.post(
                f"/api/maps/upload?game_id={test_game.id}",
                files={"file": ("large_map.png", large_data, "image/png")}
            )
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "File too large" in response.json()["detail"]


def test_upload_map_nonexistent_game(authenticated_client, tmp_path):
    """Тест загрузки карты для несуществующей игры"""
    import os
    from unittest.mock import patch
    
    test_maps_dir = tmp_path / "maps"
    test_maps_dir.mkdir()
    
    with patch('app.config.settings.maps_dir', str(test_maps_dir)):
        fake_game_id = uuid4()
        image_data = BytesIO(b'\x89PNG\r\n\x1a\nfake_png_data')
        image_data.name = "test_map.png"
        
        response = authenticated_client.post(
            f"/api/maps/upload?game_id={fake_game_id}",
            files={"file": ("test_map.png", image_data, "image/png")}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize("file_ext,content_type", [
    (".jpg", "image/jpeg"),
    (".jpeg", "image/jpeg"),
    (".png", "image/png"),
    (".webp", "image/webp"),
])
def test_upload_map_allowed_formats(authenticated_client, test_game, tmp_path, file_ext, content_type):
    """Тест загрузки карты во всех разрешенных форматах"""
    import os
    from unittest.mock import patch
    
    test_maps_dir = tmp_path / "maps"
    test_maps_dir.mkdir()
    
    with patch('app.config.settings.maps_dir', str(test_maps_dir)):
        image_data = BytesIO(b'\x89PNG\r\n\x1a\nfake_image_data')
        image_data.name = f"test_map{file_ext}"
        
        response = authenticated_client.post(
            f"/api/maps/upload?game_id={test_game.id}",
            files={"file": (f"test_map{file_ext}", image_data, content_type)}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["map_url"].endswith(file_ext)

