import logging
import uuid
from datetime import datetime, timezone
from uuid import UUID
from ...database import SessionLocal
from ...models.game_participant import GameParticipant
from ..state import connected_users
from ..utils import get_user_from_db

logger = logging.getLogger(__name__)


def register_chat_handlers(sio):
    @sio.event
    async def game_send_message(sid, data):
        """Чат-сообщение от участника игры"""
        try:
            if sid not in connected_users:
                await sio.emit("error", {"message": "Not authenticated"}, room=sid)
                return

            user_id = connected_users[sid]

            if not data or not isinstance(data, dict):
                await sio.emit("error", {"message": "Invalid data format"}, room=sid)
                return

            game_id_str = data.get("game_id")
            message = str(data.get("message", "")).strip()
            is_ooc = bool(data.get("is_ooc", False))

            if not game_id_str or not message:
                await sio.emit("error", {"message": "Missing game_id or message"}, room=sid)
                return

            if len(message) > 1000:
                await sio.emit("error", {"message": "Message too long (max 1000 chars)"}, room=sid)
                return

            try:
                game_id = UUID(game_id_str)
            except (ValueError, TypeError):
                await sio.emit("error", {"message": "Invalid game_id format"}, room=sid)
                return

            db = SessionLocal()
            try:
                participant = db.query(GameParticipant).filter(
                    GameParticipant.game_id == game_id,
                    GameParticipant.user_id == user_id
                ).first()

                if not participant:
                    await sio.emit("error", {"message": "Not a participant"}, room=sid)
                    return

                user = get_user_from_db(user_id)
                username = user.username if user else "Unknown"

                await sio.emit("game:chat_message", {
                    "id": str(uuid.uuid4()),
                    "user_id": str(user_id),
                    "username": username,
                    "message": message,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "is_ooc": is_ooc,
                }, room=f"game:{game_id}")

                logger.info(f"User {username} sent {'OOC' if is_ooc else 'IC'} message in game {game_id}")

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error in game_send_message for sid {sid}: {e}", exc_info=True)
            await sio.emit("error", {"message": "Internal server error"}, room=sid)
