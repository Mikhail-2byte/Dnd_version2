from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..schemas.game_data import (
    RaceResponse, BackgroundResponse, ClassFeatureResponse,
    SpellResponse, WeaponResponse, ArmorResponse,
    MonsterResponse, MonsterListResponse,
)
from ..services.game_data_service import (
    get_all_races, get_race_by_slug,
    get_all_backgrounds, get_background_by_slug,
    get_class_features,
    get_spells, get_spell_by_slug,
    get_weapons, get_armors,
    get_monsters, get_monster_by_slug,
)

router = APIRouter(prefix="/api/data", tags=["game-data"])


@router.get("/races", response_model=List[RaceResponse])
async def list_races(db: Session = Depends(get_db)):
    return get_all_races(db)


@router.get("/races/{slug}", response_model=RaceResponse)
async def get_race(slug: str, db: Session = Depends(get_db)):
    return get_race_by_slug(db, slug)


@router.get("/backgrounds", response_model=List[BackgroundResponse])
async def list_backgrounds(db: Session = Depends(get_db)):
    return get_all_backgrounds(db)


@router.get("/backgrounds/{slug}", response_model=BackgroundResponse)
async def get_background(slug: str, db: Session = Depends(get_db)):
    return get_background_by_slug(db, slug)


@router.get("/classes/{class_slug}/features", response_model=List[ClassFeatureResponse])
async def list_class_features(
    class_slug: str,
    level: Optional[int] = Query(None, ge=1, le=20),
    db: Session = Depends(get_db),
):
    return get_class_features(db, class_slug, level)


@router.get("/spells", response_model=List[SpellResponse])
async def list_spells(
    level: Optional[int] = Query(None, ge=0, le=9),
    school: Optional[str] = None,
    char_class: Optional[str] = Query(None, alias="class"),
    db: Session = Depends(get_db),
):
    return get_spells(db, level, school, char_class)


@router.get("/spells/{slug}", response_model=SpellResponse)
async def get_spell(slug: str, db: Session = Depends(get_db)):
    return get_spell_by_slug(db, slug)


@router.get("/weapons", response_model=List[WeaponResponse])
async def list_weapons(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return get_weapons(db, category)


@router.get("/armors", response_model=List[ArmorResponse])
async def list_armors(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return get_armors(db, category)


@router.get("/monsters", response_model=List[MonsterListResponse])
async def list_monsters(
    name: Optional[str] = None,
    type: Optional[str] = None,
    cr_min: Optional[float] = Query(None, alias="cr_min"),
    cr_max: Optional[float] = Query(None, alias="cr_max"),
    db: Session = Depends(get_db),
):
    return get_monsters(db, name, type, cr_min, cr_max)


@router.get("/monsters/{slug}", response_model=MonsterResponse)
async def get_monster(slug: str, db: Session = Depends(get_db)):
    return get_monster_by_slug(db, slug)
