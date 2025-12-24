from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from ..database import get_db
from ..schemas.game import GameCreate, GameResponse
from ..schemas.token import TokenCreate, TokenResponse as TokenResponseSchema, TokenUpdate
from ..services.game_service import (
    create_game,
    get_game_by_invite_code,
    get_game_by_id,
    join_game,
    is_master,
    create_token,
    update_token_position,
    delete_token,
    get_game_tokens
)
from ..middleware.auth import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/games", tags=["games"])


@router.post("", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
async def create_game_endpoint(
    game_data: GameCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создание новой игровой сессии"""
    game = create_game(db, game_data, current_user.id)
    return GameResponse.model_validate(game)


@router.get("/{invite_code}", response_model=GameResponse)
async def get_game_by_invite(
    invite_code: str,
    db: Session = Depends(get_db)
):
    """Получение информации о игре по invite-коду"""
    game = get_game_by_invite_code(db, invite_code)
    return GameResponse.model_validate(game)


@router.post("/{game_id}/join", response_model=GameResponse)
async def join_game_endpoint(
    game_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Присоединение к игре"""
    game = join_game(db, game_id, current_user.id)
    return GameResponse.model_validate(game)


@router.get("/{game_id}/info", response_model=GameResponse)
async def get_game_info(
    game_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение деталей игры"""
    game = get_game_by_id(db, game_id)
    return GameResponse.model_validate(game)


@router.get("/{game_id}/tokens", response_model=list[TokenResponseSchema])
async def get_tokens(
    game_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение всех токенов игры"""
    tokens = get_game_tokens(db, game_id)
    return [TokenResponseSchema.model_validate(token) for token in tokens]


@router.post("/{game_id}/tokens", response_model=TokenResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_token_endpoint(
    game_id: UUID,
    token_data: TokenCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создание токена (только мастер)"""
    if not is_master(db, game_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only master can create tokens"
        )
    token = create_token(db, game_id, token_data)
    return TokenResponseSchema.model_validate(token)


@router.put("/{game_id}/tokens/{token_id}", response_model=TokenResponseSchema)
async def update_token_endpoint(
    game_id: UUID,
    token_id: UUID,
    token_data: TokenUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновление позиции токена (только мастер)"""
    if not is_master(db, game_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only master can move tokens"
        )
    token = update_token_position(db, token_id, token_data)
    return TokenResponseSchema.model_validate(token)


@router.delete("/{game_id}/tokens/{token_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_token_endpoint(
    game_id: UUID,
    token_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удаление токена (только мастер)"""
    if not is_master(db, game_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only master can delete tokens"
        )
    delete_token(db, token_id)

