from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from ..database import get_db
from ..models.user import User
from ..middleware.auth import get_current_user
from ..schemas.character import CharacterCreate, CharacterUpdate, CharacterResponse, CharacterListResponse
from ..services.character_service import (
    create_character,
    get_character_by_id,
    get_user_characters,
    update_character,
    delete_character,
    validate_character_ownership
)

router = APIRouter(prefix="/api/characters", tags=["characters"])


@router.post("", response_model=CharacterResponse, status_code=status.HTTP_201_CREATED)
async def create_character_endpoint(
    character_data: CharacterCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создание нового персонажа"""
    character = create_character(db, current_user.id, character_data)
    return CharacterResponse.model_validate(character)


@router.get("", response_model=CharacterListResponse)
async def get_characters_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение всех персонажей текущего пользователя"""
    characters = get_user_characters(db, current_user.id)
    return CharacterListResponse(
        characters=[CharacterResponse.model_validate(c) for c in characters]
    )


@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character_endpoint(
    character_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение персонажа по ID"""
    character = get_character_by_id(db, character_id)
    # Проверяем, что персонаж принадлежит пользователю
    if not validate_character_ownership(db, character_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this character"
        )
    return CharacterResponse.model_validate(character)


@router.put("/{character_id}", response_model=CharacterResponse)
async def update_character_endpoint(
    character_id: UUID,
    character_data: CharacterUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновление персонажа"""
    # Проверяем владение
    if not validate_character_ownership(db, character_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this character"
        )
    
    character = update_character(db, character_id, character_data)
    return CharacterResponse.model_validate(character)


@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character_endpoint(
    character_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удаление персонажа"""
    # Проверяем владение
    if not validate_character_ownership(db, character_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this character"
        )
    
    delete_character(db, character_id)
    return None

