from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict
import random
from ..middleware.auth import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/dice", tags=["dice"])


class DiceRollRequest(BaseModel):
    count: int = Field(ge=1, le=10, description="Количество кубиков")
    faces: int = Field(ge=2, le=20, description="Количество граней")


class DieRoll(BaseModel):
    die_id: str
    value: int


class DiceRollResponse(BaseModel):
    rolls: List[DieRoll]
    total: int


# Стандартные D&D кубики
ALLOWED_FACES = [4, 6, 8, 10, 12, 20]


def roll_dice(count: int, faces: int) -> Dict:
    """
    Бросок кубиков
    
    Args:
        count: Количество кубиков
        faces: Количество граней
        
    Returns:
        Словарь с результатами броска
    """
    if count <= 0:
        raise ValueError("Количество кубиков должно быть положительным")
    
    if count > 10:
        raise ValueError("Максимальное количество кубиков: 10")
    
    if faces < 2:
        raise ValueError("Количество граней должно быть не менее 2")
    
    if faces not in ALLOWED_FACES:
        raise ValueError(
            f"Недопустимое количество граней: {faces}. "
            f"Разрешены: {', '.join(map(str, ALLOWED_FACES))}"
        )
    
    rolls = []
    for i in range(count):
        value = random.randint(1, faces)
        rolls.append({
            "die_id": f"d{i + 1}",
            "value": value
        })
    
    total = sum(roll["value"] for roll in rolls)
    
    return {
        "rolls": rolls,
        "total": total
    }


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
        result = roll_dice(request.count, request.faces)
        return DiceRollResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

