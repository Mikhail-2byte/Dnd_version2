# Запуск dev-серверов

Для запуска приложения необходимо запустить три компонента в отдельных терминалах.

## Быстрый запуск

Выполните в трёх отдельных окнах терминала:

### Окно 1: Базы данных

```bash
docker-compose up -d
```

### Окно 2: Backend

```bash
cd backend

# Активация venv
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/Mac:
# source venv/bin/activate

# Запуск сервера
python run.py
```

Ожидаемый результат:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Окно 3: Frontend

```bash
cd frontend
npm run dev
```

Ожидаемый результат:
```
  VITE v5.x.x  ready in xxx ms
  ➜  Local:   http://localhost:5173/
```

---

## Доступные URL

После запуска:

| Сервис | URL | Описание |
|--------|-----|----------|
| Frontend | http://localhost:5173 | Приложение |
| Backend | http://localhost:8000 | API |
| API Docs | http://localhost:8000/docs | Swagger |
| Health | http://localhost:8000/health | Проверка статуса |

---

## Остановка серверов

В каждом окне терминала нажмите `Ctrl + C`.

Базы данных:
```bash
docker-compose down
```

---

## Следующие шаги

- [Первая игра](first-game.md) — зарегистрировать пользователей, создать игру

## Ссылки

- [Установка](installation.md) — если нужно настроить окружение с нуля