# WebSocket события

## Подключение

URL: `http://localhost:8000`

```typescript
const socket = io("http://localhost:8000", {
  auth: { token: "jwt_token" },
  query: { game_id: "ABC123" }
});
```

---

## Клиент → Сервер

### Подключение к игре

```typescript
socket.emit("game:join", {
  game_id: "ABC123",
  token: "jwt_token"
});
```

### Перемещение токена

```typescript
socket.emit("token:move", {
  game_id: 1,
  token_id: 5,
  x: 100,
  y: 200
});
```

Ограничение: игроки могут двигать только свои токены, мастер — любые.

### Создание токена

```typescript
socket.emit("token:create", {
  game_id: 1,
  character_id: 3,
  name: "Goblin",
  x: 50,
  y: 50,
  size: 1
});
```

Ограничение: только мастер.

### Удаление токена

```typescript
socket.emit("token:delete", {
  game_id: 1,
  token_id: 5
});
```

Ограничение: только мастер.

### Бросание кубика

```typescript
socket.emit("dice:roll", {
  game_id: 1,
  dice: "1d20+5",
  character_name: "Aragorn"
});
```

### Обновление HP

```typescript
socket.emit("token:update_hp", {
  game_id: 1,
  token_id: 5,
  hp: 15,
  max_hp: 20
});
```

### Начало боя

```typescript
socket.emit("combat:start", {
  game_id: 1,
  participant_ids: [1, 2, 3]
});
```

### Следующий ход

```typescript
socket.emit("combat:next", {
  combat_id: 1
});
```

---

## Сервер → Клиент

### Подключение к игре (ответ)

```typescript
socket.on("game:joined", (data) => {
  // data: { game, tokens, players, role }
});
```

### Ошибка

```typescript
socket.on("error", (data) => {
  // data: { message: "error description" }
});
```

### Токен перемещён

```typescript
socket.on("token:moved", (data) => {
  // data: { token_id: 5, x: 100, y: 200, moved_by: "master" }
});
```

### Токен создан

```typescript
socket.on("token:created", (data) => {
  // data: { token: {...} }
});
```

### Токен удалён

```typescript
socket.on("token:deleted", (data) => {
  // data: { token_id: 5 }
});
```

### Токен обновлён

```typescript
socket.on("token:updated", (data) => {
  // data: { token_id: 5, hp: 15, ... }
});
```

### Игрок присоединился

```typescript
socket.on("player:joined", (data) => {
  // data: { user_id: 2, username: "player2", role: "player" }
});
```

### Игрок отключился

```typescript
socket.on("player:left", (data) => {
  // data: { user_id: 2 }
});
```

### Результат броска кубика

```typescript
socket.on("dice:rolled", (data) => {
  // data: { dice: "1d20+5", result: [18], total: 23, character_name: "Aragorn", username: "master" }
});
```

### Бой начат

```typescript
socket.on("combat:started", (data) => {
  // data: { combat_id: 1, round: 1, participants: [...] }
});
```

### Следующий ход

```typescript
socket.on("combat:next_turn", (data) => {
  // data: { token_id: 2, initiative: 15 }
});
```

### Бой завершён

```typescript
socket.on("combat:ended", (data) => {
  // data: { combat_id: 1 }
});
```

---

## Полное состояние игры

При подключении или по запросу:

```typescript
socket.emit("game:state", { game_id: 1 });

socket.on("game:state", (data) => {
  // data: {
  //   game: {...},
  //   tokens: [...],
  //   players: [...],
  //   combat: {...} | null
  // }
});
```

---

## Обработка ошибок

```typescript
socket.on("error", (data) => {
  console.error(data.message);
  // Показать уведомление пользователю
});
```

Типичные ошибки:
- `"Not authorized"` — недостаточно прав
- `"Game not found"` — игра не существует
- `"Token not found"` — токен не найден
- `"Combat not active"` — бой не активен