"""
Тесты для API игровых данных (расы, предыстории, классы, заклинания, оружие, броня).
"""
import pytest
import uuid
from tests.conftest import (
    db_session, client,
    Race, SubRace, Background, ClassFeature, Spell, Weapon, Armor,
    TestingSessionLocal,
)


# ─────────────────────── фикстуры данных ───────────────────────

@pytest.fixture
def sample_race(db_session):
    race = Race(
        id=uuid.uuid4(), slug="human", name="Человек", name_en="Human",
        source="PHB", speed=30, size="Medium", darkvision=0,
        ability_bonuses={"str": 1, "dex": 1},
        traits=[{"name": "Универсальность", "description": "Бонус к навыку."}],
        languages=["Общий"],
        description="Самая распространённая раса.",
    )
    db_session.add(race)
    db_session.commit()
    db_session.refresh(race)
    return race


@pytest.fixture
def sample_subrace(db_session, sample_race):
    subrace = SubRace(
        id=uuid.uuid4(), slug="high-elf", name="Высший эльф", name_en="High Elf",
        race_id=sample_race.id, ability_bonuses={"int": 1}, darkvision=60,
        traits=[{"name": "Заговор", "description": "Знает один заговор."}],
    )
    db_session.add(subrace)
    db_session.commit()
    db_session.refresh(subrace)
    return subrace


@pytest.fixture
def sample_background(db_session):
    bg = Background(
        id=uuid.uuid4(), slug="acolyte", name="Послушник", name_en="Acolyte",
        source="PHB",
        skill_proficiencies=["Проницательность", "Религия"],
        tool_proficiencies=[],
        languages=2,
        equipment=["Священный символ", "Молитвенная книга"],
        feature_name="Приют веры",
        feature_description="Храмы вашей веры предоставляют вам кров и еду.",
        description="Вы провели годы в служении храму.",
    )
    db_session.add(bg)
    db_session.commit()
    db_session.refresh(bg)
    return bg


@pytest.fixture
def sample_class_feature(db_session):
    feat = ClassFeature(
        id=uuid.uuid4(), class_slug="barbarian", level=1,
        feature_name="Ярость", feature_description="Яростная атака 2 раза в день.",
        is_asi=False, feature_type="main", proficiency_bonus=2,
    )
    db_session.add(feat)
    db_session.commit()
    db_session.refresh(feat)
    return feat


@pytest.fixture
def sample_spell(db_session):
    spell = Spell(
        id=uuid.uuid4(), slug="fire-bolt", name="Огненный снаряд", name_en="Fire Bolt",
        level=0, school="Evocation", casting_time="1 действие", spell_range="120 футов",
        components={"v": True, "s": True}, duration="Мгновенная",
        concentration=False, ritual=False,
        description="Сгусток огня 1d10.",
        classes=["wizard", "sorcerer"],
    )
    db_session.add(spell)
    db_session.commit()
    db_session.refresh(spell)
    return spell


@pytest.fixture
def sample_weapon(db_session):
    weapon = Weapon(
        id=uuid.uuid4(), slug="longsword", name="Длинный меч", name_en="Longsword",
        category="Martial Melee", damage_dice="1d8", damage_type="Рубящий",
        properties=["Универсальное"], two_handed_damage="1d10",
        weight=1.5, cost_gp=15.0, ability="str",
    )
    db_session.add(weapon)
    db_session.commit()
    db_session.refresh(weapon)
    return weapon


@pytest.fixture
def sample_armor(db_session):
    armor = Armor(
        id=uuid.uuid4(), slug="leather", name="Кожаная броня", name_en="Leather Armor",
        category="Light", base_ac=11, dex_modifier="full",
        min_strength=0, stealth_disadvantage=False, weight=5.0, cost_gp=10.0,
    )
    db_session.add(armor)
    db_session.commit()
    db_session.refresh(armor)
    return armor


# ─────────────────────── тесты рас ───────────────────────

class TestRaces:
    def test_list_races_empty(self, client):
        response = client.get("/api/data/races")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_races(self, client, sample_race):
        response = client.get("/api/data/races")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["slug"] == "human"
        assert data[0]["name"] == "Человек"
        assert data[0]["speed"] == 30

    def test_get_race_by_slug(self, client, sample_race):
        response = client.get("/api/data/races/human")
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == "human"
        assert data["darkvision"] == 0

    def test_get_race_not_found(self, client):
        response = client.get("/api/data/races/unknown-race")
        assert response.status_code == 404

    def test_race_with_subraces(self, client, sample_race, sample_subrace):
        response = client.get("/api/data/races/human")
        assert response.status_code == 200
        data = response.json()
        assert len(data["subraces"]) == 1
        assert data["subraces"][0]["slug"] == "high-elf"


# ─────────────────────── тесты предысторий ───────────────────────

class TestBackgrounds:
    def test_list_backgrounds_empty(self, client):
        response = client.get("/api/data/backgrounds")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_backgrounds(self, client, sample_background):
        response = client.get("/api/data/backgrounds")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["slug"] == "acolyte"

    def test_get_background_by_slug(self, client, sample_background):
        response = client.get("/api/data/backgrounds/acolyte")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Послушник"
        assert "Проницательность" in data["skill_proficiencies"]

    def test_get_background_not_found(self, client):
        response = client.get("/api/data/backgrounds/nonexistent")
        assert response.status_code == 404


# ─────────────────────── тесты способностей классов ───────────────────────

class TestClassFeatures:
    def test_list_class_features(self, client, sample_class_feature):
        response = client.get("/api/data/classes/barbarian/features")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["feature_name"] == "Ярость"
        assert data[0]["level"] == 1

    def test_list_class_features_empty(self, client):
        response = client.get("/api/data/classes/wizard/features")
        assert response.status_code == 200
        assert response.json() == []

    def test_filter_by_level(self, client, db_session):
        for level in [1, 2, 3]:
            feat = ClassFeature(
                id=uuid.uuid4(), class_slug="fighter", level=level,
                feature_name=f"Способность {level}",
                is_asi=(level == 2), feature_type="main", proficiency_bonus=2,
            )
            db_session.add(feat)
        db_session.commit()

        response = client.get("/api/data/classes/fighter/features?level=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["level"] == 2


# ─────────────────────── тесты заклинаний ───────────────────────

class TestSpells:
    def test_list_spells_empty(self, client):
        response = client.get("/api/data/spells")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_spells(self, client, sample_spell):
        response = client.get("/api/data/spells")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["slug"] == "fire-bolt"

    def test_filter_by_level(self, client, db_session):
        for level in [0, 1, 2]:
            db_session.add(Spell(
                id=uuid.uuid4(), slug=f"spell-lv{level}", name=f"Заклинание {level}",
                level=level, concentration=False, ritual=False,
                classes=["wizard"],
            ))
        db_session.commit()

        response = client.get("/api/data/spells?level=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["level"] == 1

    def test_filter_by_school(self, client, db_session):
        db_session.add(Spell(
            id=uuid.uuid4(), slug="evoc-spell", name="Evocation spell",
            level=1, school="Evocation", concentration=False, ritual=False, classes=[],
        ))
        db_session.add(Spell(
            id=uuid.uuid4(), slug="div-spell", name="Divination spell",
            level=1, school="Divination", concentration=False, ritual=False, classes=[],
        ))
        db_session.commit()

        response = client.get("/api/data/spells?school=Evocation")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["school"] == "Evocation"

    def test_filter_by_class(self, client, db_session):
        db_session.add(Spell(
            id=uuid.uuid4(), slug="wizard-spell", name="Wizard spell",
            level=1, concentration=False, ritual=False, classes=["wizard"],
        ))
        db_session.add(Spell(
            id=uuid.uuid4(), slug="cleric-spell", name="Cleric spell",
            level=1, concentration=False, ritual=False, classes=["cleric"],
        ))
        db_session.commit()

        response = client.get("/api/data/spells?class=wizard")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "wizard" in data[0]["classes"]

    def test_get_spell_by_slug(self, client, sample_spell):
        response = client.get("/api/data/spells/fire-bolt")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Огненный снаряд"
        assert data["level"] == 0

    def test_get_spell_not_found(self, client):
        response = client.get("/api/data/spells/nonexistent-spell")
        assert response.status_code == 404


# ─────────────────────── тесты оружия ───────────────────────

class TestWeapons:
    def test_list_weapons_empty(self, client):
        response = client.get("/api/data/weapons")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_weapons(self, client, sample_weapon):
        response = client.get("/api/data/weapons")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["slug"] == "longsword"
        assert data[0]["damage_dice"] == "1d8"

    def test_filter_by_category(self, client, db_session):
        db_session.add(Weapon(
            id=uuid.uuid4(), slug="dagger", name="Кинжал",
            category="Simple Melee", damage_dice="1d4", damage_type="Колющий",
            properties=["Лёгкое"], ability="str",
        ))
        db_session.add(Weapon(
            id=uuid.uuid4(), slug="longbow", name="Длинный лук",
            category="Martial Ranged", damage_dice="1d8", damage_type="Колющий",
            properties=["Двуручное"], ability="dex",
        ))
        db_session.commit()

        response = client.get("/api/data/weapons?category=Simple+Melee")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category"] == "Simple Melee"


# ─────────────────────── тесты брони ───────────────────────

class TestArmors:
    def test_list_armors_empty(self, client):
        response = client.get("/api/data/armors")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_armors(self, client, sample_armor):
        response = client.get("/api/data/armors")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["slug"] == "leather"
        assert data[0]["base_ac"] == 11

    def test_filter_by_category(self, client, db_session):
        db_session.add(Armor(
            id=uuid.uuid4(), slug="plate", name="Латы",
            category="Heavy", base_ac=18, dex_modifier="none",
            min_strength=15, stealth_disadvantage=True,
        ))
        db_session.add(Armor(
            id=uuid.uuid4(), slug="chain-shirt", name="Кольчужная рубашка",
            category="Medium", base_ac=13, dex_modifier="max2",
            min_strength=0, stealth_disadvantage=False,
        ))
        db_session.commit()

        response = client.get("/api/data/armors?category=Heavy")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category"] == "Heavy"
