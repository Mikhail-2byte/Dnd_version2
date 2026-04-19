# Инструкция по установке и запуску проекта D&D Virtual Table

## Предварительные требования

Перед началом убедитесь, что у вас установлены:

1. **Python 3.11+**
   - Скачать: https://www.python.org/downloads/
   - При установке обязательно отметьте "Add Python to PATH"
   - Проверить: `python --version`

2. **Node.js 18+**
   - Скачать: https://nodejs.org/
   - Проверить: `node --version` и `npm --version`

3. **Docker Desktop**
   - Windows: https://www.docker.com/products/docker-desktop/
   - Linux/Mac: https://docs.docker.com/get-docker/
   - После установки запустите Docker Desktop и дождитесь полной загрузки
   - Проверить: `docker --version` и `docker-compose --version`

4. **Git** (опционально, если клонируете репозиторий)
   - Скачать: https://git-scm.com/downloads

---

## Шаг 1: Подготовка проекта

### 1.1. Перейдите в папку проекта

```bash
cd C:\Projeck\Dungeons_dragons
```

### 1.2. Убедитесь, что Docker Desktop запущен

**ВАЖНО:** Docker Desktop должен быть запущен перед выполнением команд!

- Найдите Docker Desktop в меню Пуск и запустите его
- Дождитесь, пока иконка Docker в системном трее станет зеленой
- Это может занять 1-2 минуты при первом запуске

Проверьте работу Docker:
```bash
docker ps
```
Должно вернуться содержимое БЕЗ ошибок.

---

## Шаг 2: Запуск баз данных

### 2.1. Очистка старых контейнеров (если они существуют)

Если вы ранее запускали проект, выполните:

```bash
docker-compose down
```

### 2.2. Запуск PostgreSQL и Redis

```bash
docker-compose up -d
```

**Ожидаемый результат:**
```
[+] Running 2/2
 ✔ Container dnd_postgres  Started
 ✔ Container dnd_redis     Started
```

### 2.3. Проверка статуса контейнеров

```bash
docker-compose ps
```

**Ожидаемый результат:**
```
NAME            IMAGE                STATUS
dnd_postgres    postgres:15-alpine   Up (healthy)
dnd_redis       redis:7-alpine       Up (healthy)
```

---

## Шаг 3: Настройка Backend

### 3.1. Переход в папку backend

```bash
cd backend
```

### 3.2. Создание виртуального окружения Python

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

**Важно:** Если появилась ошибка о политике выполнения скриптов в PowerShell:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Признак успешной активации:** В начале строки появится `(venv)`:
```
(venv) PS C:\Projeck\Dungeons_dragons\backend>
```

### 3.3. Установка зависимостей Python

```bash
pip install -r requirements.txt
```

Это может занять несколько минут. Дождитесь завершения установки.

**Если появилась ошибка "email-validator is not installed":**
```bash
pip install email-validator
```

### 3.4. Создание файла .env

Создайте файл `.env` в папке `backend` со следующим содержимым:

```env
# Database
DATABASE_URL=postgresql://dnd_user:dnd_password@localhost:5432/dnd_db

# Redis
REDIS_URL=redis://localhost:6379

# JWT
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server
HOST=0.0.0.0
PORT=8000

# Uploads
UPLOAD_DIR=uploads
MAPS_DIR=uploads/maps
MAX_UPLOAD_SIZE=10485760

# Logging
LOG_LEVEL=INFO
```

### 3.5. Генерация SECRET_KEY

**Windows PowerShell:**
```powershell
$key = python generate_secret_key.py
(Get-Content .env) -replace 'your-secret-key-here-change-in-production', $key.Trim() | Set-Content .env
```

**Linux/Mac:**
```bash
KEY=$(python generate_secret_key.py)
sed -i "s/your-secret-key-here-change-in-production/$KEY/g" .env
```

**Или вручную:**
1. Выполните: `python generate_secret_key.py`
2. Скопируйте сгенерированный ключ
3. Откройте файл `.env` в текстовом редакторе
4. Замените `your-secret-key-here-change-in-production` на сгенерированный ключ
5. Сохраните файл

### 3.6. Применение миграций базы данных

```bash
alembic upgrade head
```

**Ожидаемый результат:**
```
INFO  [alembic.runtime.migration] Running upgrade  -> e7dfa838beb2, Initial migration
```

---

## Шаг 4: Запуск Backend

### 4.1. Убедитесь, что виртуальное окружение активировано

Если в начале строки нет `(venv)`, активируйте окружение (см. шаг 3.2).

### 4.2. Убедитесь, что базы данных запущены

В другом окне терминала проверьте:
```bash
cd C:\Projeck\Dungeons_dragons
docker-compose ps
```

Оба контейнера должны быть в статусе "Up".

### 4.3. Запуск Backend сервера

```bash
python run.py
```

**Ожидаемый результат:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Важно:** Оставьте это окно открытым! Сервер должен работать постоянно.

### 4.4. Проверка работы Backend

Откройте браузер и перейдите по адресам:

- `http://localhost:8000/health` - должен вернуть `{"status": "ok"}`
- `http://localhost:8000/docs` - должна открыться Swagger документация API

---

## Шаг 5: Настройка Frontend

### 5.1. Откройте новое окно терминала

**Важно:** Backend должен продолжать работать в первом окне!

### 5.2. Переход в папку frontend

```bash
cd C:\Projeck\Dungeons_dragons\frontend
```

### 5.3. Установка зависимостей Node.js

```bash
npm install
```

Это может занять несколько минут при первом запуске. Дождитесь завершения.

### 5.4. Создание файла .env

Создайте файл `.env` в папке `frontend` со следующим содержимым:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=http://localhost:8000
```

---

## Шаг 6: Запуск Frontend

### 6.1. Запуск dev-сервера

```bash
npm run dev
```

**Ожидаемый результат:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

**Важно:** Оставьте это окно открытым! Frontend сервер должен работать постоянно.

### 6.2. Открытие приложения в браузере

Откройте браузер и перейдите по адресу:

**http://localhost:5173**

Должна загрузиться страница регистрации/входа.

---

## Быстрый запуск (после первоначальной настройки)

Если проект уже настроен, для запуска выполните в **трех отдельных окнах терминала**:

### Окно 1: Базы данных
```bash
cd C:\Projeck\Dungeons_dragons
docker-compose up -d
```

### Окно 2: Backend
```bash
cd C:\Projeck\Dungeons_dragons\backend
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/Mac:
# source venv/bin/activate
python run.py
```

### Окно 3: Frontend
```bash
cd C:\Projeck\Dungeons_dragons\frontend
npm run dev
```

Затем откройте `http://localhost:5173` в браузере.

---

## Использование приложения

1. **Регистрация:**
   - Введите email, username и password
   - Нажмите "Зарегистрироваться"

2. **Создание игры:**
   - После входа нажмите "Создать игру"
   - Введите название игры
   - Скопируйте invite-код

3. **Присоединение к игре:**
   - В другом окне браузера (или инкогнито) зарегистрируйте второго пользователя
   - Введите invite-код и нажмите "Присоединиться"

4. **Игра:**
   - Мастер может перетаскивать токены на карте
   - Все изменения синхронизируются в реальном времени между всеми игроками

---

## Создание тестовых данных

Для быстрого тестирования можно создать тестовую игру:

```bash
cd backend
# Windows:
.\venv\Scripts\python.exe create_test_game.py
# Linux/Mac:
# source venv/bin/activate
# python create_test_game.py
```

Скрипт создаст:
- **Мастера**: `test_master@example.com` / `test123`
- **Игру** с invite-кодом `TEST01`

---

## Решение проблем

### Проблема: "Conflict. The container name is already in use"

**Решение:**
```bash
docker-compose down
docker-compose up -d
```

Если не помогло:
```bash
docker rm -f dnd_postgres dnd_redis
docker-compose up -d
```

### Проблема: "Docker Desktop не запущен"

**Симптомы:**
```
error during connect: Get "http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/...": 
open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```

**Решение:**
1. Запустите Docker Desktop из меню Пуск
2. Дождитесь полной загрузки (иконка в трее должна стать зеленой)
3. Попробуйте снова: `docker-compose up -d`

### Проблема: "Политика выполнения скриптов" (Windows PowerShell)

**Симптомы:**
```
.\venv\Scripts\Activate.ps1 : Невозможно загрузить файл, так как выполнение скриптов 
отключено в данной системе.
```

**Решение:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Затем снова активируйте окружение.

### Проблема: "Порт уже занят"

**Симптомы:**
```
ERROR:    [Errno 10048] error while attempting to bind on address ('0.0.0.0', 8000): 
only one usage of each socket address (protocol/network address/port) is normally permitted
```

**Решение:**
1. Найдите процесс, занимающий порт:
   ```powershell
   # Windows:
   netstat -ano | findstr :8000
   # Linux/Mac:
   # lsof -i :8000
   ```
2. Завершите процесс или измените порт в `backend/app/config.py` или `.env`

### Проблема: "ModuleNotFoundError"

**Симптомы:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Решение:**
1. Убедитесь, что виртуальное окружение активировано (видно `(venv)` в начале строки)
2. Переустановите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

### Проблема: "Ошибка подключения к БД"

**Симптомы:**
```
psycopg2.OperationalError: connection to server at "localhost" (127.0.0.1), port 5432 failed
```

**Решение:**
1. Проверьте, что Docker Desktop запущен
2. Проверьте статус контейнеров:
   ```bash
   docker-compose ps
   ```
3. Если контейнеры не запущены:
   ```bash
   docker-compose up -d
   ```
4. Проверьте `DATABASE_URL` в `backend/.env` файле

### Проблема: "npm install" не работает

**Решение:**
1. Убедитесь, что Node.js установлен: `node --version`
2. Очистите кеш npm:
   ```bash
   npm cache clean --force
   ```
3. Удалите папку `node_modules` и файл `package-lock.json`, затем:
   ```bash
   npm install
   ```

---

## Остановка приложения

### Остановка Frontend и Backend

В окнах терминала, где запущены серверы, нажмите `Ctrl + C`

### Остановка баз данных

```bash
cd C:\Projeck\Dungeons_dragons
docker-compose down
```

**ОСТОРОЖНО:** Для полного удаления данных (включая базу данных):

```bash
docker-compose down -v
```

---

## Проверка работоспособности

После запуска всех компонентов проверьте:

1. **Docker контейнеры:**
   ```bash
   docker-compose ps
   ```
   Оба контейнера должны быть в статусе "Up (healthy)"

2. **Backend:**
   - Откройте `http://localhost:8000/health` - должен вернуть `{"status": "ok"}`
   - Откройте `http://localhost:8000/docs` - должна открыться Swagger документация

3. **Frontend:**
   - Откройте `http://localhost:5173` - должна загрузиться страница регистрации/входа

---

## Полезные команды

### Просмотр логов Docker контейнеров

```bash
docker-compose logs -f
```

### Перезапуск контейнеров

```bash
docker-compose restart
```

### Просмотр использования ресурсов

```bash
docker stats
```

### Очистка неиспользуемых образов Docker

```bash
docker system prune -a
```

---

## Дополнительная информация

- **Backend API:** http://localhost:8000/docs
- **Frontend:** http://localhost:5173
- **Health Check:** http://localhost:8000/health

При возникновении проблем проверьте логи в окнах терминала, где запущены серверы.
