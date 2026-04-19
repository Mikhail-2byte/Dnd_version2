"""
Тесты для базовой системы боя
"""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
from app.models.user import User
from app.models.game_session import GameSession
from app.models.game_participant import GameParticipant
from app.models.character import Character
from app.models.token import Token
from app.models.combat_session import CombatSession
from app.models.combat_participant import CombatParticipant
from app.services.combat_service import (
    start_combat,
    roll_initiative,
    get_initiative_order,
    get_current_combat,
    end_combat,
    perform_attack,
    apply_damage,
    apply_healing
)
from sqlalchemy.orm import Session


@pytest.fixture
def test_combat_game(db_session: Session, test_user: User, test_user2: User):
    """Создание игры для тестов боя"""
    game = GameSession(
        id=uuid4(),
        name="Test Combat Game",
        invite_code="COMBAT1",
        master_id=test_user.id
    )
    db_session.add(game)
    
    master_participant = GameParticipant(
        game_id=game.id,
        user_id=test_user.id,
        role="master"
    )
    player_participant = GameParticipant(
        game_id=game.id,
        user_id=test_user2.id,
        role="player"
    )
    db_session.add_all([master_participant, player_participant])
    db_session.commit()
    db_session.refresh(game)
    return game


@pytest.fixture
def test_characters(db_session: Session, test_user: User, test_user2: User):
    """Создание персонажей для тестов"""
    char1 = Character(
        id=uuid4(),
        user_id=test_user.id,
        name="Warrior",
        race="Human",
        char_class="Fighter",
        level=1,
        strength=16,
        dexterity=13,
        constitution=15,
        intelligence=10,
        wisdom=12,
        charisma=8
    )
    char2 = Character(
        id=uuid4(),
        user_id=test_user2.id,
        name="Wizard",
        race="Elf",
        char_class="Wizard",
        level=1,
        strength=8,
        dexterity=13,
        constitution=14,
        intelligence=16,
        wisdom=12,
        charisma=10
    )
    db_session.add_all([char1, char2])
    db_session.commit()
    return {"char1": char1, "char2": char2}


class TestCombatService:
    """Тесты для сервиса боя"""
    
    def test_start_combat(self, db_session: Session, test_combat_game: GameSession, test_characters: dict):
        """Создание боевой сессии"""
        game = test_combat_game
        char1 = test_characters["char1"]
        
        participant_data = [
            {
                "character_id": char1.id,
                "max_hp": 20,
                "armor_class": 15,
                "is_player_controlled": True
            }
        ]
        
        combat = start_combat(db_session, game.id, participant_data)
        
        assert combat is not None
        assert combat.game_id == game.id
        assert combat.is_active is True
        assert combat.round_number == 1
        assert combat.current_turn_index == 0
        
        # Проверяем участников
        participants = combat.participants
        assert len(participants) == 1
        assert participants[0].character_id == char1.id
        assert participants[0].current_hp == 20
        assert participants[0].max_hp == 20
        assert participants[0].armor_class == 15
    
    def test_roll_initiative(self, db_session: Session, test_combat_game: GameSession, test_characters: dict):
        """Бросок инициативы"""
        game = test_combat_game
        char1 = test_characters["char1"]
        
        # Создаем бой
        participant_data = [
            {
                "character_id": char1.id,
                "max_hp": 20,
                "armor_class": 15,
                "is_player_controlled": True
            }
        ]
        combat = start_combat(db_session, game.id, participant_data)
        participant_id = combat.participants[0].id
        
        # Бросаем инициативу
        participant = roll_initiative(db_session, combat.id, participant_id, roll_value=15)
        
        assert participant.initiative == 15
        
        # Бросаем без указания значения (случайное)
        participant = roll_initiative(db_session, combat.id, participant_id, roll_value=None)
        assert participant.initiative is not None
        assert 1 <= participant.initiative <= 20
    
    def test_get_initiative_order(self, db_session: Session, test_combat_game: GameSession, test_characters: dict):
        """Получение порядка ходов по инициативе"""
        game = test_combat_game
        char1 = test_characters["char1"]
        char2 = test_characters["char2"]
        
        # Создаем бой с двумя участниками
        participant_data = [
            {
                "character_id": char1.id,
                "max_hp": 20,
                "armor_class": 15,
                "is_player_controlled": True
            },
            {
                "character_id": char2.id,
                "max_hp": 10,
                "armor_class": 12,
                "is_player_controlled": True
            }
        ]
        combat = start_combat(db_session, game.id, participant_data)
        
        participant1 = combat.participants[0]
        participant2 = combat.participants[1]
        
        # Бросаем инициативу
        roll_initiative(db_session, combat.id, participant1.id, roll_value=18)
        roll_initiative(db_session, combat.id, participant2.id, roll_value=12)
        
        # Получаем порядок
        order = get_initiative_order(db_session, combat.id)
        
        assert len(order) == 2
        assert order[0].initiative == 18  # Первый должен иметь большее значение
        assert order[1].initiative == 12
    
    def test_end_combat(self, db_session: Session, test_combat_game: GameSession, test_characters: dict):
        """Завершение боевой сессии"""
        game = test_combat_game
        char1 = test_characters["char1"]
        
        participant_data = [
            {
                "character_id": char1.id,
                "max_hp": 20,
                "armor_class": 15,
                "is_player_controlled": True
            }
        ]
        combat = start_combat(db_session, game.id, participant_data)
        
        # Завершаем бой
        ended_combat = end_combat(db_session, combat.id)
        
        assert ended_combat.is_active is False
        assert ended_combat.ended_at is not None
    
    def test_perform_attack_hit(self, db_session: Session, test_combat_game: GameSession, test_characters: dict):
        """Тест успешной атаки"""
        game = test_combat_game
        char1 = test_characters["char1"]
        char2 = test_characters["char2"]
        
        # Создаем бой с двумя участниками
        participant_data = [
            {
                "character_id": char1.id,
                "max_hp": 20,
                "armor_class": 10,
                "is_player_controlled": True
            },
            {
                "character_id": char2.id,
                "max_hp": 15,
                "armor_class": 10,
                "is_player_controlled": True
            }
        ]
        combat = start_combat(db_session, game.id, participant_data)
        attacker_id = combat.participants[0].id
        target_id = combat.participants[1].id
        
        # Атака с результатом 15 (должна попасть в КБ 10)
        attack_result = perform_attack(
            db_session,
            combat.id,
            attacker_id,
            target_id,
            attack_roll=15,
            modifier=0
        )
        
        assert attack_result["hit"] is True
        assert attack_result["attack_roll"] == 15
        assert attack_result["total_attack"] == 15
        assert attack_result["target_ac"] == 10
        assert attack_result["damage"] is not None
        assert attack_result["damage"] > 0
    
    def test_perform_attack_miss(self, db_session: Session, test_combat_game: GameSession, test_characters: dict):
        """Тест промаха"""
        game = test_combat_game
        char1 = test_characters["char1"]
        char2 = test_characters["char2"]
        
        # Создаем бой с двумя участниками
        participant_data = [
            {
                "character_id": char1.id,
                "max_hp": 20,
                "armor_class": 10,
                "is_player_controlled": True
            },
            {
                "character_id": char2.id,
                "max_hp": 15,
                "armor_class": 18,
                "is_player_controlled": True
            }
        ]
        combat = start_combat(db_session, game.id, participant_data)
        attacker_id = combat.participants[0].id
        target_id = combat.participants[1].id
        
        # Атака с результатом 10 (не попадет в КБ 18)
        attack_result = perform_attack(
            db_session,
            combat.id,
            attacker_id,
            target_id,
            attack_roll=10,
            modifier=0
        )
        
        assert attack_result["hit"] is False
        assert attack_result["attack_roll"] == 10
        assert attack_result["total_attack"] == 10
        assert attack_result["target_ac"] == 18
        assert attack_result["damage"] is None
    
    def test_apply_damage(self, db_session: Session, test_combat_game: GameSession, test_characters: dict):
        """Тест нанесения урона"""
        game = test_combat_game
        char1 = test_characters["char1"]
        
        participant_data = [
            {
                "character_id": char1.id,
                "max_hp": 20,
                "armor_class": 10,
                "is_player_controlled": True
            }
        ]
        combat = start_combat(db_session, game.id, participant_data)
        participant_id = combat.participants[0].id
        
        # Наносим урон
        participant = apply_damage(db_session, combat.id, participant_id, 5)
        
        assert participant.current_hp == 15
        assert participant.max_hp == 20
        assert participant.conditions is None  # Еще не повержен
        
        # Наносим еще урон, чтобы повергнуть
        participant = apply_damage(db_session, combat.id, participant_id, 20)
        
        assert participant.current_hp == 0
        assert participant.conditions is not None
        assert "unconscious" in participant.conditions
    
    def test_apply_healing(self, db_session: Session, test_combat_game: GameSession, test_characters: dict):
        """Тест исцеления"""
        game = test_combat_game
        char1 = test_characters["char1"]
        
        participant_data = [
            {
                "character_id": char1.id,
                "max_hp": 20,
                "armor_class": 10,
                "is_player_controlled": True
            }
        ]
        combat = start_combat(db_session, game.id, participant_data)
        participant_id = combat.participants[0].id
        
        # Наносим урон
        participant = apply_damage(db_session, combat.id, participant_id, 10)
        assert participant.current_hp == 10
        
        # Исцеляем
        participant = apply_healing(db_session, combat.id, participant_id, 5)
        
        assert participant.current_hp == 15
        assert participant.max_hp == 20
        
        # Исцеляем больше максимума
        participant = apply_healing(db_session, combat.id, participant_id, 20)
        
        assert participant.current_hp == 20  # Не больше max_hp
        assert participant.max_hp == 20


class TestCombatAPI:
    """Тесты для API боя"""
    
    def test_start_combat_endpoint(self, authenticated_client: TestClient, test_combat_game: GameSession, test_characters: dict):
        """Начало боя через API"""
        game = test_combat_game
        char1 = test_characters["char1"]
        
        response = authenticated_client.post(
            f"/api/games/{game.id}/combat/start",
            json={"participant_ids": [str(char1.id)]}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["game_id"] == str(game.id)
        assert data["is_active"] is True
        assert len(data["participants"]) == 1
        assert data["participants"][0]["character_id"] == str(char1.id)
    
    def test_start_combat_as_player_forbidden(self, authenticated_client: TestClient, test_combat_game: GameSession, test_characters: dict, test_user2: User):
        """Игрок не может начать бой"""
        game = test_combat_game
        char1 = test_characters["char1"]
        
        # Входим как игрок
        response = authenticated_client.post(
            "/api/auth/login",
            json={"email": test_user2.email, "password": "test_password"}
        )
        token = response.json()["access_token"]
        authenticated_client.headers.update({"Authorization": f"Bearer {token}"})
        
        response = authenticated_client.post(
            f"/api/games/{game.id}/combat/start",
            json={"participant_ids": [str(char1.id)]}
        )
        
        assert response.status_code == 403
        assert "мастер" in response.json()["detail"].lower() or "master" in response.json()["detail"].lower()
    
    def test_get_current_combat(self, authenticated_client: TestClient, test_combat_game: GameSession, test_characters: dict):
        """Получение текущего боя"""
        game = test_combat_game
        char1 = test_characters["char1"]
        
        # Создаем бой
        authenticated_client.post(
            f"/api/games/{game.id}/combat/start",
            json={"participant_ids": [str(char1.id)]}
        )
        
        # Получаем текущий бой
        response = authenticated_client.get(f"/api/games/{game.id}/combat/current")
        
        assert response.status_code == 200
        data = response.json()
        assert data is not None
        assert data["is_active"] is True
        assert data["game_id"] == str(game.id)
    
    def test_roll_initiative_endpoint(self, authenticated_client: TestClient, test_combat_game: GameSession, test_characters: dict):
        """Бросок инициативы через API"""
        game = test_combat_game
        char1 = test_characters["char1"]
        
        # Создаем бой
        start_response = authenticated_client.post(
            f"/api/games/{game.id}/combat/start",
            json={"participant_ids": [str(char1.id)]}
        )
        combat_id = start_response.json()["id"]
        participant_id = start_response.json()["participants"][0]["id"]
        
        # Бросаем инициативу
        response = authenticated_client.post(
            f"/api/games/{game.id}/combat/{combat_id}/roll-initiative",
            json={"participant_id": participant_id, "initiative_roll": 15}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["initiative"] == 15
    
    def test_end_combat_endpoint(self, authenticated_client: TestClient, test_combat_game: GameSession, test_characters: dict):
        """Завершение боя через API"""
        game = test_combat_game
        char1 = test_characters["char1"]
        
        # Создаем бой
        start_response = authenticated_client.post(
            f"/api/games/{game.id}/combat/start",
            json={"participant_ids": [str(char1.id)]}
        )
        combat_id = start_response.json()["id"]
        
        # Завершаем бой
        response = authenticated_client.post(f"/api/games/{game.id}/combat/{combat_id}/end")
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False
        assert data["ended_at"] is not None
    
    def test_attack_endpoint(self, authenticated_client: TestClient, test_combat_game: GameSession, test_characters: dict):
        """Атака через API"""
        game = test_combat_game
        char1 = test_characters["char1"]
        char2 = test_characters["char2"]
        
        # Создаем бой с двумя участниками
        start_response = authenticated_client.post(
            f"/api/games/{game.id}/combat/start",
            json={"participant_ids": [str(char1.id), str(char2.id)]}
        )
        combat_id = start_response.json()["id"]
        participants = start_response.json()["participants"]
        attacker_id = participants[0]["id"]
        target_id = participants[1]["id"]
        
        # Выполняем атаку
        response = authenticated_client.post(
            f"/api/games/{game.id}/combat/{combat_id}/attack",
            json={
                "attacker_id": attacker_id,
                "target_id": target_id,
                "attack_roll": 15,
                "modifier": 2
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "hit" in data
        assert data["attack_roll"] == 15
        assert data["modifier"] == 2
        assert data["total_attack"] == 17
    
    def test_damage_endpoint(self, authenticated_client: TestClient, test_combat_game: GameSession, test_characters: dict):
        """Нанесение урона через API"""
        game = test_combat_game
        char1 = test_characters["char1"]
        
        start_response = authenticated_client.post(
            f"/api/games/{game.id}/combat/start",
            json={"participant_ids": [str(char1.id)]}
        )
        combat_id = start_response.json()["id"]
        participant_id = start_response.json()["participants"][0]["id"]
        
        # Наносим урон
        response = authenticated_client.post(
            f"/api/games/{game.id}/combat/{combat_id}/damage",
            json={
                "target_id": participant_id,
                "damage": 5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["current_hp"] < data["max_hp"]
    
    def test_heal_endpoint(self, authenticated_client: TestClient, test_combat_game: GameSession, test_characters: dict):
        """Исцеление через API"""
        game = test_combat_game
        char1 = test_characters["char1"]
        
        start_response = authenticated_client.post(
            f"/api/games/{game.id}/combat/start",
            json={"participant_ids": [str(char1.id)]}
        )
        combat_id = start_response.json()["id"]
        participant_id = start_response.json()["participants"][0]["id"]
        
        # Сначала наносим урон
        authenticated_client.post(
            f"/api/games/{game.id}/combat/{combat_id}/damage",
            json={"target_id": participant_id, "damage": 10}
        )
        
        # Затем исцеляем
        response = authenticated_client.post(
            f"/api/games/{game.id}/combat/{combat_id}/heal",
            json={
                "target_id": participant_id,
                "healing": 5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["current_hp"] > 0

