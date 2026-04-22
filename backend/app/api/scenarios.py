import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.orm import Session
from uuid import UUID

from ..database import get_db
from ..middleware.auth import get_current_user
from ..models.user import User
from ..schemas.scenario import (
    ScenarioCreate, ScenarioUpdate, ScenarioResponse, ScenarioListItem,
    ScenarioNPCCreate, ScenarioNPCUpdate, ScenarioNPCResponse,
    ScenarioHiddenItemCreate, ScenarioHiddenItemUpdate, ScenarioHiddenItemResponse,
)
from ..schemas.game import GameResponse
from ..services.scenario_service import (
    create_scenario, list_scenarios, get_scenario, update_scenario, delete_scenario,
    add_npc, update_npc, delete_npc,
    add_hidden_item, update_hidden_item, delete_hidden_item,
    launch_scenario,
)

router = APIRouter(prefix="/api/scenarios", tags=["scenarios"])

SCENARIO_MAPS_DIR = "uploads/scenario-maps"
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_FILE_SIZE = 10 * 1024 * 1024


@router.get("", response_model=list[ScenarioListItem])
async def list_scenarios_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scenarios = list_scenarios(db, current_user.id)
    result = []
    for s in scenarios:
        result.append(ScenarioListItem(
            id=s.id,
            owner_id=s.owner_id,
            name=s.name,
            story=s.story,
            map_url=s.map_url,
            created_at=s.created_at,
            npc_count=len(s.npcs),
            item_count=len(s.items),
        ))
    return result


@router.post("", response_model=ScenarioResponse, status_code=status.HTTP_201_CREATED)
async def create_scenario_endpoint(
    data: ScenarioCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ScenarioResponse.model_validate(create_scenario(db, data, current_user.id))


@router.get("/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario_endpoint(
    scenario_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ScenarioResponse.model_validate(get_scenario(db, scenario_id, current_user.id))


@router.put("/{scenario_id}", response_model=ScenarioResponse)
async def update_scenario_endpoint(
    scenario_id: UUID,
    data: ScenarioUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ScenarioResponse.model_validate(update_scenario(db, scenario_id, data, current_user.id))


@router.delete("/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scenario_endpoint(
    scenario_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    delete_scenario(db, scenario_id, current_user.id)


@router.post("/{scenario_id}/upload-map")
async def upload_scenario_map(
    scenario_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scenario = get_scenario(db, scenario_id, current_user.id)

    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")

    os.makedirs(SCENARIO_MAPS_DIR, exist_ok=True)
    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "png"
    filename = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(SCENARIO_MAPS_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(content)

    map_url = f"/{file_path.replace(os.sep, '/')}"
    scenario.map_url = map_url
    db.commit()

    return {"map_url": map_url}


@router.post("/{scenario_id}/launch", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
async def launch_scenario_endpoint(
    scenario_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    game = launch_scenario(db, scenario_id, current_user.id)
    return GameResponse.model_validate(game)


@router.post("/{scenario_id}/npcs", response_model=ScenarioNPCResponse, status_code=status.HTTP_201_CREATED)
async def add_npc_endpoint(
    scenario_id: UUID,
    data: ScenarioNPCCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ScenarioNPCResponse.model_validate(add_npc(db, scenario_id, data, current_user.id))


@router.put("/{scenario_id}/npcs/{npc_id}", response_model=ScenarioNPCResponse)
async def update_npc_endpoint(
    scenario_id: UUID,
    npc_id: UUID,
    data: ScenarioNPCUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ScenarioNPCResponse.model_validate(update_npc(db, npc_id, data, current_user.id))


@router.delete("/{scenario_id}/npcs/{npc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_npc_endpoint(
    scenario_id: UUID,
    npc_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    delete_npc(db, npc_id, current_user.id)


@router.post("/{scenario_id}/items", response_model=ScenarioHiddenItemResponse, status_code=status.HTTP_201_CREATED)
async def add_item_endpoint(
    scenario_id: UUID,
    data: ScenarioHiddenItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ScenarioHiddenItemResponse.model_validate(add_hidden_item(db, scenario_id, data, current_user.id))


@router.put("/{scenario_id}/items/{item_id}", response_model=ScenarioHiddenItemResponse)
async def update_item_endpoint(
    scenario_id: UUID,
    item_id: UUID,
    data: ScenarioHiddenItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ScenarioHiddenItemResponse.model_validate(update_hidden_item(db, item_id, data, current_user.id))


@router.delete("/{scenario_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item_endpoint(
    scenario_id: UUID,
    item_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    delete_hidden_item(db, item_id, current_user.id)
