import logging
from uuid import UUID
from ...database import SessionLocal
from ...models.game_participant import GameParticipant
from ...services.game_service import get_game_by_id, is_master, set_participant_ready, set_participant_character
from ..state import connected_users, game_rooms, started_games
from ..utils import get_user_from_db, get_game_state

logger = logging.getLogger(__name__)


def register_participant_handlers(sio):
    @sio.event
    async def game_join(sid, data):
        """Подключение к игре"""
        try:
            if sid not in connected_users:
                logger.warning(f"Unauthenticated connection attempt: {sid}")
                await sio.emit("error", {"message": "Not authenticated"}, room=sid)
                return

            user_id = connected_users[sid]

            if not data or not isinstance(data, dict):
                logger.warning(f"Invalid data format for game_join: {sid}")
                await sio.emit("error", {"message": "Invalid data format"}, room=sid)
                return

            game_id_str = data.get("game_id")
            if not game_id_str:
                logger.warning(f"Missing game_id in game_join: {sid}")
                await sio.emit("error", {"message": "Missing game_id"}, room=sid)
                return

            try:
                game_id = UUID(game_id_str)
            except (ValueError, TypeError):
                logger.warning(f"Invalid game_id format: {game_id_str}")
                await sio.emit("error", {"message": "Invalid game_id format"}, room=sid)
                return

            db = SessionLocal()
            try:
                get_game_by_id(db, game_id)
                logger.info(f"User {user_id} joining game {game_id}")

                participant = db.query(GameParticipant).filter(
                    GameParticipant.game_id == game_id,
                    GameParticipant.user_id == user_id
                ).first()

                if not participant:
                    logger.warning(f"User {user_id} is not a participant of game {game_id}")
                    await sio.emit("error", {"message": "Not a participant"}, room=sid)
                    return

                if game_id not in game_rooms:
                    game_rooms[game_id] = set()
                game_rooms[game_id].add(sid)
                await sio.enter_room(sid, f"game:{game_id}")

                game_state = get_game_state(db, game_id)
                await sio.emit("game:state", game_state, room=sid)

                user = get_user_from_db(user_id)
                if user:
                    await sio.emit("player:joined", {
                        "user_id": str(user_id),
                        "username": user.username
                    }, room=f"game:{game_id}", skip_sid=sid)
                    logger.info(f"User {user.username} ({user_id}) joined game {game_id}")

            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error in game_join for sid {sid}: {e}", exc_info=True)
            await sio.emit("error", {"message": "Internal server error"}, room=sid)

    @sio.event
    async def participant_ready(sid, data):
        """Установка статуса готовности участника"""
        try:
            if sid not in connected_users:
                logger.warning(f"Unauthenticated participant_ready attempt: {sid}")
                return

            user_id = connected_users[sid]

            if not data or not isinstance(data, dict):
                logger.warning(f"Invalid data format for participant_ready: {sid}")
                await sio.emit("error", {"message": "Invalid data format"}, room=sid)
                return

            try:
                game_id = UUID(data.get("game_id"))
                is_ready = bool(data.get("is_ready", False))
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid participant_ready data: {e}")
                await sio.emit("error", {"message": "Invalid participant_ready data"}, room=sid)
                return

            db = SessionLocal()
            try:
                participant = db.query(GameParticipant).filter(
                    GameParticipant.game_id == game_id,
                    GameParticipant.user_id == user_id
                ).first()

                if not participant:
                    logger.warning(f"User {user_id} is not a participant of game {game_id}")
                    await sio.emit("error", {"message": "Not a participant"}, room=sid)
                    return

                set_participant_ready(db, game_id, user_id, is_ready)
                logger.info(f"User {user_id} set ready status to {is_ready} in game {game_id}")

                user = get_user_from_db(user_id)
                username = user.username if user else "Unknown"

                await sio.emit("participant:ready_changed", {
                    "user_id": str(user_id),
                    "username": username,
                    "is_ready": is_ready
                }, room=f"game:{game_id}")

            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error in participant_ready for sid {sid}: {e}", exc_info=True)
            await sio.emit("error", {"message": "Internal server error"}, room=sid)

    @sio.event
    async def scene_description(sid, data):
        """
        Отправка описания сцены мастером всем игрокам

        Данные:
        - game_id: UUID игры
        - description: str - описание сцены
        - title: str (опционально) - заголовок сцены
        """
        try:
            if sid not in connected_users:
                logger.warning(f"Unauthenticated scene_description attempt: {sid}")
                await sio.emit("error", {"message": "Not authenticated"}, room=sid)
                return

            user_id = connected_users[sid]

            try:
                game_id = UUID(data.get("game_id"))
                description = data.get("description", "").strip()
                title = data.get("title", "").strip() or None
            except (ValueError, TypeError, AttributeError):
                await sio.emit("error", {"message": "Invalid data format"}, room=sid)
                return

            if not description:
                await sio.emit("error", {"message": "Description is required"}, room=sid)
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

                if not is_master(db, game_id, user_id):
                    await sio.emit("error", {"message": "Only master can send scene descriptions"}, room=sid)
                    return

                await sio.emit("scene:description_received", {
                    "game_id": str(game_id),
                    "user_id": str(user_id),
                    "description": description,
                    "title": title
                }, room=f"game:{game_id}")

                logger.info(f"Master {user_id} sent scene description to game {game_id}")

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error in scene_description handler: {e}", exc_info=True)
            await sio.emit("error", {"message": "Internal server error"}, room=sid)

    @sio.event
    async def game_start(sid, data):
        """Мастер запускает игру — все игроки в комнате получают событие game:started"""
        try:
            if sid not in connected_users:
                await sio.emit("error", {"message": "Not authenticated"}, room=sid)
                return

            user_id = connected_users[sid]

            try:
                game_id = UUID(data.get("game_id"))
            except (ValueError, TypeError):
                await sio.emit("error", {"message": "Invalid game_id"}, room=sid)
                return

            db = SessionLocal()
            try:
                if not is_master(db, game_id, user_id):
                    await sio.emit("error", {"message": "Only master can start the game"}, room=sid)
                    return

                started_games.add(game_id)
                await sio.emit("game:started", {"game_id": str(game_id)}, room=f"game:{game_id}")
                logger.info(f"Master {user_id} started game {game_id}")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error in game_start for sid {sid}: {e}", exc_info=True)
            await sio.emit("error", {"message": "Internal server error"}, room=sid)

    @sio.event
    async def participant_character(sid, data):
        """Установка выбранного персонажа участника"""
        try:
            if sid not in connected_users:
                logger.warning(f"Unauthenticated participant_character attempt: {sid}")
                return

            user_id = connected_users[sid]

            if not data or not isinstance(data, dict):
                logger.warning(f"Invalid data format for participant_character: {sid}")
                await sio.emit("error", {"message": "Invalid data format"}, room=sid)
                return

            try:
                game_id = UUID(data.get("game_id"))
                character_id_str = data.get("character_id")
                character_id = UUID(character_id_str) if character_id_str else None
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid participant_character data: {e}")
                await sio.emit("error", {"message": "Invalid participant_character data"}, room=sid)
                return

            db = SessionLocal()
            try:
                participant = db.query(GameParticipant).filter(
                    GameParticipant.game_id == game_id,
                    GameParticipant.user_id == user_id
                ).first()

                if not participant:
                    logger.warning(f"User {user_id} is not a participant of game {game_id}")
                    await sio.emit("error", {"message": "Not a participant"}, room=sid)
                    return

                set_participant_character(db, game_id, user_id, character_id)
                logger.info(f"User {user_id} set character {character_id} in game {game_id}")

                user = get_user_from_db(user_id)
                username = user.username if user else "Unknown"

                await sio.emit("participant:character_changed", {
                    "user_id": str(user_id),
                    "username": username,
                    "character_id": str(character_id) if character_id else None
                }, room=f"game:{game_id}")

            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error in participant_character for sid {sid}: {e}", exc_info=True)
            await sio.emit("error", {"message": "Internal server error"}, room=sid)
