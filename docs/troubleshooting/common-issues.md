# Частые ошибки

## Docker

### Ошибка: "Conflict. The container name is already in use"

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

### Ошибка: "Docker Desktop не запущен"

**Симптомы:**
```
error during connect: Get "http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/...": 
open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```

**Решение:**
1. Запустите Docker Desktop
2. Дождитесь полной загрузки (иконка станет зелёной)
3. Повторите команду

---

## Backend

### Ошибка: "Port already in use" (порт 8000)

**Симптомы:**
```
ERROR: [Errno 10048] error while attempting to bind on address ('0.0.0.0', 8000)
```

**Решение:**

Windows:
```powershell
netstat -ano | findstr :8000
```

Найдите PID процесса и завершите его:
```powershell
taskkill /PID <PID> /F
```

Или измените порт в `.env`:
```env
PORT=8001
```

### Ошибка: "ModuleNotFoundError"

**Симптомы:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Решение:**
1. Проверьте, что venv активирован (видно `(venv)` в начале строки)
2. Переустановите зависимости:
```bash
pip install -r requirements.txt
```

### Ошибка: "psycopg2.OperationalError"

**Симптомы:**
```
connection to server at "localhost" (127.0.0.1), port 5432 failed
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

### Ошибка: "SECRET_KEY not configured"

**Решение:**
```bash
python generate_secret_key.py
```

Скопируйте ключ в `.env` файл.

---

## Frontend

### Ошибка: "npm install" не работает

**Решение:**
```bash
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Ошибка: "Port already in use" (порт 5173)

**Решение:**

Windows:
```powershell
netstat -ano | findstr :5173
```

Завершите процесс или запустите на другом порту:
```bash
npm run dev -- --port 5174
```

### Ошибка: "WebSocket connection failed"

**Симптомы:**
- Кубики не синхронизируются
- Токены не перемещаются

**Решение:**
1. Проверьте, что backend запущен
2. Проверьте `VITE_WS_URL` в `.env`
3. Обновите страницу

---

## База данных

### Миграции не применяются

**Решение:**
```bash
alembic upgrade head
```

### Ошибка: "relation does not exist"

**Решение:**
```bash
alembic upgrade head
```

Если миграции уже применены, возможно нужно пересоздать таблицы:
```bash
alembic downgrade base
alembic upgrade head
```

---

## Socket.IO

### События не доходят

**Проверьте:**
1. WebSocket соединение установлено (вкладка Network → WS)
2. Токен аутентификации действителен
3. game_id правильный

### Переподключение

При разрыве соединения клиент автоматически пытается переподключиться. Если не удаётся — обновите страницу.

---

## Общие советы

| Проблема | Действие |
|----------|----------|
| Что-то не работает | Перезапустите все серверы |
| Ошибка в консоли | Смотрите логи сервера |
| Данные сброшены | Проверьте Docker volumes |
| Медленная работа | Проверьте ресурсы: `docker stats` |

---

## Логи

### Docker

```bash
docker-compose logs -f
```

### Backend

Логи выводятся в терминал при запуске `python run.py`.

### Frontend

Откройте DevTools (F12) → Console / Network

---

## Связаться с поддержкой

При обращении укажите:
1. Описание проблемы
2. Шаги воспроизведения
3. Логи ошибок
4. Скриншоты (если есть)