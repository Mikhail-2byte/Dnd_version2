from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from ..middleware.auth import get_current_user
from ..models.user import User
from ..services.dice_service import DiceRoller, get_templates, apply_template
from ..services.character_service import get_character_by_id
from ..database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/dice", tags=["dice"])

# Создаем экземпляр сервиса для броска кубиков
dice_roller = DiceRoller(default_faces=12, max_dice=10)


class DiceRollRequest(BaseModel):
    count: int = Field(ge=1, le=10, description="Количество кубиков")
    faces: int = Field(ge=2, le=20, description="Количество граней")
    advantage: Optional[bool] = Field(None, description="Преимущество (True) или помеха (False), None = обычный бросок")


class DieRoll(BaseModel):
    die_id: str
    value: int


class DiceRollResponse(BaseModel):
    rolls: List[DieRoll]
    total: int
    advantage_rolls: Optional[List[DieRoll]] = None
    selected_roll: Optional[DieRoll] = None
    advantage_type: Optional[str] = None


@router.post("/roll", response_model=DiceRollResponse, status_code=status.HTTP_200_OK)
async def roll_dice_endpoint(
    request: DiceRollRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Бросок кубиков
    
    Поддерживает стандартные D&D кубики: d4, d6, d8, d10, d12, d20
    """
    try:
        result = dice_roller.roll(request.count, request.faces, request.advantage)
        result_dict = dice_roller.to_dict(result)
        return DiceRollResponse(**result_dict)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


class DiceTemplateResponse(BaseModel):
    """Ответ с шаблонами бросков"""
    templates: Dict[str, Dict[str, Any]]


@router.get("/templates", response_model=DiceTemplateResponse)
async def get_dice_templates(
    current_user: User = Depends(get_current_user)
):
    """
    Получение всех доступных шаблонов бросков
    
    Шаблоны содержат предустановленные проверки (атака, спасбросок, проверка навыка)
    """
    templates = get_templates()
    return DiceTemplateResponse(templates=templates)


class ApplyTemplateRequest(BaseModel):
    """Запрос на применение шаблона"""
    template_name: str
    character_id: Optional[str] = None


class ApplyTemplateResponse(BaseModel):
    """Ответ с параметрами примененного шаблона"""
    count: int
    faces: int
    roll_type: str
    modifier: Optional[int] = None


@router.post("/templates/apply", response_model=ApplyTemplateResponse)
async def apply_dice_template(
    request: ApplyTemplateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Применение шаблона броска к персонажу
    
    Если указан character_id, модификатор будет рассчитан из характеристик персонажа
    """
    character = None
    if request.character_id:
        try:
            from uuid import UUID
            character = get_character_by_id(db, UUID(request.character_id))
            # Проверяем, что персонаж принадлежит текущему пользователю
            if character and character.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Этот персонаж вам не принадлежит"
                )
        except (ValueError, AttributeError):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Персонаж не найден"
            )
    
    try:
        result = apply_template(request.template_name, character)
        return ApplyTemplateResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

