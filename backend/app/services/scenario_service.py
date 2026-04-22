from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from uuid import UUID

from ..models.scenario import Scenario, ScenarioNPC, ScenarioHiddenItem
from ..models.token import Token
from ..models.game_session import GameSession
from ..models.game_participant import GameParticipant
from ..schemas.scenario import ScenarioCreate, ScenarioUpdate, ScenarioNPCCreate, ScenarioNPCUpdate, ScenarioHiddenItemCreate, ScenarioHiddenItemUpdate
from .game_service import generate_invite_code


def _require_owner(scenario: Scenario | None, owner_id: UUID) -> Scenario:
    if not scenario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
    if scenario.owner_id != owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your scenario")
    return scenario


def create_scenario(db: Session, data: ScenarioCreate, owner_id: UUID) -> Scenario:
    scenario = Scenario(
        owner_id=owner_id,
        name=data.name,
        story=data.story,
        map_url=data.map_url,
    )
    db.add(scenario)
    db.commit()
    db.refresh(scenario)
    return scenario


def list_scenarios(db: Session, owner_id: UUID) -> list[Scenario]:
    return db.query(Scenario).filter(Scenario.owner_id == owner_id).order_by(Scenario.created_at.desc()).all()


def get_scenario(db: Session, scenario_id: UUID, owner_id: UUID) -> Scenario:
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    return _require_owner(scenario, owner_id)


def update_scenario(db: Session, scenario_id: UUID, data: ScenarioUpdate, owner_id: UUID) -> Scenario:
    scenario = get_scenario(db, scenario_id, owner_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(scenario, field, value)
    db.commit()
    db.refresh(scenario)
    return scenario


def delete_scenario(db: Session, scenario_id: UUID, owner_id: UUID) -> None:
    scenario = get_scenario(db, scenario_id, owner_id)
    db.delete(scenario)
    db.commit()


def add_npc(db: Session, scenario_id: UUID, data: ScenarioNPCCreate, owner_id: UUID) -> ScenarioNPC:
    get_scenario(db, scenario_id, owner_id)
    loot_data = [e.model_dump() for e in data.loot] if data.loot else None
    # Convert UUIDs to strings in loot for JSON serialization
    if loot_data:
        for entry in loot_data:
            if 'item_id' in entry and entry['item_id']:
                entry['item_id'] = str(entry['item_id'])
    npc = ScenarioNPC(
        scenario_id=scenario_id,
        name=data.name,
        x=data.x,
        y=data.y,
        image_url=data.image_url,
        is_hidden=data.is_hidden,
        monster_slug=data.monster_slug,
        loot=loot_data,
        notes=data.notes,
    )
    db.add(npc)
    db.commit()
    db.refresh(npc)
    return npc


def update_npc(db: Session, npc_id: UUID, data: ScenarioNPCUpdate, owner_id: UUID) -> ScenarioNPC:
    npc = db.query(ScenarioNPC).filter(ScenarioNPC.id == npc_id).first()
    if not npc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NPC not found")
    get_scenario(db, npc.scenario_id, owner_id)
    updates = data.model_dump(exclude_unset=True)
    if 'loot' in updates and updates['loot'] is not None:
        loot_data = [e.model_dump() for e in updates['loot']]
        for entry in loot_data:
            if 'item_id' in entry and entry['item_id']:
                entry['item_id'] = str(entry['item_id'])
        updates['loot'] = loot_data
    for field, value in updates.items():
        setattr(npc, field, value)
    db.commit()
    db.refresh(npc)
    return npc


def delete_npc(db: Session, npc_id: UUID, owner_id: UUID) -> None:
    npc = db.query(ScenarioNPC).filter(ScenarioNPC.id == npc_id).first()
    if not npc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NPC not found")
    get_scenario(db, npc.scenario_id, owner_id)
    db.delete(npc)
    db.commit()


def add_hidden_item(db: Session, scenario_id: UUID, data: ScenarioHiddenItemCreate, owner_id: UUID) -> ScenarioHiddenItem:
    get_scenario(db, scenario_id, owner_id)
    item = ScenarioHiddenItem(
        scenario_id=scenario_id,
        name=data.name,
        x=data.x,
        y=data.y,
        image_url=data.image_url,
        item_type=data.item_type,
        item_id=data.item_id,
        quantity=data.quantity,
        notes=data.notes,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_hidden_item(db: Session, item_id: UUID, data: ScenarioHiddenItemUpdate, owner_id: UUID) -> ScenarioHiddenItem:
    item = db.query(ScenarioHiddenItem).filter(ScenarioHiddenItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    get_scenario(db, item.scenario_id, owner_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


def delete_hidden_item(db: Session, item_id: UUID, owner_id: UUID) -> None:
    item = db.query(ScenarioHiddenItem).filter(ScenarioHiddenItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    get_scenario(db, item.scenario_id, owner_id)
    db.delete(item)
    db.commit()


def launch_scenario(db: Session, scenario_id: UUID, owner_id: UUID) -> GameSession:
    scenario = get_scenario(db, scenario_id, owner_id)

    invite_code = generate_invite_code()
    while db.query(GameSession).filter(GameSession.invite_code == invite_code).first():
        invite_code = generate_invite_code()

    game = GameSession(
        name=scenario.name,
        invite_code=invite_code,
        master_id=owner_id,
        story=scenario.story,
        map_url=scenario.map_url,
    )
    db.add(game)
    db.flush()

    participant = GameParticipant(game_id=game.id, user_id=owner_id, role="master")
    db.add(participant)

    for npc in scenario.npcs:
        loot_data = npc.loot if npc.loot else None
        token = Token(
            game_id=game.id,
            name=npc.name,
            x=npc.x,
            y=npc.y,
            image_url=npc.image_url,
            is_hidden=npc.is_hidden,
            token_type='npc',
            token_metadata={'monster_slug': npc.monster_slug, 'loot': loot_data, 'notes': npc.notes},
        )
        db.add(token)

    for hidden_item in scenario.items:
        token = Token(
            game_id=game.id,
            name=hidden_item.name,
            x=hidden_item.x,
            y=hidden_item.y,
            image_url=hidden_item.image_url,
            is_hidden=True,
            token_type='item',
            token_metadata={
                'item_type': hidden_item.item_type,
                'item_id': str(hidden_item.item_id) if hidden_item.item_id else None,
                'quantity': hidden_item.quantity,
                'notes': hidden_item.notes,
            },
        )
        db.add(token)

    db.commit()
    db.refresh(game)
    return game
