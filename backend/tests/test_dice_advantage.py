"""
Тесты для системы преимущества/помехи (Advantage/Disadvantage)
"""
import pytest
from app.services.dice_service import DiceRoller


class TestAdvantageDisadvantage:
    """Тесты для advantage/disadvantage"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.roller = DiceRoller(default_faces=20, max_dice=10)
    
    def test_advantage_rolls_two_dice(self):
        """При преимуществе бросается 2 кубика"""
        result = self.roller.roll(1, faces=20, advantage=True)
        
        assert result.advantage_rolls is not None
        assert len(result.advantage_rolls) == 2
        assert result.advantage_type == "advantage"
        assert result.selected_roll is not None
    
    def test_advantage_selects_higher(self):
        """При преимуществе выбирается большее значение"""
        # Делаем несколько бросков, чтобы проверить логику
        for _ in range(10):
            result = self.roller.roll(1, faces=20, advantage=True)
            assert result.selected_roll is not None
            assert result.selected_roll.value >= min(die.value for die in result.advantage_rolls)
            assert result.selected_roll.value <= max(die.value for die in result.advantage_rolls)
            # Выбранное значение должно быть максимальным
            assert result.selected_roll.value == max(die.value for die in result.advantage_rolls)
    
    def test_disadvantage_selects_lower(self):
        """При помехе выбирается меньшее значение"""
        for _ in range(10):
            result = self.roller.roll(1, faces=20, advantage=False)
            assert result.selected_roll is not None
            assert result.selected_roll.value >= min(die.value for die in result.advantage_rolls)
            assert result.selected_roll.value <= max(die.value for die in result.advantage_rolls)
            # Выбранное значение должно быть минимальным
            assert result.selected_roll.value == min(die.value for die in result.advantage_rolls)
    
    def test_advantage_only_for_single_die(self):
        """Advantage/disadvantage работает только для одного кубика"""
        # При count > 1 advantage игнорируется
        result = self.roller.roll(2, faces=20, advantage=True)
        assert result.advantage_rolls is None
        assert result.advantage_type is None
        assert result.selected_roll is None
        assert len(result.rolls) == 2
    
    def test_normal_roll_no_advantage(self):
        """Обычный бросок без advantage/disadvantage"""
        result = self.roller.roll(1, faces=20, advantage=None)
        assert result.advantage_rolls is None
        assert result.advantage_type is None
        assert result.selected_roll is None
        assert len(result.rolls) == 1
    
    def test_advantage_total_is_selected_value(self):
        """Итоговое значение при advantage = выбранное значение"""
        result = self.roller.roll(1, faces=20, advantage=True)
        assert result.total == result.selected_roll.value
    
    def test_disadvantage_total_is_selected_value(self):
        """Итоговое значение при disadvantage = выбранное значение"""
        result = self.roller.roll(1, faces=20, advantage=False)
        assert result.total == result.selected_roll.value
    
    def test_advantage_to_dict_includes_info(self):
        """to_dict включает информацию об advantage"""
        result = self.roller.roll(1, faces=20, advantage=True)
        result_dict = self.roller.to_dict(result)
        
        assert "advantage_rolls" in result_dict
        assert "selected_roll" in result_dict
        assert "advantage_type" in result_dict
        assert result_dict["advantage_type"] == "advantage"
        assert len(result_dict["advantage_rolls"]) == 2
    
    def test_disadvantage_to_dict_includes_info(self):
        """to_dict включает информацию об disadvantage"""
        result = self.roller.roll(1, faces=20, advantage=False)
        result_dict = self.roller.to_dict(result)
        
        assert "advantage_rolls" in result_dict
        assert "selected_roll" in result_dict
        assert "advantage_type" in result_dict
        assert result_dict["advantage_type"] == "disadvantage"
        assert len(result_dict["advantage_rolls"]) == 2
    
    def test_normal_roll_to_dict_no_advantage_info(self):
        """to_dict не включает advantage информацию для обычного броска"""
        result = self.roller.roll(1, faces=20, advantage=None)
        result_dict = self.roller.to_dict(result)
        
        assert "advantage_rolls" not in result_dict
        assert "selected_roll" not in result_dict
        assert "advantage_type" not in result_dict


class TestAdvantageDisadvantageAPI:
    """Тесты для API advantage/disadvantage"""
    
    def test_roll_with_advantage(self, authenticated_client):
        """Бросок с преимуществом через API"""
        response = authenticated_client.post(
            "/api/dice/roll",
            json={"count": 1, "faces": 20, "advantage": True}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "advantage_rolls" in data
        assert "selected_roll" in data
        assert "advantage_type" in data
        assert data["advantage_type"] == "advantage"
        assert len(data["advantage_rolls"]) == 2
        assert data["total"] == data["selected_roll"]["value"]
        # Выбранное значение должно быть максимальным
        assert data["selected_roll"]["value"] == max(die["value"] for die in data["advantage_rolls"])
    
    def test_roll_with_disadvantage(self, authenticated_client):
        """Бросок с помехой через API"""
        response = authenticated_client.post(
            "/api/dice/roll",
            json={"count": 1, "faces": 20, "advantage": False}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "advantage_rolls" in data
        assert "selected_roll" in data
        assert "advantage_type" in data
        assert data["advantage_type"] == "disadvantage"
        assert len(data["advantage_rolls"]) == 2
        assert data["total"] == data["selected_roll"]["value"]
        # Выбранное значение должно быть минимальным
        assert data["selected_roll"]["value"] == min(die["value"] for die in data["advantage_rolls"])
    
    def test_roll_without_advantage(self, authenticated_client):
        """Обычный бросок без advantage/disadvantage"""
        response = authenticated_client.post(
            "/api/dice/roll",
            json={"count": 1, "faces": 20, "advantage": None}
        )
        
        assert response.status_code == 200
        data = response.json()
        # Для обычного броска advantage поля могут отсутствовать или быть None
        if "advantage_type" in data:
            assert data["advantage_type"] is None
    
    def test_advantage_ignored_for_multiple_dice(self, authenticated_client):
        """Advantage игнорируется при броске нескольких кубиков"""
        response = authenticated_client.post(
            "/api/dice/roll",
            json={"count": 2, "faces": 20, "advantage": True}
        )
        
        assert response.status_code == 200
        data = response.json()
        # При count > 1 advantage не применяется
        assert "advantage_rolls" not in data or data.get("advantage_rolls") is None
        assert len(data["rolls"]) == 2

