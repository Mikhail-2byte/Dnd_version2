"""
Скрипт для создания тестовой игры с известным invite-кодом
Использование: python create_test_game.py
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


def create_test_user_and_game():
    """Создает тестового пользователя (мастера) и игру с известным invite-кодом"""
    db: Session = SessionLocal()
    
    try:
        # Проверяем, есть ли уже пользователь с таким email
        test_email = "test_master@example.com"
        test_username = "TestMaster"
        existing_user = db.query(User).filter(User.email == test_email).first()
        
        if existing_user:
            print(f"Пользователь {test_email} уже существует, используем его")
            master = existing_user
        else:
            # Создаем тестового пользователя (мастера)
            master = User(
                email=test_email,
                username=test_username,
                password_hash=get_password_hash("test123")
            )
            db.add(master)
            db.commit()
            db.refresh(master)
            print(f"Создан тестовый пользователь: {master.username} (ID: {master.id})")
            print(f"Email: {master.email}, Password: test123")
        
        # Проверяем, есть ли уже игра с таким invite-кодом
        test_invite_code = "TEST01"
        existing_game = db.query(GameSession).filter(
            GameSession.invite_code == test_invite_code
        ).first()
        
        if existing_game:
            print(f"\n[INFO] Игра с invite-кодом {test_invite_code} уже существует!")
            print(f"ID игры: {existing_game.id}")
            print(f"Название: {existing_game.name}")
            master_info = db.query(User).filter(User.id == existing_game.master_id).first()
            print(f"Мастер: {master_info.username if master_info else 'Unknown'} (ID: {existing_game.master_id})")
            print(f"=" * 50)
            print(f"\nДля подключения используйте invite-код: {test_invite_code}")
            print(f"Или перейдите по URL: http://localhost:5173/game/{existing_game.id}/lobby")
            print(f"\nДанные для входа в систему:")
            print(f"  Email: {master_info.email if master_info else 'N/A'}")
            print(f"  Password: test123")
            return existing_game
        
        # Создаем игру с известным invite-кодом
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
        participant = GameParticipant(
            game_id=game.id,
            user_id=master.id,
            role="master",
            is_ready=False  # Мастер по умолчанию не готов (но может быть готов сразу)
        )
        db.add(participant)
        db.commit()
        db.refresh(game)
        
        print(f"\n[OK] Тестовая игра успешно создана!")
        print(f"=" * 50)
        print(f"Название: {game.name}")
        print(f"Invite-код: {game.invite_code}")
        print(f"ID игры: {game.id}")
        print(f"Мастер: {master.username} (ID: {master.id})")
        print(f"=" * 50)
        print(f"\nДля подключения используйте invite-код: {test_invite_code}")
        print(f"Или перейдите по URL: http://localhost:5173/game/{game.id}/lobby")
        print(f"\nДанные для входа в систему:")
        print(f"  Email: {master.email}")
        print(f"  Password: test123")
        
        return game
        
    except Exception as e:
        db.rollback()
        print(f"Ошибка при создании тестовой игры: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Создание тестовой игры...")
    print("=" * 50)
    create_test_user_and_game()
    print("\nГотово!")
