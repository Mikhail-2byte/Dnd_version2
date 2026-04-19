import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..models.race import Race, SubRace
from ..models.background import Background
from ..models.class_feature import ClassFeature
from ..models.spell import Spell
from ..models.item import Weapon, Armor
from ..models.monster import Monster, MonsterAction

logger = logging.getLogger(__name__)


def get_all_races(db: Session) -> List[Race]:
    return db.query(Race).order_by(Race.name).all()


def get_race_by_slug(db: Session, slug: str) -> Race:
    race = db.query(Race).filter(Race.slug == slug).first()
    if not race:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Race '{slug}' not found")
    return race


def get_all_backgrounds(db: Session) -> List[Background]:
    return db.query(Background).order_by(Background.name).all()


def get_background_by_slug(db: Session, slug: str) -> Background:
    bg = db.query(Background).filter(Background.slug == slug).first()
    if not bg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Background '{slug}' not found")
    return bg


def get_class_features(db: Session, class_slug: str, level: Optional[int] = None) -> List[ClassFeature]:
    q = db.query(ClassFeature).filter(ClassFeature.class_slug == class_slug)
    if level is not None:
        q = q.filter(ClassFeature.level == level)
    return q.order_by(ClassFeature.level, ClassFeature.feature_name).all()


def get_spells(
    db: Session,
    level: Optional[int] = None,
    school: Optional[str] = None,
    class_slug: Optional[str] = None,
) -> List[Spell]:
    q = db.query(Spell)
    if level is not None:
        q = q.filter(Spell.level == level)
    if school:
        q = q.filter(Spell.school.ilike(school))
    if class_slug:
        q = q.filter(Spell.classes.contains([class_slug]))
    return q.order_by(Spell.level, Spell.name).all()


def get_spell_by_slug(db: Session, slug: str) -> Spell:
    spell = db.query(Spell).filter(Spell.slug == slug).first()
    if not spell:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Spell '{slug}' not found")
    return spell


def get_weapons(db: Session, category: Optional[str] = None) -> List[Weapon]:
    q = db.query(Weapon)
    if category:
        q = q.filter(Weapon.category == category)
    return q.order_by(Weapon.category, Weapon.name).all()


def get_armors(db: Session, category: Optional[str] = None) -> List[Armor]:
    q = db.query(Armor)
    if category:
        q = q.filter(Armor.category == category)
    return q.order_by(Armor.category, Armor.name).all()


def get_monsters(
    db: Session,
    name: Optional[str] = None,
    monster_type: Optional[str] = None,
    cr_min: Optional[float] = None,
    cr_max: Optional[float] = None,
) -> List[Monster]:
    q = db.query(Monster)
    if name:
        q = q.filter(Monster.name.ilike(f"%{name}%"))
    if monster_type:
        q = q.filter(Monster.monster_type.ilike(monster_type))
    if cr_min is not None:
        q = q.filter(Monster.cr >= cr_min)
    if cr_max is not None:
        q = q.filter(Monster.cr <= cr_max)
    return q.order_by(Monster.cr, Monster.name).all()


def get_monster_by_slug(db: Session, slug: str) -> Monster:
    monster = db.query(Monster).filter(Monster.slug == slug).first()
    if not monster:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Monster '{slug}' not found")
    return monster
