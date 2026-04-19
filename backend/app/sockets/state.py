from typing import Dict, Set
from uuid import UUID

connected_users: Dict[str, UUID] = {}
game_rooms: Dict[UUID, set] = {}
started_games: Set[UUID] = set()
_sio_instance = None
