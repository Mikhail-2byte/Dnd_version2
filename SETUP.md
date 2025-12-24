# Инструкция по установке и запуску

> **Для пользователей Windows:** См. [SETUP_WINDOWS.md](./SETUP_WINDOWS.md) - подробная пошаговая инструкция с командами PowerShell и решением проблем.

## Предварительные требования

- Python 3.11+
- Node.js 18+
- Docker и Docker Compose
- Git

## Краткая инструкция (для тех, кто уже настраивал проект)

Если проект уже настроен, для запуска выполните:

```bash
# 1. Запустить базы данных
docker-compose up -d

# 2. Запустить Backend (в отдельном терминале)
cd backend
# Windows:
venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate
python run.py

# 3. Запустить Frontend (в отдельном терминале)
cd frontend
npm run dev
```

Откройте `http://localhost:5173` в браузере.

---

## Полная инструкция по установке (первый запуск)

## Шаг 1: Запуск баз данных

```bash
# Запустить PostgreSQL и Redis
docker-compose up -d

# Проверить статус
docker-compose ps
```

## Шаг 2: Настройка Backend

```bash
cd backend

# Создать виртуальное окружение
python -m venv venv

# Активировать виртуальное окружение
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt

# Создать .env файл из шаблона
copy .env.example .env
# Linux/Mac: cp .env.example .env

# Сгенерировать безопасный SECRET_KEY для JWT
python generate_secret_key.py
# Скопируйте сгенерированный ключ и вставьте его в .env файл вместо "your-secret-key-here-change-in-production"
# Или в Windows PowerShell:
# (Get-Content .env) -replace 'your-secret-key-here-change-in-production', 'ВАШ_СГЕНЕРИРОВАННЫЙ_КЛЮЧ' | Set-Content .env

# Применить миграции базы данных
# Миграция уже создана, нужно только применить её
alembic upgrade head
```

## Шаг 3: Запуск Backend

```bash
# Убедитесь, что виртуальное окружение активировано
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Из папки backend с активированным venv
python run.py

# Или через uvicorn напрямую:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Важно:** Убедитесь, что PostgreSQL и Redis запущены перед запуском backend!

Backend будет доступен на `http://localhost:8000`

API документация: `http://localhost:8000/docs`

## Шаг 4: Настройка Frontend

```bash
cd frontend

# Установить зависимости
npm install

# Создать .env файл
copy .env.example .env
# Linux/Mac: cp .env.example .env

# Отредактировать .env при необходимости (по умолчанию должно работать)
```

## Шаг 5: Запуск Frontend

```bash
# Из папки frontend
npm run dev
```

Frontend будет доступен на `http://localhost:5173`

## Использование

1. Откройте `http://localhost:5173` в браузере
2. Зарегистрируйте новый аккаунт
3. Создайте игру или присоединитесь по invite-коду
4. Мастер может перетаскивать токены на карте
5. Все изменения синхронизируются в реальном времени

## Структура базы данных

После применения миграций будут созданы следующие таблицы:
- `users` - пользователи
- `game_sessions` - игровые сессии
- `game_participants` - участники игр
- `tokens` - токены на карте

## Решение проблем

### Ошибка подключения к БД

Проверьте, что PostgreSQL запущен:
```bash
docker-compose ps
```

Проверьте переменные в `.env` файле backend.

### Ошибка подключения к Redis

Проверьте, что Redis запущен:
```bash
docker-compose ps
```

### Порт уже занят

Измените порты в:
- Backend: `backend/app/config.py` или `.env`
- Frontend: `frontend/vite.config.ts`

### Миграции не применяются

Убедитесь, что:
1. PostgreSQL запущен через `docker-compose up -d`
2. База данных создана (создается автоматически при первом запуске контейнера)
3. Переменная `DATABASE_URL` в `.env` правильная и соответствует настройкам docker-compose.yml
4. Пользователь БД имеет права на создание таблиц

### Ошибка "ModuleNotFoundError" при запуске

Убедитесь, что:
1. Виртуальное окружение активировано
2. Все зависимости установлены: `pip install -r requirements.txt`

### Ошибка "SECRET_KEY" не найден

Убедитесь, что:
1. Файл `.env` создан из `.env.example`
2. В `.env` файле установлен правильный `SECRET_KEY` (сгенерируйте через `python generate_secret_key.py`)

## Остановка

```bash
# Остановить контейнеры (PostgreSQL и Redis)
docker-compose down

# Остановить с удалением данных (ОСТОРОЖНО! Удалит все данные из БД)
docker-compose down -v
```

**Примечание:** Остановка контейнеров не останавливает backend и frontend серверы. Остановите их вручную (Ctrl+C в терминалах).

## Проверка работоспособности

После запуска всех компонентов проверьте:

1. **Backend работает:**
   - Откройте `http://localhost:8000/health` - должен вернуть `{"status": "ok"}`
   - Откройте `http://localhost:8000/docs` - должна открыться Swagger документация

2. **Frontend работает:**
   - Откройте `http://localhost:5173` - должна загрузиться страница регистрации/входа

3. **Базы данных работают:**
   ```bash
   docker-compose ps
   # Оба контейнера должны быть в статусе "Up"
   ```

