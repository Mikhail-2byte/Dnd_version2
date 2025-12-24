# Подробная инструкция по установке и запуску на Windows

## Предварительные требования

Перед началом убедитесь, что у вас установлены:

1. **Python 3.11+**
   - Скачать: https://www.python.org/downloads/
   - При установке обязательно отметьте "Add Python to PATH"
   - Проверить: `python --version` в PowerShell

2. **Node.js 18+**
   - Скачать: https://nodejs.org/
   - Проверить: `node --version` и `npm --version` в PowerShell

3. **Docker Desktop для Windows**
   - Скачать: https://www.docker.com/products/docker-desktop/
   - После установки запустите Docker Desktop и дождитесь полной загрузки
   - Проверить: `docker --version` и `docker-compose --version` в PowerShell

4. **Git** (опционально, если клонируете репозиторий)
   - Скачать: https://git-scm.com/download/win

---

## Шаг 1: Подготовка проекта

### 1.1. Откройте PowerShell

Нажмите `Win + X` и выберите "Windows PowerShell" или "Терминал", или найдите PowerShell в меню Пуск.

### 1.2. Перейдите в папку проекта

```powershell
cd C:\Projeck\Dungeons_dragons
```

Если проект находится в другом месте, укажите правильный путь.

---

## Шаг 2: Запуск Docker Desktop и баз данных

### 2.1. Проверка Docker Desktop

**ВАЖНО:** Docker Desktop должен быть запущен перед выполнением команд!

1. Найдите Docker Desktop в меню Пуск и запустите его
2. Дождитесь, пока иконка Docker в системном трее (справа внизу) станет зеленой
3. Это может занять 1-2 минуты при первом запуске

### 2.2. Проверка работы Docker

Выполните в PowerShell:

```powershell
docker --version
docker-compose --version
```

Оба должны вернуть версии без ошибок.

### 2.3. Очистка старых контейнеров (если они существуют)

**ВАЖНО:** Если вы ранее запускали проект, старые контейнеры могут мешать. Выполните очистку:

```powershell
docker-compose down
```

Эта команда остановит и удалит существующие контейнеры, но сохранит данные в volumes.

**Если появилась ошибка "Conflict. The container name is already in use":**

Выполните принудительное удаление контейнеров:

```powershell
# Сначала попробуйте стандартную очистку
docker-compose down

# Если контейнеры все еще существуют, удалите их вручную
docker rm -f dnd_postgres dnd_redis

# Проверьте, что контейнеры удалены
docker ps -a | Select-String "dnd_postgres|dnd_redis"
# Должно быть пусто (или контейнеры должны отсутствовать)

# Затем снова запустите
docker-compose up -d
```

**Примечание:** Если вы хотите сохранить данные БД, используйте `docker-compose down` (без `-v`). Если нужно начать с чистой БД, используйте `docker-compose down -v`.

### 2.4. Запуск баз данных (PostgreSQL и Redis)

В PowerShell выполните:

```powershell
docker-compose up -d
```

**Что происходит:**
- Скачиваются образы PostgreSQL и Redis (при первом запуске, может занять несколько минут)
- Создаются и запускаются контейнеры с базами данных

**Ожидаемый результат:**
```
[+] Running 2/2
 ✔ Container dnd_postgres  Started
 ✔ Container dnd_redis     Started
```

**Если появилась ошибка:**
```
Error response from daemon: Conflict. The container name "/dnd_postgres" is already in use
```

См. решение в шаге 2.3 выше.

### 2.5. Проверка статуса контейнеров

```powershell
docker-compose ps
```

**Ожидаемый результат:**
```
NAME            IMAGE                STATUS
dnd_postgres    postgres:15-alpine   Up (healthy)
dnd_redis       redis:7-alpine       Up (healthy)
```

Если контейнеры не запустились, см. раздел "Решение проблем" ниже.

---

## Шаг 3: Настройка Backend

### 3.1. Переход в папку backend

```powershell
cd backend
```

### 3.2. Создание виртуального окружения Python

```powershell
python -m venv venv
```

Это создаст папку `venv` с изолированным окружением Python.

### 3.3. Активация виртуального окружения

```powershell
.\venv\Scripts\Activate.ps1
```

**Важно:** Если появилась ошибка о политике выполнения скриптов, выполните:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Затем снова активируйте окружение:

```powershell
.\venv\Scripts\Activate.ps1
```

**Признак успешной активации:** В начале строки PowerShell появится `(venv)`:
```
(venv) PS C:\Projeck\Dungeons_dragons\backend>
```

### 3.4. Установка зависимостей Python

```powershell
pip install -r requirements.txt
```

Это может занять несколько минут. Дождитесь завершения установки.

**Если при запуске появилась ошибка "email-validator is not installed":**

Выполните дополнительную установку:

```powershell
pip install email-validator
```

Или переустановите зависимости:

```powershell
pip install -r requirements.txt
```

### 3.5. Создание файла .env

```powershell
Copy-Item .env.example .env
```

### 3.6. Генерация SECRET_KEY

```powershell
python generate_secret_key.py
```

**Результат:** В консоли появится строка вида `RA5A57NM4ETRPODUY2JvbNz0k7ig1TXSgvpiinHJgs4`

Скопируйте эту строку (выделите и нажмите Enter, или щелкните правой кнопкой мыши).

### 3.7. Установка SECRET_KEY в .env файл

**Способ 1 (автоматический):**

Выполните команду, заменив `ВАШ_СГЕНЕРИРОВАННЫЙ_КЛЮЧ` на ключ из предыдущего шага:

```powershell
$key = python generate_secret_key.py
(Get-Content .env) -replace 'your-secret-key-here-change-in-production', $key.Trim() | Set-Content .env
```

**Способ 2 (ручной):**

1. Откройте файл `.env` в любом текстовом редакторе (Notepad, VS Code)
2. Найдите строку: `SECRET_KEY=your-secret-key-here-change-in-production`
3. Замените `your-secret-key-here-change-in-production` на сгенерированный ключ
4. Сохраните файл

### 3.8. Применение миграций базы данных

```powershell
alembic upgrade head
```

**Ожидаемый результат:**
```
INFO  [alembic.runtime.migration] Running upgrade  -> e7dfa838beb2, Initial migration
```

Если появилась ошибка подключения к БД, убедитесь, что:
- Docker Desktop запущен
- Контейнеры запущены (`docker-compose ps`)
- В `.env` файле правильный `DATABASE_URL`

---

## Шаг 4: Запуск Backend

### 4.1. Убедитесь, что виртуальное окружение активировано

Если в начале строки нет `(venv)`, активируйте окружение:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4.2. Убедитесь, что все зависимости установлены

Если при запуске появилась ошибка "email-validator is not installed", установите недостающий пакет:

```powershell
pip install email-validator
```

Или переустановите все зависимости:

```powershell
pip install -r requirements.txt
```

### 4.3. Убедитесь, что базы данных запущены

В другом окне PowerShell (или в этом же, но в фоновом режиме) проверьте:

```powershell
cd C:\Projeck\Dungeons_dragons
docker-compose ps
```

Оба контейнера должны быть в статусе "Up".

### 4.4. Запуск Backend сервера

```powershell
python run.py
```

**Ожидаемый результат:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Важно:** Оставьте это окно PowerShell открытым! Сервер должен работать постоянно.

### 4.4. Проверка работы Backend

Откройте браузер и перейдите по адресам:

- `http://localhost:8000/health` - должен вернуть `{"status": "ok"}`
- `http://localhost:8000/docs` - должна открыться Swagger документация API

---

## Шаг 5: Настройка Frontend

### 5.1. Откройте новое окно PowerShell

**Важно:** Backend должен продолжать работать в первом окне PowerShell!

### 5.2. Переход в папку frontend

```powershell
cd C:\Projeck\Dungeons_dragons\frontend
```

### 5.3. Установка зависимостей Node.js

```powershell
npm install
```

Это может занять несколько минут при первом запуске. Дождитесь завершения.

### 5.4. Создание файла .env

```powershell
Copy-Item .env.example .env
```

Файл `.env` уже должен содержать правильные значения по умолчанию, но можно проверить и отредактировать при необходимости.

---

## Шаг 6: Запуск Frontend

### 6.1. Запуск dev-сервера

```powershell
npm run dev
```

**Ожидаемый результат:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

**Важно:** Оставьте это окно PowerShell открытым! Frontend сервер должен работать постоянно.

### 6.2. Открытие приложения в браузере

Откройте браузер и перейдите по адресу:

**http://localhost:5173**

Должна загрузиться страница регистрации/входа.

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

## Быстрый запуск (после первоначальной настройки)

Если проект уже настроен, для запуска выполните в **трех отдельных окнах PowerShell**:

### Окно 1: Базы данных
```powershell
cd C:\Projeck\Dungeons_dragons
docker-compose up -d
```

### Окно 2: Backend
```powershell
cd C:\Projeck\Dungeons_dragons\backend
.\venv\Scripts\Activate.ps1
python run.py
```

### Окно 3: Frontend
```powershell
cd C:\Projeck\Dungeons_dragons\frontend
npm run dev
```

Затем откройте `http://localhost:5173` в браузере.

---

## Решение проблем

### Проблема: "Conflict. The container name is already in use"

**Симптомы:**
```
Error response from daemon: Conflict. The container name "/dnd_postgres" is already in use 
by container "71ec669dbbf9...". You have to remove (or rename) that container to be able to reuse that name.
```

**Решение:**

1. **Способ 1 (рекомендуемый):**
   ```powershell
   docker-compose down
   docker-compose up -d
   ```

2. **Способ 2 (если способ 1 не помог):**
   ```powershell
   # Удалить контейнеры вручную
   docker rm -f dnd_postgres dnd_redis
   
   # Запустить заново
   docker-compose up -d
   ```

3. **Способ 3 (полная очистка, удалит все данные БД!):**
   ```powershell
   docker-compose down -v
   docker-compose up -d
   ```
   ⚠️ **ВНИМАНИЕ:** Это удалит все данные из базы данных!

### Проблема: "Docker Desktop не запущен" или "unable to get image"

**Симптомы:**
```
error during connect: Get "http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/v1.51/...": 
open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```

**Решение:**
1. Запустите Docker Desktop из меню Пуск
2. Дождитесь полной загрузки (иконка в трее должна стать зеленой)
3. Попробуйте снова: `docker-compose up -d`

### Проблема: "Политика выполнения скриптов"

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
   netstat -ano | findstr :8000
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
   ```powershell
   pip install -r requirements.txt
   ```

### Проблема: "email-validator is not installed"

**Симптомы:**
```
ImportError: email-validator is not installed, run `pip install pydantic[email]`
```

**Решение:**
```powershell
pip install email-validator
```

Или переустановите все зависимости:
```powershell
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
   ```powershell
   docker-compose ps
   ```
3. Если контейнеры не запущены:
   ```powershell
   docker-compose up -d
   ```
4. Проверьте `DATABASE_URL` в `backend/.env` файле

### Проблема: "npm install" не работает

**Симптомы:**
```
npm ERR! code ENOENT
```

**Решение:**
1. Убедитесь, что Node.js установлен: `node --version`
2. Очистите кеш npm:
   ```powershell
   npm cache clean --force
   ```
3. Удалите папку `node_modules` и файл `package-lock.json`, затем:
   ```powershell
   npm install
   ```

### Проблема: Контейнеры не запускаются

**Решение:**
1. Проверьте логи:
   ```powershell
   docker-compose logs
   ```
2. Пересоздайте контейнеры:
   ```powershell
   docker-compose down
   docker-compose up -d
   ```

---

## Остановка приложения

### Остановка Frontend и Backend

В окнах PowerShell, где запущены серверы, нажмите `Ctrl + C`

### Остановка баз данных

```powershell
cd C:\Projeck\Dungeons_dragons
docker-compose down
```

**ОСТОРОЖНО:** Для полного удаления данных (включая базу данных):

```powershell
docker-compose down -v
```

---

## Проверка работоспособности

После запуска всех компонентов проверьте:

1. **Docker контейнеры:**
   ```powershell
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

```powershell
docker-compose logs -f
```

### Перезапуск контейнеров

```powershell
docker-compose restart
```

### Просмотр использования ресурсов

```powershell
docker stats
```

### Очистка неиспользуемых образов Docker

```powershell
docker system prune -a
```

---

## Дополнительная информация

- **Backend API:** http://localhost:8000/docs
- **Frontend:** http://localhost:5173
- **Health Check:** http://localhost:8000/health

При возникновении проблем проверьте логи в окнах PowerShell, где запущены серверы.

