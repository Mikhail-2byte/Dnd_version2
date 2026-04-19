"""
Тесты для предысторий персонажей
"""
import pytest
from app.services.character_service import get_character_template


class TestCharacterBackgrounds:
    """Тесты для предысторий персонажей"""
    
    def test_templates_have_backgrounds(self):
        """Проверка, что шаблоны содержат предыстории"""
        class_names = ["warrior", "wizard", "rogue", "cleric", "ranger"]
        
        for class_name in class_names:
            template = get_character_template(class_name)
            
            assert "backgrounds" in template
            assert isinstance(template["backgrounds"], list)
            assert len(template["backgrounds"]) > 0
    
    def test_background_structure(self):
        """Проверка структуры предыстории"""
        template = get_character_template("warrior")
        
        if "backgrounds" not in template or not template["backgrounds"]:
            pytest.skip("Предыстории не найдены в шаблоне")
        
        background = template["backgrounds"][0]
        
        # Проверяем обязательные поля
        assert "name" in background
        assert "description" in background
        assert "skill_bonuses" in background
        assert "features" in background
        
        # Проверяем типы
        assert isinstance(background["name"], str)
        assert isinstance(background["description"], str)
        assert isinstance(background["skill_bonuses"], list)
        assert isinstance(background["features"], str)
        
        # Проверяем, что есть хотя бы один бонус навыка
        assert len(background["skill_bonuses"]) > 0
    
    def test_warrior_backgrounds(self):
        """Проверка предысторий воина"""
        template = get_character_template("warrior")
        backgrounds = template["backgrounds"]
        
        # Воин должен иметь предыстории связанные с военным делом
        background_names = [bg["name"] for bg in backgrounds]
        
        # Проверяем, что есть предыстория "Солдат"
        assert "Солдат" in background_names
        
        # Проверяем структуру каждой предыстории
        for background in backgrounds:
            assert "skill_bonuses" in background
            assert len(background["skill_bonuses"]) >= 1
    
    def test_wizard_backgrounds(self):
        """Проверка предысторий мага"""
        template = get_character_template("wizard")
        backgrounds = template["backgrounds"]
        
        background_names = [bg["name"] for bg in backgrounds]
        
        # Маг должен иметь предыстории связанные с изучением магии
        assert "Ученый" in background_names or "Ученик мага" in background_names
        
        for background in backgrounds:
            assert "skill_bonuses" in background
            assert len(background["skill_bonuses"]) >= 1
    
    def test_rogue_backgrounds(self):
        """Проверка предысторий плута"""
        template = get_character_template("rogue")
        backgrounds = template["backgrounds"]
        
        background_names = [bg["name"] for bg in backgrounds]
        
        # Плут должен иметь предыстории связанные с преступностью или обманом
        assert "Преступник" in background_names or "Шарлатан" in background_names
        
        for background in backgrounds:
            assert "skill_bonuses" in background
    
    def test_cleric_backgrounds(self):
        """Проверка предысторий жреца"""
        template = get_character_template("cleric")
        backgrounds = template["backgrounds"]
        
        background_names = [bg["name"] for bg in backgrounds]
        
        # Жрец должен иметь предыстории связанные с религией
        assert "Аколит" in background_names
        
        for background in backgrounds:
            assert "skill_bonuses" in background
    
    def test_ranger_backgrounds(self):
        """Проверка предысторий следопыта"""
        template = get_character_template("ranger")
        backgrounds = template["backgrounds"]
        
        background_names = [bg["name"] for bg in backgrounds]
        
        # Следопыт должен иметь предыстории связанные с природой
        assert "Отшельник" in background_names or "Охотник" in background_names
        
        for background in backgrounds:
            assert "skill_bonuses" in background
    
    def test_all_backgrounds_have_required_fields(self):
        """Проверка, что все предыстории имеют обязательные поля"""
        class_names = ["warrior", "wizard", "rogue", "cleric", "ranger"]
        
        for class_name in class_names:
            template = get_character_template(class_name)
            
            if "backgrounds" not in template:
                continue
            
            for background in template["backgrounds"]:
                assert "name" in background, f"Предыстория {class_name} не имеет поля 'name'"
                assert "description" in background, f"Предыстория {class_name} не имеет поля 'description'"
                assert "skill_bonuses" in background, f"Предыстория {class_name} не имеет поля 'skill_bonuses'"
                assert "features" in background, f"Предыстория {class_name} не имеет поля 'features'"
                
                assert isinstance(background["skill_bonuses"], list), f"skill_bonuses должен быть списком для {class_name}"
                assert len(background["skill_bonuses"]) > 0, f"skill_bonuses должен содержать хотя бы один элемент для {class_name}"

