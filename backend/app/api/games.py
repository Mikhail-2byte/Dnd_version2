from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc
from uuid import UUID
from typing import List, Optional
from ..database import get_db
from ..schemas.game import GameCreate, GameResponse, ParticipantReadyUpdate, ParticipantCharacterUpdate, ParticipantResponse, MasterTransferRequest, MasterTransferResponse, GiveItemRequest
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
    get_game_tokens,
    reveal_token,
    give_item_to_character,
    set_participant_ready,
    set_participant_character,
    get_game_participants,
    transfer_master_role
)
from ..middleware.auth import get_current_user
from ..models.user import User
from ..models.dice_roll_history import DiceRollHistory
from ..models.game_participant import GameParticipant
from ..sockets.game_events import emit_master_transferred
from ..sockets.state import started_games

router = APIRouter(prefix="/api/games", tags=["games"])


class DieRollSchema(BaseModel):
    """Схема для одного броска кубика"""
    die_id: str
    value: int


class DiceRollHistoryItem(BaseModel):
    """Элемент истории бросков"""
    id: UUID
    user_id: UUID
    username: str
    count: int
    faces: int
    rolls: List[DieRollSchema]
    total: int
    roll_type: Optional[str] = None
    modifier: Optional[int] = None
    advantage_type: Optional[str] = None
    advantage_rolls: Optional[List[DieRollSchema]] = None
    selected_roll: Optional[DieRollSchema] = None
    created_at: str

    class Config:
        from_attributes = True


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


@router.post("/{game_id}/spectate", response_model=GameResponse)
async def spectate_game_endpoint(
    game_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Присоединение к игре как наблюдатель"""
    from ..services.game_service import join_as_spectator
    game = join_as_spectator(db, game_id, current_user.id)
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
    """Получение токенов игры. Скрытые токены видны только мастеру."""
    include_hidden = is_master(db, game_id, current_user.id)
    tokens = get_game_tokens(db, game_id, include_hidden=include_hidden)
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


@router.post("/{game_id}/tokens/{token_id}/reveal", response_model=TokenResponseSchema)
async def reveal_token_endpoint(
    game_id: UUID,
    token_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Мастер раскрывает скрытый токен — токен становится виден всем игрокам"""
    if not is_master(db, game_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only master can reveal tokens")
    token = reveal_token(db, token_id, game_id)
    from ..sockets.emitters import emit_token_revealed
    await emit_token_revealed(game_id, {
        "token_id": str(token.id),
        "name": token.name,
        "x": token.x,
        "y": token.y,
        "image_url": token.image_url,
        "token_type": token.token_type,
        "token_metadata": token.token_metadata,
    })
    return TokenResponseSchema.model_validate(token)


@router.post("/{game_id}/give-item", status_code=status.HTTP_201_CREATED)
async def give_item_endpoint(
    game_id: UUID,
    data: GiveItemRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Мастер выдаёт предмет персонажу игрока"""
    if not is_master(db, game_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only master can give items")
    inv_item = give_item_to_character(db, game_id, data.character_id, data.item_type, data.item_id, data.quantity)
    return {"message": "Item given", "inventory_id": str(inv_item.id)}


@router.patch("/{game_id}/participants/me/ready", response_model=ParticipantResponse)
async def set_participant_ready_endpoint(
    game_id: UUID,
    ready_data: ParticipantReadyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Установка статуса готовности текущего участника"""
    participant = set_participant_ready(db, game_id, current_user.id, ready_data.is_ready)
    
    return ParticipantResponse(
        user_id=participant.user_id,
        username=current_user.username,
        role=participant.role,
        is_ready=participant.is_ready
    )


@router.patch("/{game_id}/participants/me/character", response_model=ParticipantResponse)
async def set_participant_character_endpoint(
    game_id: UUID,
    character_data: ParticipantCharacterUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Установка выбранного персонажа для текущего участника"""
    character_id = character_data.character_id if character_data.character_id else None
    participant = set_participant_character(db, game_id, current_user.id, character_id)
    
    return ParticipantResponse(
        user_id=participant.user_id,
        username=current_user.username,
        role=participant.role,
        is_ready=participant.is_ready,
        character_id=participant.character_id
    )


@router.get("/{game_id}/participants", response_model=list[ParticipantResponse])
async def get_participants_endpoint(
    game_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение списка участников игры с информацией о готовности и выбранном персонаже"""
    participants_data = get_game_participants(db, game_id)
    return [ParticipantResponse(**p) for p in participants_data]


@router.patch("/{game_id}/participants/{user_id}/transfer-master", response_model=MasterTransferResponse)
async def transfer_master_role_endpoint(
    game_id: UUID,
    user_id: UUID,
    transfer_data: MasterTransferRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Передача роли мастера другому игроку (только текущий мастер)"""
    # Проверяем, что текущий пользователь является мастером
    if not is_master(db, game_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only master can transfer master role"
        )
    
    # Передаем роль
    old_master_id = current_user.id
    game = transfer_master_role(db, game_id, old_master_id, transfer_data.to_user_id)
    
    # Отправляем WebSocket событие всем участникам игры
    await emit_master_transferred(game_id, old_master_id, transfer_data.to_user_id)
    
    return MasterTransferResponse(
        game=GameResponse.model_validate(game),
        new_master_id=transfer_data.to_user_id,
        old_master_id=old_master_id
    )


@router.get("/{game_id}/dice-history", response_model=List[DiceRollHistoryItem])
async def get_dice_history(
    game_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    user_id: Optional[UUID] = Query(None, description="Фильтр по пользователю"),
    roll_type: Optional[str] = Query(None, description="Фильтр по типу проверки (attack, save, skill, custom)"),
    limit: int = Query(50, ge=1, le=100, description="Количество записей"),
    offset: int = Query(0, ge=0, description="Смещение")
):
    """
    Получение истории бросков для игры с фильтрацией
    
    Требуется быть участником игры
    """
    # Проверяем, что пользователь является участником игры
    participant = db.query(GameParticipant).filter(
        GameParticipant.game_id == game_id,
        GameParticipant.user_id == current_user.id
    ).first()
    
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не являетесь участником этой игры"
        )
    
    # Формируем запрос с фильтрами
    query = db.query(DiceRollHistory).filter(
        DiceRollHistory.game_id == game_id
    )
    
    if user_id:
        query = query.filter(DiceRollHistory.user_id == user_id)
    
    if roll_type:
        query = query.filter(DiceRollHistory.roll_type == roll_type)
    
    # Сортируем по дате создания (новые сначала) и применяем пагинацию
    history = query.order_by(desc(DiceRollHistory.created_at)).offset(offset).limit(limit).all()
    
    # Получаем имена пользователей для всех записей
    user_ids = {entry.user_id for entry in history}
    users = {user.id: user.username for user in db.query(User).filter(User.id.in_(user_ids)).all()}
    
    # Формируем ответ
    result = []
    for entry in history:
        # Преобразуем advantage_rolls и selected_roll из JSON, если они есть
        advantage_rolls_list = None
        if entry.advantage_rolls:
            advantage_rolls_list = entry.advantage_rolls
        
        selected_roll_dict = None
        if entry.selected_roll:
            selected_roll_dict = entry.selected_roll
        
        result.append(DiceRollHistoryItem(
            id=entry.id,
            user_id=entry.user_id,
            username=users.get(entry.user_id, "Unknown"),
            count=entry.count,
            faces=entry.faces,
            rolls=entry.rolls,  # JSON уже является списком словарей
            total=entry.total,
            roll_type=entry.roll_type,
            modifier=entry.modifier,
            advantage_type=entry.advantage_type,
            advantage_rolls=advantage_rolls_list,
            selected_roll=selected_roll_dict,
            created_at=entry.created_at.isoformat()
        ))

    return result


@router.get("/{game_id}/status")
async def get_game_status(
    game_id: UUID,
    current_user: User = Depends(get_current_user),
):
    return {"started": game_id in started_games}
