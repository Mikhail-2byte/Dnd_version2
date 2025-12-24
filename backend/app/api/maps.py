from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from uuid import UUID
import os
import uuid
from ..database import get_db
from ..services.game_service import get_game_by_id, is_master
from ..middleware.auth import get_current_user
from ..models.user import User
from ..config import settings

router = APIRouter(prefix="/api/maps", tags=["maps"])


@router.post("/upload")
async def upload_map(
    game_id: UUID = Query(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Загрузка карты (только мастер)"""
    # Проверка прав
    game = get_game_by_id(db, game_id)
    if not is_master(db, game_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only master can upload maps"
        )
    
    # Проверка размера файла
    contents = await file.read()
    if len(contents) > settings.max_upload_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {settings.max_upload_size} bytes"
        )
    
    # Проверка типа файла
    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {allowed_extensions}"
        )
    
    # Генерируем уникальное имя файла
    file_id = str(uuid.uuid4())
    filename = f"{file_id}{file_ext}"
    file_path = os.path.join(settings.maps_dir, filename)
    
    # Сохраняем файл
    os.makedirs(settings.maps_dir, exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Обновляем URL карты в игре
    map_url = f"/uploads/maps/{filename}"
    game.map_url = map_url
    db.commit()
    
    return {"map_url": map_url, "message": "Map uploaded successfully"}

