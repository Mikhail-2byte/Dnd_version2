"""
Тесты для автогенерации характеристик персонажей
"""
import pytest
from app.services.character_service import generate_ability_scores, get_character_template


class TestAbilityScoresGeneration:
    """Тесты для генерации характеристик"""
    
    def test_standard_array_method(self):
        """Тест стандартного массива"""
        scores = generate_ability_scores(method="standard_array")
        
        # Проверяем структуру
        assert isinstance(scores, dict)
        assert len(scores) == 6
        
        # Проверяем наличие всех характеристик
        required_stats = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        for stat in required_stats:
            assert stat in scores
            assert isinstance(scores[stat], int)
            assert 1 <= scores[stat] <= 30
        
        # Стандартный массив содержит [15, 14, 13, 12, 10, 8]
        # Проверяем, что значения корректны (могут быть в любом порядке)
        score_values = list(scores.values())
        assert 15 in score_values
        assert 14 in score_values
        assert 13 in score_values
        assert 12 in score_values
        assert 10 in score_values
        assert 8 in score_values
    
    def test_point_buy_method(self):
        """Тест метода Point Buy"""
        scores = generate_ability_scores(method="point_buy")
        
        assert isinstance(scores, dict)
        assert len(scores) == 6
        
        # Проверяем, что все значения в допустимом диапазоне
        for stat_name, value in scores.items():
            assert 8 <= value <= 15  # Point Buy ограничивает максимум 15
            assert isinstance(value, int)
        
        # Проверяем, что все характеристики присутствуют
        required_stats = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        assert set(scores.keys()) == set(required_stats)
    
    def test_random_method(self):
        """Тест метода 4d6 drop lowest"""
        scores = generate_ability_scores(method="random")
        
        assert isinstance(scores, dict)
        assert len(scores) == 6
        
        # Метод 4d6 drop lowest дает значения от 3 до 18
        for stat_name, value in scores.items():
            assert 3 <= value <= 18
            assert isinstance(value, int)
        
        # Проверяем структуру
        required_stats = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        assert set(scores.keys()) == set(required_stats)
    
    def test_invalid_method(self):
        """Тест с неверным методом"""
        with pytest.raises(ValueError) as exc_info:
            generate_ability_scores(method="invalid_method")
        
        assert "неверный метод" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()
    
    def test_with_class_template(self):
        """Тест генерации с учетом шаблона класса"""
        template = get_character_template("warrior")
        
        scores = generate_ability_scores(method="standard_array", class_template=template)
        
        assert isinstance(scores, dict)
        assert len(scores) == 6
        
        # Воин должен иметь высокую силу (это приоритетная характеристика)
        # При стандартном массиве [15, 14, 13, 12, 10, 8], самое высокое значение (15)
        # должно попасть на силу, если воин имеет силу как приоритет
        assert scores["strength"] >= 13  # Должно быть одно из высоких значений
        
        # Проверяем, что все характеристики присутствуют
        required_stats = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        assert set(scores.keys()) == set(required_stats)
    
    def test_class_prioritization(self):
        """Тест приоритизации характеристик по классу"""
        wizard_template = get_character_template("wizard")
        
        scores = generate_ability_scores(method="standard_array", class_template=wizard_template)
        
        # Маг должен иметь высокий интеллект (приоритетная характеристика)
        assert scores["intelligence"] >= 13
        
        # Проверяем структуру
        assert isinstance(scores, dict)
        assert len(scores) == 6


class TestAbilityScoresGenerationAPI:
    """Тесты для API автогенерации характеристик"""
    
    def test_generate_abilities_standard_array(self, authenticated_client):
        """Генерация стандартным массивом через API"""
        response = authenticated_client.post(
            "/api/characters/generate-abilities",
            json={"method": "standard_array"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "strength" in data
        assert "dexterity" in data
        assert "constitution" in data
        assert "intelligence" in data
        assert "wisdom" in data
        assert "charisma" in data
        assert data["method"] == "standard_array"
        
        # Проверяем, что значения в стандартном массиве
        values = [data["strength"], data["dexterity"], data["constitution"],
                  data["intelligence"], data["wisdom"], data["charisma"]]
        assert 15 in values
        assert 14 in values
        assert 13 in values
        assert 12 in values
        assert 10 in values
        assert 8 in values
    
    def test_generate_abilities_point_buy(self, authenticated_client):
        """Генерация методом Point Buy через API"""
        response = authenticated_client.post(
            "/api/characters/generate-abilities",
            json={"method": "point_buy"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["method"] == "point_buy"
        
        # Point Buy ограничивает максимум 15
        values = [data["strength"], data["dexterity"], data["constitution"],
                  data["intelligence"], data["wisdom"], data["charisma"]]
        assert all(8 <= v <= 15 for v in values)
    
    def test_generate_abilities_random(self, authenticated_client):
        """Генерация случайным методом через API"""
        response = authenticated_client.post(
            "/api/characters/generate-abilities",
            json={"method": "random"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["method"] == "random"
        
        # Случайный метод дает значения от 3 до 18
        values = [data["strength"], data["dexterity"], data["constitution"],
                  data["intelligence"], data["wisdom"], data["charisma"]]
        assert all(3 <= v <= 18 for v in values)
    
    def test_generate_abilities_with_class(self, authenticated_client):
        """Генерация с учетом класса"""
        response = authenticated_client.post(
            "/api/characters/generate-abilities",
            json={"method": "standard_array", "class_name": "warrior"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Воин должен иметь относительно высокую силу
        assert data["strength"] >= 12
    
    def test_generate_abilities_invalid_method(self, authenticated_client):
        """Генерация с неверным методом"""
        response = authenticated_client.post(
            "/api/characters/generate-abilities",
            json={"method": "invalid_method"}
        )
        
        assert response.status_code == 400
        assert "неверный метод" in response.json()["detail"].lower() or "invalid" in response.json()["detail"].lower()
    
    def test_generate_abilities_invalid_class(self, authenticated_client):
        """Генерация с неверным классом (должно игнорироваться, не вызывать ошибку)"""
        response = authenticated_client.post(
            "/api/characters/generate-abilities",
            json={"method": "standard_array", "class_name": "invalid_class"}
        )
        
        # Не должно вызывать ошибку, просто игнорирует класс
        assert response.status_code == 200
        data = response.json()
        assert "strength" in data
        assert data["method"] == "standard_array"
    
    def test_generate_abilities_unauthorized(self, client):
        """Генерация без авторизации"""
        response = client.post(
            "/api/characters/generate-abilities",
            json={"method": "standard_array"}
        )
        
        assert response.status_code == 403

