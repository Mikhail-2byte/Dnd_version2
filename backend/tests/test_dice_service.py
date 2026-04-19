"""
Тесты для доменного сервиса броска кубиков
Основаны на тестах из Example/roll-dice
"""
import pytest
from app.services.dice_service import DiceRoller


class TestDiceRoller:
    """Тесты для класса DiceRoller"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.roller = DiceRoller(default_faces=12, max_dice=10)
    
    def test_roll_generates_requested_number_of_dice_within_bounds(self):
        """Тест: бросок генерирует запрошенное количество кубиков в допустимых пределах"""
        result = self.roller.roll(5)
        
        assert len(result.rolls) == 5
        for i, die in enumerate(result.rolls):
            assert die.die_id == f"d{i + 1}"
            assert 1 <= die.value <= 12
    
    def test_total_sums_up_die_results(self):
        """Тест: сумма складывает результаты всех кубиков"""
        result = self.roller.roll(3)
        expected_total = sum(die.value for die in result.rolls)
        
        assert result.total == expected_total
    
    def test_roll_throws_when_dice_count_is_zero(self):
        """Тест: выбрасывает ошибку при нулевом количестве кубиков"""
        with pytest.raises(ValueError, match="положительным"):
            self.roller.roll(0)
    
    def test_roll_throws_when_dice_count_exceeds_limit(self):
        """Тест: выбрасывает ошибку при превышении лимита кубиков"""
        with pytest.raises(ValueError, match="превышает"):
            self.roller.roll(11)
    
    def test_roll_with_custom_faces(self):
        """Тест: бросок с кастомным количеством граней"""
        result = self.roller.roll(2, faces=20)
        
        assert len(result.rolls) == 2
        for die in result.rolls:
            assert 1 <= die.value <= 20
    
    def test_roll_uses_default_faces_when_not_specified(self):
        """Тест: использует грани по умолчанию, если не указаны"""
        result = self.roller.roll(1)
        
        assert len(result.rolls) == 1
        assert 1 <= result.rolls[0].value <= 12
    
    def test_roll_throws_when_faces_too_low(self):
        """Тест: выбрасывает ошибку при слишком малом количестве граней"""
        with pytest.raises(ValueError, match="не менее 2"):
            self.roller.roll(1, faces=1)
    
    def test_roll_throws_when_faces_not_allowed(self):
        """Тест: выбрасывает ошибку при неразрешенном количестве граней"""
        with pytest.raises(ValueError, match="Недопустимое количество граней"):
            self.roller.roll(1, faces=7)
    
    def test_roll_all_allowed_faces(self):
        """Тест: бросок всех разрешенных типов кубиков"""
        allowed_faces = [4, 6, 8, 10, 12, 20]
        
        for faces in allowed_faces:
            result = self.roller.roll(1, faces=faces)
            assert len(result.rolls) == 1
            assert 1 <= result.rolls[0].value <= faces
    
    def test_roll_max_dice(self):
        """Тест: бросок максимального количества кубиков"""
        result = self.roller.roll(10)
        
        assert len(result.rolls) == 10
        assert result.total == sum(die.value for die in result.rolls)
    
    def test_to_dict_conversion(self):
        """Тест: преобразование результата в словарь"""
        result = self.roller.roll(2, faces=6)
        result_dict = self.roller.to_dict(result)
        
        assert "rolls" in result_dict
        assert "total" in result_dict
        assert len(result_dict["rolls"]) == 2
        assert isinstance(result_dict["rolls"][0], dict)
        assert "die_id" in result_dict["rolls"][0]
        assert "value" in result_dict["rolls"][0]
        assert result_dict["total"] == result.total
    
    def test_die_ids_are_sequential(self):
        """Тест: ID кубиков последовательные"""
        result = self.roller.roll(5)
        
        for i, die in enumerate(result.rolls):
            assert die.die_id == f"d{i + 1}"
    
    def test_roll_values_are_in_range(self):
        """Тест: значения кубиков в допустимом диапазоне"""
        result = self.roller.roll(10, faces=20)
        
        for die in result.rolls:
            assert 1 <= die.value <= 20

