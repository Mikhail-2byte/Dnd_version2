import json
from typing import Dict
from socketio import AsyncServer
from sqlalchemy.orm import Session
from uuid import UUID
from ..database import SessionLocal
from ..models.user import User
from ..models.game_session import GameSession
from ..models.game_participant import GameParticipant
from ..models.token import Token
from ..services.game_service import (
    get_game_by_id,
    is_master,
    create_token,
    update_token_position,
    delete_token,
    get_game_tokens
)
from ..utils.jwt import decode_access_token
from ..redis_client import redis_client


# Хранилище подключенных пользователей: {socket_id: user_id}
connected_users: Dict[str, UUID] = {}
# Хранилище комнат: {game_id: set(socket_ids)}
game_rooms: Dict[UUID, set] = {}


def get_user_from_token(token: str) -> UUID | None:
    """Получение user_id из JWT токена"""
    payload = decode_access_token(token)
    if payload:
        return UUID(payload.get("sub"))
    return None


def get_user_from_db(user_id: UUID) -> User | None:
    """Получение пользователя из БД"""
    db = SessionLocal()
    try:
        return db.query(User).filter(User.id == user_id).first()
    finally:
        db.close()


def get_game_state(db: Session, game_id: UUID) -> dict:
    """Получение полного состояния игры"""
    game = get_game_by_id(db, game_id)
    tokens = get_game_tokens(db, game_id)
    participants = db.query(GameParticipant).filter(
        GameParticipant.game_id == game_id
    ).all()
    
    # Получаем информацию об игроках
    players = []
    for participant in participants:
        user = db.query(User).filter(User.id == participant.user_id).first()
        if user:
            players.append({
                "user_id": str(user.id),
                "username": user.username,
                "role": participant.role
            })
    
    return {
        "game": {
            "id": str(game.id),
            "name": game.name,
            "invite_code": game.invite_code,
            "map_url": game.map_url
        },
        "tokens": [
            {
                "id": str(token.id),
                "name": token.name,
                "x": token.x,
                "y": token.y,
                "image_url": token.image_url
            }
            for token in tokens
        ],
        "players": players
    }


def save_game_state_to_redis(game_id: UUID, tokens: list[Token]) -> None:
    """Сохранение состояния игры в Redis"""
    # Сохраняем токены
    tokens_key = f"game:{game_id}:tokens"
    redis_client.delete(tokens_key)
    
    for token in tokens:
        token_data = {
            "id": str(token.id),
            "name": token.name,
            "x": token.x,
            "y": token.y,
            "image_url": token.image_url or ""
        }
        redis_client.hset(tokens_key, str(token.id), json.dumps(token_data))
    
    # Устанавливаем TTL 24 часа
    redis_client.expire(tokens_key, 86400)


def load_game_state_from_redis(game_id: UUID) -> list[dict] | None:
    """Загрузка состояния игры из Redis"""
    tokens_key = f"game:{game_id}:tokens"
    tokens_data = redis_client.hgetall(tokens_key)
    
    if not tokens_data:
        return None
    
    tokens = []
    for token_json in tokens_data.values():
        tokens.append(json.loads(token_json))
    
    return tokens


def register_socket_handlers(sio: AsyncServer):
    """Регистрация обработчиков Socket.IO событий"""
    
    @sio.event
    async def connect(sid, environ, auth):
        """Обработка подключения"""
        # Получаем токен из query параметров или auth
        token = None
        if auth and isinstance(auth, dict):
            token = auth.get("token")
        elif environ.get("QUERY_STRING"):
            query_string = environ["QUERY_STRING"]
            params = dict(param.split("=") for param in query_string.split("&") if "=" in param)
            token = params.get("token")
        
        if not token:
            return False
        
        user_id = get_user_from_token(token)
        if not user_id:
            return False
        
        connected_users[sid] = user_id
        return True
    
    @sio.event
    async def disconnect(sid):
        """Обработка отключения"""
        user_id = connected_users.pop(sid, None)
        
        # Удаляем из всех комнат
        for game_id, socket_ids in game_rooms.items():
            socket_ids.discard(sid)
            if not socket_ids:
                game_rooms.pop(game_id, None)
    
    @sio.event
    async def game_join(sid, data):
        """Подключение к игре"""
        if sid not in connected_users:
            await sio.emit("error", {"message": "Not authenticated"}, room=sid)
            return
        
        user_id = connected_users[sid]
        game_id = UUID(data.get("game_id"))
        
        db = SessionLocal()
        try:
            # Проверяем существование игры
            game = get_game_by_id(db, game_id)
            
            # Проверяем, является ли пользователь участником
            participant = db.query(GameParticipant).filter(
                GameParticipant.game_id == game_id,
                GameParticipant.user_id == user_id
            ).first()
            
            if not participant:
                await sio.emit("error", {"message": "Not a participant"}, room=sid)
                return
            
            # Добавляем в комнату
            if game_id not in game_rooms:
                game_rooms[game_id] = set()
            game_rooms[game_id].add(sid)
            await sio.enter_room(sid, f"game:{game_id}")
            
            # Отправляем полное состояние игры
            game_state = get_game_state(db, game_id)
            await sio.emit("game:state", game_state, room=sid)
            
            # Уведомляем других игроков
            user = get_user_from_db(user_id)
            if user:
                await sio.emit("player:joined", {
                    "user_id": str(user_id),
                    "username": user.username
                }, room=f"game:{game_id}", skip_sid=sid)
        
        finally:
            db.close()
    
    @sio.event
    async def token_move(sid, data):
        """Перемещение токена"""
        if sid not in connected_users:
            return
        
        user_id = connected_users[sid]
        game_id = UUID(data.get("game_id"))
        token_id = UUID(data.get("token_id"))
        x = float(data.get("x"))
        y = float(data.get("y"))
        
        db = SessionLocal()
        try:
            # Проверяем права (только мастер)
            if not is_master(db, game_id, user_id):
                await sio.emit("error", {"message": "Only master can move tokens"}, room=sid)
                return
            
            # Обновляем позицию
            from ..schemas.token import TokenUpdate
            token_update = TokenUpdate(x=x, y=y)
            token = update_token_position(db, token_id, token_update)
            
            # Сохраняем в Redis
            tokens = get_game_tokens(db, game_id)
            save_game_state_to_redis(game_id, tokens)
            
            # Broadcast изменения
            await sio.emit("token:moved", {
                "token_id": str(token_id),
                "x": x,
                "y": y,
                "moved_by": str(user_id)
            }, room=f"game:{game_id}")
        
        finally:
            db.close()
    
    @sio.event
    async def token_create(sid, data):
        """Создание токена"""
        if sid not in connected_users:
            return
        
        user_id = connected_users[sid]
        game_id = UUID(data.get("game_id"))
        name = data.get("name")
        x = float(data.get("x"))
        y = float(data.get("y"))
        image_url = data.get("image_url")
        
        db = SessionLocal()
        try:
            # Проверяем права (только мастер)
            if not is_master(db, game_id, user_id):
                await sio.emit("error", {"message": "Only master can create tokens"}, room=sid)
                return
            
            # Создаем токен
            from ..schemas.token import TokenCreate
            token_data = TokenCreate(name=name, x=x, y=y, image_url=image_url)
            token = create_token(db, game_id, token_data)
            
            # Сохраняем в Redis
            tokens = get_game_tokens(db, game_id)
            save_game_state_to_redis(game_id, tokens)
            
            # Broadcast создания
            await sio.emit("token:created", {
                "token": {
                    "id": str(token.id),
                    "name": token.name,
                    "x": token.x,
                    "y": token.y,
                    "image_url": token.image_url
                }
            }, room=f"game:{game_id}")
        
        finally:
            db.close()
    
    @sio.event
    async def dice_roll(sid, data):
        """Бросок кубиков"""
        if sid not in connected_users:
            return
        
        user_id = connected_users[sid]
        game_id = UUID(data.get("game_id"))
        count = int(data.get("count", 1))
        faces = int(data.get("faces", 20))
        
        db = SessionLocal()
        try:
            # Проверяем, что пользователь в игре
            participant = db.query(GameParticipant).filter(
                GameParticipant.game_id == game_id,
                GameParticipant.user_id == user_id
            ).first()
            
            if not participant:
                await sio.emit("error", {"message": "Not a participant"}, room=sid)
                return
            
            # Бросаем кубики
            from ..api.dice import roll_dice
            try:
                result = roll_dice(count, faces)
            except ValueError as e:
                await sio.emit("error", {"message": str(e)}, room=sid)
                return
            
            # Получаем пользователя для имени
            user = get_user_from_db(user_id)
            username = user.username if user else "Unknown"
            
            # Broadcast результата всем участникам игры
            await sio.emit("dice:rolled", {
                "game_id": str(game_id),
                "user_id": str(user_id),
                "username": username,
                "count": count,
                "faces": faces,
                "rolls": result["rolls"],
                "total": result["total"]
            }, room=f"game:{game_id}")
        
        finally:
            db.close()
    
    @sio.event
    async def token_delete(sid, data):
        """Удаление токена"""
        if sid not in connected_users:
            return
        
        user_id = connected_users[sid]
        game_id = UUID(data.get("game_id"))
        token_id = UUID(data.get("token_id"))
        
        db = SessionLocal()
        try:
            # Проверяем права (только мастер)
            if not is_master(db, game_id, user_id):
                await sio.emit("error", {"message": "Only master can delete tokens"}, room=sid)
                return
            
            # Удаляем токен
            delete_token(db, token_id)
            
            # Обновляем Redis
            tokens = get_game_tokens(db, game_id)
            save_game_state_to_redis(game_id, tokens)
            
            # Broadcast удаления
            await sio.emit("token:deleted", {
                "token_id": str(token_id)
            }, room=f"game:{game_id}")
        
        finally:
            db.close()

