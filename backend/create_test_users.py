"""
Скрипт для создания тестовых пользователей (мастера и игрока)
Использование: python create_test_users.py

Создает:
- Тестового мастера (test_master@example.com)
- Тестового игрока (test_player@example.com)
- Тестовую игру с invite-кодом TEST01
"""
import sys
import os
from pathlib import Path

# Добавляем путь к app
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

# Загружаем переменные окружения
from dotenv import load_dotenv
env_path = backend_path / '.env'
if env_path.exists():
    load_dotenv(env_path)

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.models.game_session import GameSession
from app.models.game_participant import GameParticipant
from app.utils.security import get_password_hash


def create_test_users_and_game():
    """Создает тестовых пользователей и игру"""
    db: Session = SessionLocal()
    
    try:
        print("Создание тестовых пользователей и игры...")
        print("=" * 60)
        
        # Создаем или получаем тестового мастера
        test_master_email = "test_master@example.com"
        test_master_username = "TestMaster"
        existing_master = db.query(User).filter(User.email == test_master_email).first()
        
        if existing_master:
            print(f"[INFO] Пользователь {test_master_email} уже существует")
            master = existing_master
        else:
            master = User(
                email=test_master_email,
                username=test_master_username,
                password_hash=get_password_hash("test123")
            )
            db.add(master)
            db.commit()
            db.refresh(master)
            print(f"[OK] Создан тестовый мастер: {master.username}")
        
        # Создаем или получаем тестового игрока
        test_player_email = "test_player@example.com"
        test_player_username = "TestPlayer"
        existing_player = db.query(User).filter(User.email == test_player_email).first()
        
        if existing_player:
            print(f"[INFO] Пользователь {test_player_email} уже существует")
            player = existing_player
        else:
            player = User(
                email=test_player_email,
                username=test_player_username,
                password_hash=get_password_hash("test123")
            )
            db.add(player)
            db.commit()
            db.refresh(player)
            print(f"[OK] Создан тестовый игрок: {player.username}")
        
        # Создаем или получаем тестовую игру
        test_invite_code = "TEST01"
        existing_game = db.query(GameSession).filter(
            GameSession.invite_code == test_invite_code
        ).first()
        
        if existing_game:
            print(f"\n[INFO] Игра с invite-кодом {test_invite_code} уже существует")
            game = existing_game
            
            # Проверяем, является ли игрок участником
            existing_participant = db.query(GameParticipant).filter(
                GameParticipant.game_id == game.id,
                GameParticipant.user_id == player.id
            ).first()
            
            if not existing_participant:
                # Добавляем игрока как участника
                participant = GameParticipant(
                    game_id=game.id,
                    user_id=player.id,
                    role="player",
                    is_ready=False
                )
                db.add(participant)
                db.commit()
                print(f"[OK] Игрок {player.username} добавлен в игру")
        else:
            # Создаем новую игру
            game = GameSession(
                name="Подземелья Дракона",
                invite_code=test_invite_code,
                master_id=master.id,
                story="Классическое приключение в темных подземельях, где хранятся древние сокровища и обитает могучий дракон. Отважные герои должны пройти через опасные ловушки и сразиться с монстрами.",
                map_url="/assets/images/dnd-map.jpg"
            )
            db.add(game)
            db.flush()
            
            # Добавляем мастера как участника
            master_participant = GameParticipant(
                game_id=game.id,
                user_id=master.id,
                role="master",
                is_ready=False
            )
            db.add(master_participant)
            
            # Добавляем игрока как участника
            player_participant = GameParticipant(
                game_id=game.id,
                user_id=player.id,
                role="player",
                is_ready=False
            )
            db.add(player_participant)
            db.commit()
            db.refresh(game)
            print(f"\n[OK] Создана тестовая игра: {game.name}")
        
        # Выводим итоговую информацию
        print("\n" + "=" * 60)
        print("ДАННЫЕ ДЛЯ ТЕСТИРОВАНИЯ")
        print("=" * 60)
        print("\n1. МАСТЕР (первая вкладка браузера):")
        print(f"   Email: {master.email}")
        print(f"   Password: test123")
        print(f"   URL: http://localhost:5173/")
        print(f"   После входа перейти: http://localhost:5173/game/{game.id}/lobby")
        
        print("\n2. ИГРОК (вторая вкладка браузера):")
        print(f"   Email: {player.email}")
        print(f"   Password: test123")
        print(f"   URL: http://localhost:5173/")
        print(f"   После входа:")
        print(f"   - Нажать 'Присоединиться'")
        print(f"   - Ввести invite-код: {test_invite_code}")
        print(f"   - Или перейти: http://localhost:5173/game/{game.id}/lobby")
        
        print(f"\n3. ИНФОРМАЦИЯ ОБ ИГРЕ:")
        print(f"   Название: {game.name}")
        print(f"   Invite-код: {test_invite_code}")
        print(f"   ID игры: {game.id}")
        
        print("\n" + "=" * 60)
        print("ИНСТРУКЦИЯ ПО ТЕСТИРОВАНИЮ")
        print("=" * 60)
        print("1. Откройте первую вкладку браузера")
        print("2. Войдите как мастер (test_master@example.com / test123)")
        print("3. Перейдите в лобби игры")
        print("4. Откройте вторую вкладку браузера в режиме инкогнито")
        print("5. Войдите как игрок (test_player@example.com / test123)")
        print("6. Присоединитесь к игре по invite-коду TEST01")
        print("7. В обеих вкладках вы увидите обновления в реальном времени")
        print("=" * 60)
        
        return {
            "master": master,
            "player": player,
            "game": game,
            "invite_code": test_invite_code
        }
        
    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Ошибка при создании тестовых данных: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_test_users_and_game()
    print("\nГотово!")
