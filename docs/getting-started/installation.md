# Установка и настройка окружения

## Предварительные требования

Перед началом убедитесь, что установлены все необходимые инструменты.

### Python 3.11+

Скачать: https://www.python.org/downloads/

При установке обязательно отметьте "Add Python to PATH".

Проверить версию:
```bash
python --version
```

### Node.js 18+

Скачать: https://nodejs.org/

Проверить версию:
```bash
node --version
npm --version
```

### Docker Desktop

Скачать: https://www.docker.com/products/docker-desktop/

После установки запустите Docker Desktop и дождитесь полной загрузки (иконка в трее станет зелёной).

Проверить версию:
```bash
docker --version
docker-compose --version
```

---

## Шаг 1: Клонирование репозитория

```bash
git clone <репозиторий>
cd <папка-проекта>
```

---

## Шаг 2: Запуск баз данных

### Запуск контейнеров

```bash
docker-compose up -d
```

Ожидаемый результат:
```
[+] Running 2/2
 ✔ Container dnd_postgres  Started
 ✔ Container dnd_redis     Started
```

### Проверка статуса

```bash
docker-compose ps
```

Оба контейнера должны быть в статусе "Up (healthy)":
```
NAME       IMAGE            STATUS
dnd_postgres  postgres:15-alpine   Up (healthy)
dnd_redis     redis:7-alpine    Up (healthy)
```

### Остановка

```bash
docker-compose down
```

Для удаления данных:
```bash
docker-compose down -v
```

---

## Шаг 3: Настройка Backend

### Создание виртуального окружения

```bash
cd backend
python -m venv venv
```

**Windows:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

Признак успешной активации — `(venv)` в начале строки.

### Установка зависимостей

```bash
pip install -r requirements.txt
```

### Создание файла .env

Создайте файл `backend/.env`:

```env
# Database
DATABASE_URL=postgresql://dnd_user:dnd_password@localhost:5432/dnd_db

# Redis
REDIS_URL=redis://localhost:6379

# JWT
SECRET_KEY=<сгенерируйте-ключ>
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

### Генерация SECRET_KEY

```bash
python generate_secret_key.py
```

Скопируйте сгенерированный ключ в `SECRET_KEY` в файле `.env`.

### Применение миграций

```bash
alembic upgrade head
```

Ожидаемый результат:
```
INFO  [alembic.runtime.migration] Running upgrade  -> <миграция>, Initial migration
```

---

## Шаг 4: Настройка Frontend

### Установка зависимостей

```bash
cd frontend
npm install
```

### Создание файла .env

Создайте файл `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=http://localhost:8000
```

---

## Проверка установки

После настройки всех компонентов:

| Компонент | URL | Ожидаемый ответ |
|-----------|-----|-----------------|
| Backend | http://localhost:8000/health | `{"status": "ok"}` |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Frontend | http://localhost:5173 | Страница регистрации |

---

## Следующие шаги

- [Запуск dev-серверов](quick-start.md)
- [Первая игра](first-game.md)