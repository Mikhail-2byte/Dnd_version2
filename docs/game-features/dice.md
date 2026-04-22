# Бросание кубиков

Система поддерживает dnd-нотацию кубиков с автоматическим подсчётом.

---

## Dnd-нотация

### Формат

```
XdY+Z
```

Где:
- `X` — количество кубиков
- `Y` — тип кубика (d4, d6, d8, d10, d12, d20, d100)
- `Z` — модификатор (может быть отрицательным)

### Примеры

| Нотация | Описание |
|---------|----------|
| `1d20` | Один d20 |
| `2d6` | Два d6 |
| `1d20+5` | d20 + 5 |
| `1d8+3` | d8 + 3 |
| `2d6+1d8+2` | 2d6 + 1d8 + 2 |
| `1d20-1` | d20 - 1 |

---

## Бросание кубика

### Через UI

1. Откройте панель кубиков справа
2. Выберите тип кубика или введите вручную
3. Нажмите "Бросить"

### Через Socket

```typescript
socket.emit("dice:roll", {
  game_id: 1,
  dice: "1d20+5",
  character_name: "Aragorn"
});
```

### Через HTTP

```bash
curl -X POST http://localhost:8000/api/dice/roll \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "dice": "1d20+5",
    "character_name": "Aragorn",
    "game_id": 1
  }'
```

---

## Результат

### Ответ сервера

```json
{
  "dice": "1d20+5",
  "result": [18],
  "total": 23,
  "character_name": "Aragorn",
  "username": "master"
}
```

`result` — массив с результатами каждого кубика.

---

## Преимущество и помеха

### Через UI

Кнопки "Advantage" и "Disadvantage":
- **Advantage** — бросить 2d20, выбрать больший
- **Disadvantage** — бросить 2d20, выбрать меньший

### Socket

```typescript
socket.emit("dice:roll", {
  game_id: 1,
  dice: "1d20+5",
  character_name: "Aragorn",
  advantage: true  // или disadvantage: true
});
```

---

## История бросков

### Получить историю

```bash
GET http://localhost:8000/api/dice/history/1 \
  -H "Authorization: Bearer <token>"
```

### Ответ

```json
[
  {
    "id": 1,
    "dice_string": "1d20+5",
    "result": [18],
    "total": 23,
    "character_name": "Aragorn",
    "username": "master",
    "created_at": "2024-01-01T12:00:00"
  },
  {
    "id": 2,
    "dice_string": "2d6",
    "result": [3, 5],
    "total": 8,
    "character_name": "Grog",
    "username": "player2",
    "created_at": "2024-01-01T12:05:00"
  }
]
```

---

## Визуализация

Результаты отображаются:
- В чате/логе бросков
- Всплывающим уведомлением
- Анимацией кубика (опционально)

---

## События

### Сервер → Клиент

```typescript
socket.on("dice:rolled", (data) => {
  // Показать результат всем игрокам
});
```

---

## Смотрите также

- [Токены](tokens.md) — токены на карте
- [Бой](combat.md) — боевая система