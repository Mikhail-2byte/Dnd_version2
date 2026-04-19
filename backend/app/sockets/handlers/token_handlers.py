import logging
from uuid import UUID
from ...database import SessionLocal
from ...services.game_service import is_master, create_token, update_token_position, delete_token, get_game_tokens
from ..state import connected_users
from ..cache import save_game_state_to_redis

logger = logging.getLogger(__name__)


def register_token_handlers(sio):
    @sio.event
    async def token_move(sid, data):
        """Перемещение токена"""
        try:
            if sid not in connected_users:
                logger.warning(f"Unauthenticated token_move attempt: {sid}")
                return

            user_id = connected_users[sid]

            if not data or not isinstance(data, dict):
                logger.warning(f"Invalid data format for token_move: {sid}")
                await sio.emit("error", {"message": "Invalid data format"}, room=sid)
                return

            try:
                game_id = UUID(data.get("game_id"))
                token_id = UUID(data.get("token_id"))
                x = float(data.get("x"))
                y = float(data.get("y"))
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid token_move data: {e}")
                await sio.emit("error", {"message": "Invalid token_move data"}, room=sid)
                return

            if not (0 <= x <= 100) or not (0 <= y <= 100):
                logger.warning(f"Invalid coordinates: x={x}, y={y}")
                await sio.emit("error", {"message": "Coordinates must be between 0 and 100"}, room=sid)
                return

            db = SessionLocal()
            try:
                if not is_master(db, game_id, user_id):
                    logger.warning(f"User {user_id} attempted to move token without master rights")
                    await sio.emit("error", {"message": "Only master can move tokens"}, room=sid)
                    return

                from ...schemas.token import TokenUpdate
                token_update = TokenUpdate(x=x, y=y)
                update_token_position(db, token_id, token_update)

                tokens = get_game_tokens(db, game_id)
                save_game_state_to_redis(game_id, tokens)

                await sio.emit("token:moved", {
                    "token_id": str(token_id),
                    "x": x,
                    "y": y,
                    "moved_by": str(user_id)
                }, room=f"game:{game_id}")
                logger.debug(f"Token {token_id} moved to ({x}, {y}) by user {user_id}")

            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error in token_move for sid {sid}: {e}", exc_info=True)
            await sio.emit("error", {"message": "Internal server error"}, room=sid)

    @sio.event
    async def token_create(sid, data):
        """Создание токена"""
        try:
            if sid not in connected_users:
                logger.warning(f"Unauthenticated token_create attempt: {sid}")
                return

            user_id = connected_users[sid]

            if not data or not isinstance(data, dict):
                logger.warning(f"Invalid data format for token_create: {sid}")
                await sio.emit("error", {"message": "Invalid data format"}, room=sid)
                return

            try:
                game_id = UUID(data.get("game_id"))
                name = data.get("name", "").strip()
                x = float(data.get("x"))
                y = float(data.get("y"))
                image_url = data.get("image_url")
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid token_create data: {e}")
                await sio.emit("error", {"message": "Invalid token_create data"}, room=sid)
                return

            if not name:
                logger.warning(f"Missing token name in token_create")
                await sio.emit("error", {"message": "Token name is required"}, room=sid)
                return

            if not (0 <= x <= 100) or not (0 <= y <= 100):
                logger.warning(f"Invalid coordinates: x={x}, y={y}")
                await sio.emit("error", {"message": "Coordinates must be between 0 and 100"}, room=sid)
                return

            db = SessionLocal()
            try:
                if not is_master(db, game_id, user_id):
                    logger.warning(f"User {user_id} attempted to create token without master rights")
                    await sio.emit("error", {"message": "Only master can create tokens"}, room=sid)
                    return

                from ...schemas.token import TokenCreate
                token_data = TokenCreate(name=name, x=x, y=y, image_url=image_url)
                token = create_token(db, game_id, token_data)
                logger.info(f"Token {token.id} ({name}) created by user {user_id} in game {game_id}")

                tokens = get_game_tokens(db, game_id)
                save_game_state_to_redis(game_id, tokens)

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
        except Exception as e:
            logger.error(f"Error in token_create for sid {sid}: {e}", exc_info=True)
            await sio.emit("error", {"message": "Internal server error"}, room=sid)

    @sio.event
    async def token_delete(sid, data):
        """Удаление токена"""
        try:
            if sid not in connected_users:
                logger.warning(f"Unauthenticated token_delete attempt: {sid}")
                return

            user_id = connected_users[sid]

            if not data or not isinstance(data, dict):
                logger.warning(f"Invalid data format for token_delete: {sid}")
                await sio.emit("error", {"message": "Invalid data format"}, room=sid)
                return

            try:
                game_id = UUID(data.get("game_id"))
                token_id = UUID(data.get("token_id"))
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid token_delete data: {e}")
                await sio.emit("error", {"message": "Invalid token_delete data"}, room=sid)
                return

            db = SessionLocal()
            try:
                if not is_master(db, game_id, user_id):
                    logger.warning(f"User {user_id} attempted to delete token without master rights")
                    await sio.emit("error", {"message": "Only master can delete tokens"}, room=sid)
                    return

                delete_token(db, token_id)
                logger.info(f"Token {token_id} deleted by user {user_id} in game {game_id}")

                tokens = get_game_tokens(db, game_id)
                save_game_state_to_redis(game_id, tokens)

                await sio.emit("token:deleted", {
                    "token_id": str(token_id)
                }, room=f"game:{game_id}")

            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error in token_delete for sid {sid}: {e}", exc_info=True)
            await sio.emit("error", {"message": "Internal server error"}, room=sid)
