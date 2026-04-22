# Боевая система

Система боя включает инициативу, раунды, ходы и отслеживание HP.

---

## Начало боя

### Через UI

1. Нажмите "Начать бой" в панели боя
2. Выберите участников (токены на карте)
3. Нажмите "Старт"

### Через Socket

```typescript
socket.emit("combat:start", {
  game_id: 1,
  participant_ids: [1, 2, 3]
});
```

### Через HTTP

```bash
curl -X POST http://localhost:8000/api/combat/1/start \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"participant_ids": [1, 2, 3]}'
```

---

## Инициатива

При начале боя каждый участник бросает инициативу (1d20 + DEX модификатор).

### Автоматический подсчёт

```json
{
  "combat_id": 1,
  "round": 1,
  "participants": [
    {"token_id": 1, "name": "Aragorn", "initiative": 18, "hp": 42},
    {"token_id": 2, "name": "Goblin 1", "initiative": 14, "hp": 7},
    {"token_id": 3, "name": "Legolas", "initiative": 20, "hp": 35}
  ]
}
```

Участники сортируются по инициативе (от большей к меньшей).

---

## Раунды и ходы

### Структура

```
Раунд 1
├── Ход: Legolas (инициатива 20)
├── Ход: Aragorn (инициатива 18)
└── Ход: Goblin 1 (инициатива 14)

Раунд 2
├── Ход: Legolas
├── Ход: Aragorn
└── Ход: Goblin 1
```

### Следующий ход

```typescript
socket.emit("combat:next", {
  combat_id: 1
});
```

```json
{
  "current_turn_token_id": 2,
  "round": 1
}
```

---

## HP и урон

### Обновление HP

```typescript
socket.emit("token:update_hp", {
  game_id: 1,
  token_id: 2,
  hp: 7,     // текущее HP
  max_hp: 15 // максимальное HP
});
```

### Автоматические статусы

| HP | Статус |
|----|--------|
| > 0 | Active |
| 0 | Unconscious |
| < 0 | Dead |

---

## Завершение боя

### Через UI

Нажмите "Завершить бой" в панели боя.

### Через Socket

```typescript
socket.emit("combat:end", {
  combat_id: 1
});
```

Все участники возвращаются в нормальное состояние.

---

## События

### Сервер → Клиент

```typescript
// Бой начат
socket.on("combat:started", (data) => {
  // data: { combat_id, round, participants }
});

// Следующий ход
socket.on("combat:next_turn", (data) => {
  // data: { token_id, initiative }
});

// Бой завершён
socket.on("combat:ended", (data) => {
  // data: { combat_id }
});
```

---

## Ограничения

- Начать бой может только **мастер**
- Переключать ходы может **мастер** или текущий игрок
- Обновлять HP может **мастер**

---

## Панель боя

В игровой комнате справа отображается панель боя:

- Текущий раунд
- Текущий ход (подсвечен)
- Список участников с HP
- Кнопки управления (следующий ход, завершить)

---

## Смотрите также

- [Токены](tokens.md) — токены на карте
- [Кубики](dice.md) — бросание кубиков для инициативы