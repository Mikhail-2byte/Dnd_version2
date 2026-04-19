"""
Тесты для истории бросков кубиков
"""
import pytest
import uuid
from sqlalchemy.orm import Session
from app.models.dice_roll_history import DiceRollHistory
from app.models.game_session import GameSession
from app.models.user import User
from app.services.dice_service import save_roll_history, get_ability_modifier, get_templates, apply_template
from app.models.character import Character


@pytest.fixture
def sample_user(db_session) -> User:
    """Создание тестового пользователя"""
    user = User(
        id=uuid.uuid4(),
        email=f"test_{uuid.uuid4()}@example.com",
        username="test_user",
        password_hash="hashed_password"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_game(db_session, sample_user: User) -> GameSession:
    """Создание тестовой игры"""
    game = GameSession(
        id=uuid.uuid4(),
        name="Test Game",
        invite_code="TEST01",
        master_id=sample_user.id
    )
    db_session.add(game)
    db_session.commit()
    db_session.refresh(game)
    return game


@pytest.fixture
def sample_character(db_session, sample_user: User) -> Character:
    """Создание тестового персонажа"""
    character = Character(
        id=uuid.uuid4(),
        user_id=sample_user.id,
        name="Test Character",
        race="Human",
        char_class="Fighter",
        level=1,
        strength=16,  # Модификатор должен быть +3
        dexterity=14,  # Модификатор должен быть +2
        constitution=12,  # Модификатор должен быть +1
        intelligence=10,  # Модификатор должен быть 0
        wisdom=8,  # Модификатор должен быть -1
        charisma=6  # Модификатор должен быть -2
    )
    db_session.add(character)
    db_session.commit()
    db_session.refresh(character)
    return character


class TestAbilityModifier:
    """Тесты для расчета модификаторов характеристик"""
    
    def test_modifier_10(self):
        """Модификатор для характеристики 10 должен быть 0"""
        assert get_ability_modifier(10) == 0
    
    def test_modifier_12(self):
        """Модификатор для характеристики 12 должен быть +1"""
        assert get_ability_modifier(12) == 1
    
    def test_modifier_15(self):
        """Модификатор для характеристики 15 должен быть +2"""
        assert get_ability_modifier(15) == 2
    
    def test_modifier_18(self):
        """Модификатор для характеристики 18 должен быть +4"""
        assert get_ability_modifier(18) == 4
    
    def test_modifier_8(self):
        """Модификатор для характеристики 8 должен быть -1"""
        assert get_ability_modifier(8) == -1
    
    def test_modifier_6(self):
        """Модификатор для характеристики 6 должен быть -2"""
        assert get_ability_modifier(6) == -2
    
    def test_modifier_1(self):
        """Модификатор для характеристики 1 должен быть -5"""
        assert get_ability_modifier(1) == -5


class TestDiceTemplates:
    """Тесты для шаблонов бросков"""
    
    def test_get_templates(self):
        """Тест загрузки шаблонов из JSON"""
        templates = get_templates()
        assert isinstance(templates, dict)
        assert len(templates) > 0
        # Проверяем наличие основных шаблонов
        assert "attack_melee" in templates
        assert "strength_save" in templates
        assert "dexterity_check" in templates
    
    def test_template_structure(self):
        """Проверка структуры шаблона"""
        templates = get_templates()
        template = templates.get("attack_melee")
        assert template is not None
        assert "label" in template
        assert "count" in template
        assert "faces" in template
        assert "roll_type" in template
        assert "modifier_source" in template
    
    def test_apply_template_without_character(self):
        """Применение шаблона без персонажа"""
        result = apply_template("attack_melee", None)
        assert result["count"] == 1
        assert result["faces"] == 20
        assert result["roll_type"] == "attack"
        assert result["modifier"] is None
    
    def test_apply_template_with_character(self, sample_character: Character):
        """Применение шаблона с персонажем"""
        result = apply_template("attack_melee", sample_character)
        assert result["count"] == 1
        assert result["faces"] == 20
        assert result["roll_type"] == "attack"
        # Сила персонажа = 16, модификатор = +3
        assert result["modifier"] == 3
    
    def test_apply_template_dexterity(self, sample_character: Character):
        """Применение шаблона с характеристикой Ловкость"""
        result = apply_template("dexterity_save", sample_character)
        # Ловкость персонажа = 14, модификатор = +2
        assert result["modifier"] == 2
    
    def test_apply_template_invalid(self):
        """Применение несуществующего шаблона"""
        with pytest.raises(ValueError, match="не найден"):
            apply_template("invalid_template", None)
    
    def test_apply_template_invalid_ability(self, sample_character: Character):
        """Попытка применить шаблон с несуществующей характеристикой"""
        # Создаем шаблон с несуществующей характеристикой
        # Это должно вызвать ошибку при применении


class TestDiceRollHistory:
    """Тесты для истории бросков"""
    
    def test_save_roll_history(self, db_session, sample_game: GameSession, sample_user: User):
        """Сохранение записи истории броска"""
        rolls = [{"die_id": "d1", "value": 15}, {"die_id": "d2", "value": 5}]
        
        history = save_roll_history(
            db=db_session,
            game_id=sample_game.id,
            user_id=sample_user.id,
            count=2,
            faces=20,
            rolls=rolls,
            total=20,
            roll_type="attack",
            modifier=3
        )
        
        assert history.id is not None
        assert history.game_id == sample_game.id
        assert history.user_id == sample_user.id
        assert history.count == 2
        assert history.faces == 20
        assert history.rolls == rolls
        assert history.total == 20
        assert history.roll_type == "attack"
        assert history.modifier == 3
        assert history.created_at is not None
    
    def test_save_roll_history_no_modifier(self, db_session, sample_game: GameSession, sample_user: User):
        """Сохранение записи истории без модификатора"""
        rolls = [{"die_id": "d1", "value": 10}]
        
        history = save_roll_history(
            db=db_session,
            game_id=sample_game.id,
            user_id=sample_user.id,
            count=1,
            faces=20,
            rolls=rolls,
            total=10
        )
        
        assert history.roll_type is None
        assert history.modifier is None
    
    def test_save_roll_history_with_roll_type(self, db_session, sample_game: GameSession, sample_user: User):
        """Сохранение записи истории с типом проверки"""
        rolls = [{"die_id": "d1", "value": 12}]
        
        history = save_roll_history(
            db=db_session,
            game_id=sample_game.id,
            user_id=sample_user.id,
            count=1,
            faces=20,
            rolls=rolls,
            total=15,
            roll_type="save",
            modifier=3
        )
        
        assert history.roll_type == "save"
        assert history.total == 15  # 12 + 3

