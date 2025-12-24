from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from uuid import UUID
from ..models.character import Character
from ..schemas.character import CharacterCreate, CharacterUpdate


def create_character(db: Session, user_id: UUID, character_data: CharacterCreate) -> Character:
    """Создание нового персонажа"""
    db_character = Character(
        user_id=user_id,
        name=character_data.name,
        race=character_data.race,
        char_class=character_data.char_class,
        level=character_data.level,
        strength=character_data.strength,
        dexterity=character_data.dexterity,
        constitution=character_data.constitution,
        intelligence=character_data.intelligence,
        wisdom=character_data.wisdom,
        charisma=character_data.charisma,
        character_history=character_data.character_history,
        equipment_and_features=character_data.equipment_and_features,
        avatar_url=character_data.avatar_url
    )
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    return db_character


def get_character_by_id(db: Session, character_id: UUID) -> Character:
    """Получение персонажа по ID"""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )
    return character


def get_user_characters(db: Session, user_id: UUID) -> list[Character]:
    """Получение всех персонажей пользователя"""
    return db.query(Character).filter(Character.user_id == user_id).all()


def update_character(db: Session, character_id: UUID, character_data: CharacterUpdate) -> Character:
    """Обновление персонажа"""
    character = get_character_by_id(db, character_id)
    
    update_data = character_data.model_dump(exclude_unset=True, by_alias=False)
    # Преобразуем char_class из alias "class" если есть
    if "char_class" in update_data:
        character.char_class = update_data.pop("char_class")
    
    for field, value in update_data.items():
        if hasattr(character, field):
            setattr(character, field, value)
    
    db.commit()
    db.refresh(character)
    return character


def delete_character(db: Session, character_id: UUID) -> None:
    """Удаление персонажа"""
    character = get_character_by_id(db, character_id)
    db.delete(character)
    db.commit()


def validate_character_ownership(db: Session, character_id: UUID, user_id: UUID) -> bool:
    """Проверка, что персонаж принадлежит пользователю"""
    character = get_character_by_id(db, character_id)
    return character.user_id == user_id

