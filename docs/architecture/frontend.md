# Frontend

## Технологии

- **React 19** — UI-фреймворк
- **TypeScript** — типизация
- **Vite** — сборка (порт 5173)
- **Tailwind CSS** — стили
- **Zustand** — управление состоянием
- **React Router v6** — роутинг
- **socket.io-client** — WebSocket

---

## Структура

```
frontend/src/
├── pages/              # Страницы
│   ├── Auth.tsx        # Регистрация/вход
│   ├── MainMenu.tsx    # Главное меню
│   ├── GameLobby.tsx   # Лобби игры
│   ├── GameRoom.tsx   # Основная игровая комната
│   ├── CreateGameNew.tsx  # Создание игры
│   └── ...
│
├── components/         # UI компоненты
│   ├── GameMap.tsx    # Карта с токенами
│   ├── TokenWrapper.tsx  # Токен на карте
│   ├── DiceRoller.tsx    # Бросание кубиков
│   ├── CombatPanel.tsx   # Панель боя
│   ├── PlayerList.tsx    # Список игроков
│   └── ui/           # Базовые UI компоненты
│
├── store/            # Zustand стейт
│   ├── authStore.ts  # Авторизация
│   └── gameStore.ts # Игровое состояние
│
├── services/         # API и Socket
│   ├── api.ts        # HTTP запросы
│   └── socket.ts     # Socket.IO клиент
│
├── hooks/           # React хуки
│   ├── useTokenHandlers.ts   # Операции с токенами
│   ├── useMapDragDrop.ts    # Drag & drop
│   └── use-toast.ts          # Уведомления
│
└── types/           # TypeScript типы
    ├── game.ts
    ├── character.ts
    └── dice.ts
```

---

## Роутинг

Все роуты определены в `App.tsx`:

```tsx
<Routes>
  <Route path="/" element={<Auth />} />
  <Route path="/menu" element={<MainMenu />} />
  <Route path="/game/:gameId" element={<GameRoom />} />
  {/* ... */}
</Routes>
```

---

## Управление состоянием

### Auth Store

`store/authStore.ts` — Zustand:

```typescript
interface AuthState {
  token: string | null
  user: User | null
  login: (email, password) => Promise<void>
  logout: () => void
}
```

Хранит JWT токен и данные текущего пользователя.

### Game Store

`store/gameStore.ts` — Zustand:

```typescript
interface GameState {
  game: Game | null
  tokens: Token[]
  players: Player[]
  userRole: 'master' | 'player'
  currentPlayer: string | null  // Для боя
  
  // Actions
  setGame: (game) => void
  addToken: (token) => void
  moveToken: (id, x, y) => void
  // ...
}
```

Хранит всё состояние игры: токены, игроки, роль.

---

## Socket.IO

### Socket Service

`services/socket.ts` — singleton:

```typescript
class SocketService {
  private sio: SocketIOClient
  
  connect(gameId: string, token: string): void
  disconnect(): void
  emit(event: string, data: any): void
  on(event: string, handler: Function): void
}
```

Подключается при входе в GameRoom.

### Обработка событий

Все события обрабатываются в `pages/GameRoom.tsx`:

```tsx
useEffect(() => {
  socket.on("token:moved", (data) => {
    gameStore.moveToken(data.token_id, data.x, data.y)
  })
  
  socket.on("player:joined", (data) => {
    gameStore.addPlayer(data)
  })
}, [])
```

---

## Компоненты карты

### GameMap

`components/GameMap.tsx` — главный компонент карты:

- Использует `react-zoom-pan-pinch` для зума и пана
- Рендерит токены поверх изображения карты

### TokenWrapper

`components/TokenWrapper.tsx` — токен:

- Кружок с именем/инициалами
- Popover меню (удалить, пометить убитым)
- Drag & drop для перемещения

### Hooks

| Hook | Описание |
|------|----------|
| `useTokenHandlers.ts` | Операции с токенами (создать, переместить, удалить) |
| `useMapDragDrop.ts` | Drag & drop персонажей на карту |

---

## Следующие шаги

- [Базы данных](database.md) — модели и схема

---

## Ссылки

- [WebSocket события](../api/websocket.md)
- [Токены](../game-features/tokens.md)
- [Карты](../game-features/maps.md)