# Production развёртывание

## Требования

- Docker
- Docker Compose
- Nginx (для reverse proxy)
- SSL сертификат (Let's Encrypt)

---

## Docker Compose

### production-compose.yml

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: dnd_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: dnd_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  redis:
    image: redis:7-alpine
    restart: always

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://dnd_user:${DB_PASSWORD}@postgres:5432/dnd_db
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - postgres
      - redis
    restart: always

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    restart: always

volumes:
  postgres_data:
```

---

## Nginx

### nginx.conf

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    location /socket.io {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    location /uploads {
        proxy_pass http://backend:8000;
    }
}
```

---

## Переменные окружения

### Backend (.env)

```env
# Database
DATABASE_URL=postgresql://dnd_user:PASSWORD@postgres:5432/dnd_db

# Redis
REDIS_URL=redis://redis:6379

# JWT
SECRET_KEY=<сложный-случайный-ключ>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Server
HOST=0.0.0.0
PORT=8000

# Uploads
UPLOAD_DIR=/app/uploads
MAPS_DIR=/app/uploads/maps
MAX_UPLOAD_SIZE=10485760

# Logging
LOG_LEVEL=WARNING
```

### Frontend (.env)

```env
VITE_API_URL=https://your-domain.com
VITE_WS_URL=https://your-domain.com
```

---

## Сборка

### Backend

```bash
cd backend
docker build -t dnd-backend .
```

### Frontend

```bash
cd frontend
npm run build
docker build -t dnd-frontend .
```

---

## Запуск

```bash
docker-compose -f production-compose.yml up -d
```

---

## SSL

### Let's Encrypt

```bash
certbot --nginx -d your-domain.com
```

---

## Мониторинг

### Логи

```bash
docker-compose logs -f
```

### Статус

```bash
docker-compose ps
```

---

## Резервное копирование

### База данных

```bash
docker exec dnd_postgres pg_dump -U dnd_user dnd_db > backup.sql
```

---

## Обновление

```bash
docker-compose pull
docker-compose up -d
```

---

## Смотрите также

- [Быстрый старт](../getting-started/quick-start.md) — запуск в dev режиме