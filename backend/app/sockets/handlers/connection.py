import logging
from ..state import connected_users, game_rooms
from ..utils import get_user_from_token

logger = logging.getLogger(__name__)


def register_connection_handlers(sio):
    @sio.event
    async def connect(sid, environ, auth):
        """Обработка подключения"""
        try:
            token = None
            if auth and isinstance(auth, dict):
                token = auth.get("token")
            elif environ.get("QUERY_STRING"):
                query_string = environ["QUERY_STRING"]
                params = dict(param.split("=") for param in query_string.split("&") if "=" in param)
                token = params.get("token")

            if not token:
                logger.warning(f"Connection attempt without token: {sid}")
                return False

            user_id = get_user_from_token(token)
            if not user_id:
                logger.warning(f"Invalid token for connection: {sid}")
                return False

            connected_users[sid] = user_id
            logger.info(f"User {user_id} connected with socket {sid}")
            return True
        except Exception as e:
            logger.error(f"Error in connect for sid {sid}: {e}", exc_info=True)
            return False

    @sio.event
    async def disconnect(sid):
        """Обработка отключения"""
        try:
            user_id = connected_users.pop(sid, None)
            if user_id:
                logger.info(f"User {user_id} disconnected (socket {sid})")

            for game_id, socket_ids in list(game_rooms.items()):
                socket_ids.discard(sid)
                if not socket_ids:
                    game_rooms.pop(game_id, None)
                    logger.debug(f"Game room {game_id} is now empty")
        except Exception as e:
            logger.error(f"Error in disconnect for sid {sid}: {e}", exc_info=True)
