import logging
from typing import Optional
from uuid import UUID
from socketio import AsyncServer
from . import state

logger = logging.getLogger(__name__)


def get_sio() -> Optional[AsyncServer]:
    """Получение экземпляра socketio сервера"""
    return state._sio_instance


async def emit_combat_started(game_id: UUID, combat_data: dict):
    """Эмиссия события начала боя"""
    if state._sio_instance:
        room_name = str(game_id)
        await state._sio_instance.emit("combat:started", combat_data, room=room_name)
        logger.info(f"Emitted combat:started for game {game_id}")


async def emit_initiative_rolled(game_id: UUID, participant_data: dict):
    """Эмиссия события броска инициативы"""
    if state._sio_instance:
        room_name = f"game:{game_id}"
        await state._sio_instance.emit("combat:initiative_rolled", participant_data, room=room_name)
        logger.info(f"Emitted combat:initiative_rolled for game {game_id}")


async def emit_combat_ended(game_id: UUID):
    """Эмиссия события завершения боя"""
    if state._sio_instance:
        room_name = f"game:{game_id}"
        await state._sio_instance.emit("combat:ended", {}, room=room_name)
        logger.info(f"Emitted combat:ended for game {game_id}")


async def emit_combat_attack(game_id: UUID, attack_data: dict):
    """Эмиссия события атаки"""
    if state._sio_instance:
        room_name = f"game:{game_id}"
        await state._sio_instance.emit("combat:attack", attack_data, room=room_name)
        logger.info(f"Emitted combat:attack for game {game_id}")


async def emit_combat_damage(game_id: UUID, damage_data: dict):
    """Эмиссия события нанесения урона"""
    if state._sio_instance:
        room_name = f"game:{game_id}"
        await state._sio_instance.emit("combat:damage", damage_data, room=room_name)
        logger.info(f"Emitted combat:damage for game {game_id}")


async def emit_combat_heal(game_id: UUID, heal_data: dict):
    """Эмиссия события исцеления"""
    if state._sio_instance:
        room_name = f"game:{game_id}"
        await state._sio_instance.emit("combat:heal", heal_data, room=room_name)
        logger.info(f"Emitted combat:heal for game {game_id}")


async def emit_participant_defeated(game_id: UUID, participant_id: UUID):
    """Эмиссия события поверженного участника"""
    if state._sio_instance:
        room_name = f"game:{game_id}"
        await state._sio_instance.emit("combat:participant_defeated", {
            "participant_id": str(participant_id)
        }, room=room_name)
        logger.info(f"Emitted combat:participant_defeated for participant {participant_id} in game {game_id}")


async def emit_master_transferred(game_id: UUID, old_master_id: UUID, new_master_id: UUID):
    """Отправка WebSocket события о смене мастера"""
    if state._sio_instance:
        await state._sio_instance.emit("master:transferred", {
            "game_id": str(game_id),
            "old_master_id": str(old_master_id),
            "new_master_id": str(new_master_id)
        }, room=f"game:{game_id}")



async def emit_turn_changed(game_id: UUID, combat_data: dict):
    """Emit turn change event to all players in the game."""
    if state._sio_instance:
        await state._sio_instance.emit("combat:turn_changed", combat_data, room=f"game:{game_id}")


async def emit_token_revealed(game_id: UUID, token_data: dict):
    """Мастер раскрыл скрытый токен — уведомить всех игроков в комнате"""
    if state._sio_instance:
        await state._sio_instance.emit("token:revealed", token_data, room=f"game:{game_id}")
        logger.info(f"Emitted token:revealed for game {game_id}, token {token_data.get('token_id')}")
