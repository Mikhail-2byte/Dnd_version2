"""
Тесты для шаблонов персонажей
"""
import pytest
from fastapi.testclient import TestClient
from app.services.character_service import get_character_templates, get_character_template


class TestCharacterTemplatesService:
    """Тесты для сервиса шаблонов персонажей"""
    
    def test_get_all_templates(self):
        """Получение всех шаблонов"""
        templates = get_character_templates()
        
        assert isinstance(templates, dict)
        assert len(templates) > 0
        
        # Проверяем, что есть ожидаемые классы
        expected_classes = ["warrior", "wizard", "rogue", "cleric", "ranger"]
        for class_name in expected_classes:
            assert class_name in templates
    
    def test_template_structure(self):
        """Проверка структуры шаблона"""
        templates = get_character_templates()
        
        if not templates:
            pytest.skip("Шаблоны не загружены")
        
        # Берем первый шаблон для проверки
        template_key = list(templates.keys())[0]
        template = templates[template_key]
        
        # Проверяем обязательные поля
        assert "class" in template
        assert "description" in template
        assert "default_stats" in template
        assert "starting_equipment" in template
        assert "suggested_names" in template
        assert "suggested_background" in template
        assert "icon" in template
        
        # Проверяем структуру default_stats
        stats = template["default_stats"]
        required_stats = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        for stat in required_stats:
            assert stat in stats
            assert isinstance(stats[stat], int)
            assert 1 <= stats[stat] <= 30
    
    def test_get_specific_template(self):
        """Получение конкретного шаблона"""
        template = get_character_template("warrior")
        
        assert template is not None
        assert template["class"] == "Воин"
        assert "default_stats" in template
        assert template["default_stats"]["strength"] >= 10  # Воин должен иметь высокую силу
    
    def test_get_invalid_template(self):
        """Получение несуществующего шаблона"""
        with pytest.raises(ValueError) as exc_info:
            get_character_template("invalid_class")
        
        assert "не найден" in str(exc_info.value).lower() or "not found" in str(exc_info.value).lower()


class TestCharacterTemplatesAPI:
    """Тесты для API шаблонов персонажей"""
    
    def test_get_templates_endpoint(self, authenticated_client: TestClient):
        """Получение всех шаблонов через API"""
        response = authenticated_client.get("/api/characters/templates")
        
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        templates = data["templates"]
        assert isinstance(templates, dict)
        assert len(templates) > 0
    
    def test_get_templates_unauthorized(self, client: TestClient):
        """Получение шаблонов без авторизации"""
        response = client.get("/api/characters/templates")
        assert response.status_code == 403
    
    def test_get_specific_template_endpoint(self, authenticated_client: TestClient):
        """Получение конкретного шаблона через API"""
        response = authenticated_client.get("/api/characters/templates/warrior")
        
        assert response.status_code == 200
        data = response.json()
        assert "template" in data
        template = data["template"]
        assert template["class"] == "Воин"
        assert "default_stats" in template
    
    def test_get_invalid_template_endpoint(self, authenticated_client: TestClient):
        """Получение несуществующего шаблона через API"""
        response = authenticated_client.get("/api/characters/templates/invalid_class")
        
        assert response.status_code == 404
        assert "не найден" in response.json()["detail"].lower() or "not found" in response.json()["detail"].lower()
    
    def test_all_class_templates_exist(self, authenticated_client: TestClient):
        """Проверка, что все ожидаемые классы присутствуют"""
        response = authenticated_client.get("/api/characters/templates")
        assert response.status_code == 200
        
        templates = response.json()["templates"]
        expected_classes = ["warrior", "wizard", "rogue", "cleric", "ranger"]
        
        for class_name in expected_classes:
            assert class_name in templates, f"Класс {class_name} не найден в шаблонах"
            
            # Проверяем базовую валидность каждого шаблона
            template = templates[class_name]
            assert template["class"] is not None
            assert len(template["default_stats"]) == 6  # Все 6 характеристик
            assert len(template["starting_equipment"]) > 0
            assert len(template["suggested_names"]) > 0

