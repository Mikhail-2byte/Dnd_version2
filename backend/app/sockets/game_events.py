from socketio import AsyncServer
from . import state as _state
from .state import connected_users, game_rooms
from .utils import get_user_from_token, get_game_state
from .emitters import (
    get_sio,
    emit_combat_started,
    emit_initiative_rolled,
    emit_combat_ended,
    emit_combat_attack,
    emit_combat_damage,
    emit_combat_heal,
    emit_participant_defeated,
    emit_master_transferred,
    emit_turn_changed,
)
from .handlers.connection import register_connection_handlers
from .handlers.token_handlers import register_token_handlers
from .handlers.dice_handlers import register_dice_handlers
from .handlers.participant_handlers import register_participant_handlers


def register_socket_handlers(sio: AsyncServer):
    """Регистрация обработчиков Socket.IO событий"""
    _state._sio_instance = sio

    register_connection_handlers(sio)
    register_token_handlers(sio)
    register_dice_handlers(sio)
    register_participant_handlers(sio)


__all__ = [
    "register_socket_handlers",
    "connected_users",
    "game_rooms",
    "get_user_from_token",
    "get_game_state",
    "get_sio",
    "emit_combat_started",
    "emit_initiative_rolled",
    "emit_combat_ended",
    "emit_combat_attack",
    "emit_combat_damage",
    "emit_combat_heal",
    "emit_participant_defeated",
    "emit_master_transferred",
    "emit_turn_changed",
]
