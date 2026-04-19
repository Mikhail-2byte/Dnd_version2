/**
 * Утилиты для назначения цветов игрокам
 */

export type PlayerColor = {
  border: string;
  bg: string;
  text: string;
  ring: string;
};

// Палитра цветов для игроков
const PLAYER_COLORS: PlayerColor[] = [
  {
    border: 'border-blue-500',
    bg: 'bg-blue-500/20',
    text: 'text-blue-700 dark:text-blue-400',
    ring: 'ring-blue-500/30',
  },
  {
    border: 'border-green-500',
    bg: 'bg-green-500/20',
    text: 'text-green-700 dark:text-green-400',
    ring: 'ring-green-500/30',
  },
  {
    border: 'border-purple-500',
    bg: 'bg-purple-500/20',
    text: 'text-purple-700 dark:text-purple-400',
    ring: 'ring-purple-500/30',
  },
  {
    border: 'border-orange-500',
    bg: 'bg-orange-500/20',
    text: 'text-orange-700 dark:text-orange-400',
    ring: 'ring-orange-500/30',
  },
  {
    border: 'border-pink-500',
    bg: 'bg-pink-500/20',
    text: 'text-pink-700 dark:text-pink-400',
    ring: 'ring-pink-500/30',
  },
  {
    border: 'border-cyan-500',
    bg: 'bg-cyan-500/20',
    text: 'text-cyan-700 dark:text-cyan-400',
    ring: 'ring-cyan-500/30',
  },
  {
    border: 'border-yellow-500',
    bg: 'bg-yellow-500/20',
    text: 'text-yellow-700 dark:text-yellow-400',
    ring: 'ring-yellow-500/30',
  },
  {
    border: 'border-red-500',
    bg: 'bg-red-500/20',
    text: 'text-red-700 dark:text-red-400',
    ring: 'ring-red-500/30',
  },
];

/**
 * Получить цвет для игрока по его индексу
 */
export function getPlayerColor(playerIndex: number): PlayerColor {
  return PLAYER_COLORS[playerIndex % PLAYER_COLORS.length];
}

/**
 * Создать мапу цветов для участников игры
 */
export function createPlayerColorMap(participants: Array<{ user_id: string; role: string }>): Map<string, PlayerColor> {
  const colorMap = new Map<string, PlayerColor>();
  
  // Мастер всегда получает первый цвет (или можно сделать его нейтральным)
  // Игроки получают цвета по порядку
  let playerIndex = 0;
  
  participants.forEach((participant) => {
    if (participant.role === 'player') {
      colorMap.set(participant.user_id, getPlayerColor(playerIndex));
      playerIndex++;
    }
  });
  
  return colorMap;
}

/**
 * Получить информацию о том, кто выбрал персонажа
 * Для шаблонных персонажей проверяем только локально (не по character_id)
 */
export function getCharacterOwner(
  characterId: string,
  participants: Array<{ user_id: string; character_id?: string; username: string }>
): { user_id: string; username: string } | null {
  // Шаблонные персонажи не сохраняются в БД, поэтому не ищем их по character_id
  // Проверяем, является ли это шаблонным ID (начинается с "template-" или не валидный UUID)
  if (characterId.startsWith('template-')) {
    return null;
  }
  
  const owner = participants.find(p => p.character_id === characterId);
  return owner ? { user_id: owner.user_id, username: owner.username } : null;
}
