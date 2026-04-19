import logging
from uuid import UUID
from ...database import SessionLocal
from ...models.game_participant import GameParticipant
from ..state import connected_users
from ..utils import get_user_from_db

logger = logging.getLogger(__name__)


def register_dice_handlers(sio):
    @sio.event
    async def dice_roll(sid, data):
        """Бросок кубиков"""
        try:
            if sid not in connected_users:
                logger.warning(f"Unauthenticated dice_roll attempt: {sid}")
                return

            user_id = connected_users[sid]

            if not data or not isinstance(data, dict):
                logger.warning(f"Invalid data format for dice_roll: {sid}")
                await sio.emit("error", {"message": "Invalid data format"}, room=sid)
                return

            try:
                game_id = UUID(data.get("game_id"))
                count = int(data.get("count", 1))
                faces = int(data.get("faces", 20))
                advantage = data.get("advantage")
                if advantage is not None:
                    advantage = bool(advantage)
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid dice_roll data: {e}")
                await sio.emit("error", {"message": "Invalid dice_roll data"}, room=sid)
                return

            if count < 1 or count > 10:
                logger.warning(f"Invalid dice count: {count}")
                await sio.emit("error", {"message": "Dice count must be between 1 and 10"}, room=sid)
                return

            if faces not in [4, 6, 8, 10, 12, 20]:
                logger.warning(f"Invalid dice faces: {faces}")
                await sio.emit("error", {"message": "Invalid dice faces. Allowed: 4, 6, 8, 10, 12, 20"}, room=sid)
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

                from ...services.dice_service import DiceRoller, save_roll_history
                dice_roller = DiceRoller(default_faces=12, max_dice=10)
                try:
                    result = dice_roller.roll(count, faces, advantage)
                    result_dict = dice_roller.to_dict(result)
                except ValueError as e:
                    logger.warning(f"Dice roll validation error: {e}")
                    await sio.emit("error", {"message": str(e)}, room=sid)
                    return

                roll_type = data.get("roll_type")
                modifier = data.get("modifier")
                if modifier is not None:
                    modifier = int(modifier)
                    result_dict["total"] = result_dict["total"] + modifier

                try:
                    save_roll_history(
                        db=db,
                        game_id=game_id,
                        user_id=user_id,
                        count=count,
                        faces=faces,
                        rolls=result_dict["rolls"],
                        total=result_dict["total"],
                        roll_type=roll_type,
                        modifier=modifier,
                        advantage_type=result_dict.get("advantage_type"),
                        advantage_rolls=result_dict.get("advantage_rolls"),
                        selected_roll=result_dict.get("selected_roll")
                    )
                except Exception as e:
                    logger.error(f"Error saving dice roll history: {e}", exc_info=True)

                user = get_user_from_db(user_id)
                username = user.username if user else "Unknown"

                logger.info(f"User {username} ({user_id}) rolled {count}d{faces} = {result_dict['total']} (modifier: {modifier}) in game {game_id}")

                await sio.emit("dice:rolled", {
                    "game_id": str(game_id),
                    "user_id": str(user_id),
                    "username": username,
                    "count": count,
                    "faces": faces,
                    "rolls": result_dict["rolls"],
                    "total": result_dict["total"],
                    "roll_type": roll_type,
                    "modifier": modifier,
                    "advantage_type": result_dict.get("advantage_type"),
                    "advantage_rolls": result_dict.get("advantage_rolls"),
                    "selected_roll": result_dict.get("selected_roll")
                }, room=f"game:{game_id}")

            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error in dice_roll for sid {sid}: {e}", exc_info=True)
            await sio.emit("error", {"message": "Internal server error"}, room=sid)
