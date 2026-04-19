from typing import List, Optional, Dict
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..models.character import Character
from ..models.spell import Spell
from ..models.character_spell import CharacterSpell, SpellSlotTracker

# PHB spell slot tables by class and character level
# Format: {class_name: {char_level: {spell_level: max_slots}}}
_FULL_CASTER_SLOTS = {
    1:  {1: 2},
    2:  {1: 3},
    3:  {1: 4, 2: 2},
    4:  {1: 4, 2: 3},
    5:  {1: 4, 2: 3, 3: 2},
    6:  {1: 4, 2: 3, 3: 3},
    7:  {1: 4, 2: 3, 3: 3, 4: 1},
    8:  {1: 4, 2: 3, 3: 3, 4: 2},
    9:  {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
    10: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
    11: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
    12: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
    13: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
    14: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
    15: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
    16: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
    17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1},
    18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 1, 7: 1, 8: 1, 9: 1},
    19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 1, 8: 1, 9: 1},
    20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 2, 8: 1, 9: 1},
}

_HALF_CASTER_SLOTS = {
    1:  {},
    2:  {1: 2},
    3:  {1: 3},
    4:  {1: 3},
    5:  {1: 4, 2: 2},
    6:  {1: 4, 2: 2},
    7:  {1: 4, 2: 3},
    8:  {1: 4, 2: 3},
    9:  {1: 4, 2: 3, 3: 2},
    10: {1: 4, 2: 3, 3: 2},
    11: {1: 4, 2: 3, 3: 3},
    12: {1: 4, 2: 3, 3: 3},
    13: {1: 4, 2: 3, 3: 3, 4: 1},
    14: {1: 4, 2: 3, 3: 3, 4: 1},
    15: {1: 4, 2: 3, 3: 3, 4: 2},
    16: {1: 4, 2: 3, 3: 3, 4: 2},
    17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
    18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
    19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
    20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
}

_WARLOCK_SLOTS = {
    1:  {1: 1}, 2: {1: 2}, 3: {2: 2}, 4: {2: 2},
    5:  {3: 2}, 6: {3: 2}, 7: {4: 2}, 8: {4: 2},
    9:  {5: 2}, 10: {5: 2}, 11: {5: 3}, 12: {5: 3},
    13: {5: 3}, 14: {5: 3}, 15: {5: 3}, 16: {5: 3},
    17: {5: 4}, 18: {5: 4}, 19: {5: 4}, 20: {5: 4},
}

_FULL_CASTERS = {
    "wizard", "маг", "cleric", "жрец", "druid", "друид",
    "bard", "бард", "sorcerer", "чародей",
}
_HALF_CASTERS = {"paladin", "паладин", "ranger", "следопыт"}
_WARLOCKS = {"warlock", "колдун"}

# Classes that recover slots on short rest (warlock pact magic)
_SHORT_REST_RECOVERY = {"warlock", "колдун"}


def _get_slot_table(char_class: str, level: int) -> Dict[int, int]:
    cls = char_class.lower()
    if cls in _WARLOCKS:
        return _WARLOCK_SLOTS.get(level, {})
    if cls in _FULL_CASTERS:
        return _FULL_CASTER_SLOTS.get(level, {})
    if cls in _HALF_CASTERS:
        return _HALF_CASTER_SLOTS.get(level, {})
    return {}


def initialize_spell_slots(db: Session, character: Character) -> List[SpellSlotTracker]:
    """Create or update spell slot trackers based on class and level."""
    slot_table = _get_slot_table(character.char_class, character.level)

    existing = {t.spell_level: t for t in db.query(SpellSlotTracker).filter(
        SpellSlotTracker.character_id == character.id
    ).all()}

    trackers = []
    for spell_level, max_slots in slot_table.items():
        if spell_level in existing:
            tracker = existing[spell_level]
            tracker.max_slots = max_slots
        else:
            tracker = SpellSlotTracker(
                character_id=character.id,
                spell_level=spell_level,
                max_slots=max_slots,
                used_slots=0,
            )
            db.add(tracker)
        trackers.append(tracker)

    # Remove slots for levels no longer available
    for lvl, tracker in existing.items():
        if lvl not in slot_table:
            db.delete(tracker)

    db.commit()
    return trackers


def get_spellbook(db: Session, character_id: UUID) -> dict:
    spells = db.query(CharacterSpell).filter(
        CharacterSpell.character_id == character_id
    ).all()
    slots = db.query(SpellSlotTracker).filter(
        SpellSlotTracker.character_id == character_id
    ).order_by(SpellSlotTracker.spell_level).all()

    return {
        "spells": [_spell_entry(s) for s in spells],
        "slots": [
            {
                "spell_level": t.spell_level,
                "max_slots": t.max_slots,
                "used_slots": t.used_slots,
                "available": t.max_slots - t.used_slots,
            }
            for t in slots
        ],
    }


def _spell_entry(cs: CharacterSpell) -> dict:
    spell = cs.spell
    return {
        "id": str(cs.id),
        "spell_id": str(cs.spell_id),
        "is_prepared": cs.is_prepared,
        "is_ritual": cs.is_ritual,
        "learned_at_level": cs.learned_at_level,
        "name": spell.name if spell else None,
        "level": spell.level if spell else None,
        "school": spell.school if spell else None,
        "concentration": spell.concentration if spell else False,
        "ritual": spell.ritual if spell else False,
        "casting_time": spell.casting_time if spell else None,
        "spell_range": spell.spell_range if spell else None,
        "components": spell.components if spell else None,
        "duration": spell.duration if spell else None,
        "description": spell.description if spell else None,
    }


def add_spell_to_spellbook(
    db: Session, character: Character, spell_id: UUID
) -> CharacterSpell:
    spell = db.query(Spell).filter(Spell.id == spell_id).first()
    if not spell:
        raise HTTPException(status_code=404, detail="Spell not found")

    existing = db.query(CharacterSpell).filter(
        CharacterSpell.character_id == character.id,
        CharacterSpell.spell_id == spell_id,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Spell already in spellbook")

    cs = CharacterSpell(
        character_id=character.id,
        spell_id=spell_id,
        is_prepared=spell.level == 0,  # Cantrips are always prepared
        is_ritual=spell.ritual,
        learned_at_level=character.level,
    )
    db.add(cs)
    db.commit()
    db.refresh(cs)
    return cs


def remove_spell_from_spellbook(
    db: Session, character_id: UUID, spell_id: UUID
) -> None:
    cs = db.query(CharacterSpell).filter(
        CharacterSpell.character_id == character_id,
        CharacterSpell.spell_id == spell_id,
    ).first()
    if not cs:
        raise HTTPException(status_code=404, detail="Spell not in spellbook")
    db.delete(cs)
    db.commit()


def prepare_spell(
    db: Session, character_id: UUID, spell_id: UUID, is_prepared: bool
) -> CharacterSpell:
    cs = db.query(CharacterSpell).filter(
        CharacterSpell.character_id == character_id,
        CharacterSpell.spell_id == spell_id,
    ).first()
    if not cs:
        raise HTTPException(status_code=404, detail="Spell not in spellbook")
    cs.is_prepared = is_prepared
    db.commit()
    db.refresh(cs)
    return cs


def use_spell_slot(db: Session, character_id: UUID, spell_level: int) -> SpellSlotTracker:
    tracker = db.query(SpellSlotTracker).filter(
        SpellSlotTracker.character_id == character_id,
        SpellSlotTracker.spell_level == spell_level,
    ).first()
    if not tracker:
        raise HTTPException(status_code=404, detail=f"No spell slots of level {spell_level}")
    if tracker.used_slots >= tracker.max_slots:
        raise HTTPException(status_code=400, detail=f"No available spell slots of level {spell_level}")
    tracker.used_slots += 1
    db.commit()
    db.refresh(tracker)
    return tracker


def recover_spell_slots(db: Session, character: Character, rest_type: str) -> List[SpellSlotTracker]:
    """Recover slots on rest. Warlock recovers on short rest; others on long rest only."""
    cls = character.char_class.lower()
    is_warlock = cls in _SHORT_REST_RECOVERY

    if rest_type == "short" and not is_warlock:
        return []  # Non-warlocks don't recover spell slots on short rest

    trackers = db.query(SpellSlotTracker).filter(
        SpellSlotTracker.character_id == character.id
    ).all()
    for t in trackers:
        t.used_slots = 0
    db.commit()
    return trackers
