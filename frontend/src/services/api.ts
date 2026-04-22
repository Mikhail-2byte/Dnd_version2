import axios from 'axios';
import type { TokenResponse, User, UserStats } from '../types/user';
import type { GameSession, Token } from '../types/game';
import type { Scenario, ScenarioListItem, ScenarioNPC, ScenarioHiddenItem } from '../types/scenario';
import type {
  Character, CharacterCreate, CharacterUpdate, RaceData, BackgroundData,
  InventoryItem, WeaponData, ArmorData, ItemData,
  SpellbookData, SpellData,
  MonsterData, MonsterListItem,
} from '../types/character';
import type { DiceRollHistoryItem, DiceRollHistoryFilters } from '../types/dice';
import type { CombatSession, StartCombatRequest, RollInitiativeRequest, CombatParticipant } from '../types/combat';

export const API_URL: string = (import.meta.env.VITE_API_URL as string) ?? '';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor для добавления токена
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor для обработки ошибок
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Удаляем токен, но не делаем жесткую перезагрузку
      // Пусть React Router обработает навигацию
      localStorage.removeItem('token');
      // Триггерим событие для обновления состояния авторизации
      window.dispatchEvent(new CustomEvent('auth:logout'));
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: async (email: string, username: string, password: string): Promise<TokenResponse> => {
    const response = await api.post<TokenResponse>('/api/auth/register', {
      email,
      username,
      password,
    });
    return response.data;
  },

  login: async (email: string, password: string): Promise<TokenResponse> => {
    const response = await api.post<TokenResponse>('/api/auth/login', {
      email,
      password,
    });
    return response.data;
  },

  me: async (): Promise<User> => {
    const response = await api.get<User>('/api/auth/me');
    return response.data;
  },

  getStats: async (): Promise<UserStats> => {
    const response = await api.get<UserStats>('/api/auth/stats');
    return response.data;
  },
};

export const gamesAPI = {
  create: async (name: string, story?: string, mapUrl?: string): Promise<GameSession> => {
    const response = await api.post<GameSession>('/api/games', { 
      name,
      story,
      map_url: mapUrl,
    });
    return response.data;
  },

  getByInviteCode: async (inviteCode: string): Promise<GameSession> => {
    const response = await api.get<GameSession>(`/api/games/${inviteCode}`);
    return response.data;
  },

  join: async (gameId: string): Promise<GameSession> => {
    const response = await api.post<GameSession>(`/api/games/${gameId}/join`);
    return response.data;
  },

  spectate: async (gameId: string): Promise<GameSession> => {
    const response = await api.post<GameSession>(`/api/games/${gameId}/spectate`);
    return response.data;
  },

  getInfo: async (gameId: string): Promise<GameSession> => {
    const response = await api.get<GameSession>(`/api/games/${gameId}/info`);
    return response.data;
  },

  getTokens: async (gameId: string): Promise<Token[]> => {
    const response = await api.get<Token[]>(`/api/games/${gameId}/tokens`);
    return response.data;
  },

  setReady: async (gameId: string, isReady: boolean, characterId?: string | null): Promise<void> => {
    // Сначала устанавливаем персонажа, если он указан
    if (characterId !== undefined) {
      await api.patch(`/api/games/${gameId}/participants/me/character`, { 
        character_id: characterId || null 
      });
    }
    // Затем устанавливаем готовность
    await api.patch(`/api/games/${gameId}/participants/me/ready`, { is_ready: isReady });
  },

  getParticipants: async (gameId: string): Promise<import('../types/game').Participant[]> => {
    const response = await api.get<import('../types/game').Participant[]>(`/api/games/${gameId}/participants`);
    return response.data;
  },

  getDiceHistory: async (gameId: string, filters?: DiceRollHistoryFilters): Promise<DiceRollHistoryItem[]> => {
    const params = new URLSearchParams();
    if (filters?.user_id) params.append('user_id', filters.user_id);
    if (filters?.roll_type) params.append('roll_type', filters.roll_type);
    if (filters?.limit) params.append('limit', filters.limit.toString());
    if (filters?.offset) params.append('offset', filters.offset.toString());
    
    const queryString = params.toString();
    const url = `/api/games/${gameId}/dice-history${queryString ? `?${queryString}` : ''}`;
    const response = await api.get<DiceRollHistoryItem[]>(url);
    return response.data;
  },

  setCharacter: async (gameId: string, characterId: string | null): Promise<void> => {
    await api.patch(`/api/games/${gameId}/participants/me/character`, { 
      character_id: characterId 
    });
  },

  transferMasterRole: async (gameId: string, fromUserId: string, toUserId: string): Promise<{ game: GameSession; new_master_id: string; old_master_id: string }> => {
    const response = await api.patch<{ game: GameSession; new_master_id: string; old_master_id: string }>(
      `/api/games/${gameId}/participants/${fromUserId}/transfer-master`,
      { to_user_id: toUserId }
    );
    return response.data;
  },

  getStatus: async (gameId: string): Promise<{ started: boolean }> => {
    const response = await api.get<{ started: boolean }>(`/api/games/${gameId}/status`);
    return response.data;
  },

  revealToken: async (gameId: string, tokenId: string): Promise<Token> => {
    const response = await api.post<Token>(`/api/games/${gameId}/tokens/${tokenId}/reveal`);
    return response.data;
  },

  giveItem: async (gameId: string, data: {
    character_id: string;
    item_type: string;
    item_id: string;
    quantity?: number;
  }): Promise<{ message: string; inventory_id: string }> => {
    const response = await api.post(`/api/games/${gameId}/give-item`, data);
    return response.data;
  },
};

export const charactersAPI = {
  create: async (characterData: CharacterCreate): Promise<Character> => {
    const response = await api.post<Character>('/api/characters', characterData);
    return response.data;
  },

  getAll: async (): Promise<Character[]> => {
    const response = await api.get<{ characters: Character[] }>('/api/characters');
    return response.data.characters;
  },

  getById: async (characterId: string): Promise<Character> => {
    const response = await api.get<Character>(`/api/characters/${characterId}`);
    return response.data;
  },

  update: async (characterId: string, characterData: CharacterUpdate): Promise<Character> => {
    const response = await api.put<Character>(`/api/characters/${characterId}`, characterData);
    return response.data;
  },

  delete: async (characterId: string): Promise<void> => {
    await api.delete(`/api/characters/${characterId}`);
  },

  getTemplates: async (): Promise<Record<string, any>> => {
    const response = await api.get<{ templates: Record<string, any> }>('/api/characters/templates');
    return response.data.templates;
  },

  getTemplate: async (className: string): Promise<any> => {
    const response = await api.get<{ template: any }>(`/api/characters/templates/${className}`);
    return response.data.template;
  },

  generateAbilities: async (method: string, className?: string): Promise<{
    strength: number; dexterity: number; constitution: number;
    intelligence: number; wisdom: number; charisma: number; method: string;
  }> => {
    const response = await api.post<{
      strength: number; dexterity: number; constitution: number;
      intelligence: number; wisdom: number; charisma: number; method: string;
    }>('/api/characters/generate-abilities', { method, class_name: className || null });
    return response.data;
  },

  grantXP: async (characterId: string, xp: number): Promise<{
    xp_gained: number; total_xp: number; level_up_available: boolean;
    earned_level: number; next_level_xp: number | null;
  }> => {
    const response = await api.post(`/api/characters/${characterId}/grant-xp`, { xp });
    return response.data;
  },

  levelUp: async (characterId: string, takeAverage = true): Promise<Character> => {
    const response = await api.post<Character>(`/api/characters/${characterId}/level-up`, { take_average: takeAverage });
    return response.data;
  },

  rest: async (characterId: string, type: 'short' | 'long', hitDiceSpent = 1): Promise<Character> => {
    const response = await api.post<Character>(`/api/characters/${characterId}/rest`, {
      type,
      hit_dice_spent: hitDiceSpent,
    });
    return response.data;
  },

  uploadAvatar: async (file: File): Promise<string> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post<{ avatar_url: string }>('/api/characters/upload-avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data.avatar_url;
  },
};

export const diceAPI = {
  getTemplates: async (): Promise<Record<string, any>> => {
    const response = await api.get<{ templates: Record<string, any> }>('/api/dice/templates');
    return response.data.templates;
  },

  applyTemplate: async (templateName: string, characterId?: string): Promise<{
    count: number;
    faces: number;
    roll_type: string;
    modifier?: number | null;
  }> => {
    const response = await api.post<{
      count: number;
      faces: number;
      roll_type: string;
      modifier?: number | null;
    }>('/api/dice/templates/apply', {
      template_name: templateName,
      character_id: characterId || null,
    });
    return response.data;
  },
};

export const combatAPI = {
  start: async (gameId: string, request: StartCombatRequest): Promise<CombatSession> => {
    const response = await api.post<CombatSession>(`/api/games/${gameId}/combat/start`, request);
    return response.data;
  },

  getCurrent: async (gameId: string): Promise<CombatSession | null> => {
    const response = await api.get<CombatSession | null>(`/api/games/${gameId}/combat/current`);
    return response.data;
  },

  rollInitiative: async (gameId: string, combatId: string, request: RollInitiativeRequest): Promise<CombatParticipant> => {
    const response = await api.post<CombatParticipant>(`/api/games/${gameId}/combat/${combatId}/roll-initiative`, request);
    return response.data;
  },

  end: async (gameId: string, combatId: string): Promise<CombatSession> => {
    const response = await api.post<CombatSession>(`/api/games/${gameId}/combat/${combatId}/end`);
    return response.data;
  },

  attack: async (
    gameId: string, combatId: string, attackerId: string, targetId: string,
    opts: { attackRoll?: number; modifier?: number; advantage?: string; damageDice?: string; damageModifier?: number; damageType?: string } = {}
  ): Promise<{
    hit: boolean; attack_roll: number; rolls: number[]; modifier: number;
    total_attack: number; target_ac: number; critical: boolean; auto_miss: boolean;
    advantage: string | null; damage: number | null; damage_dice: string;
  }> => {
    const response = await api.post(`/api/games/${gameId}/combat/${combatId}/attack`, {
      attacker_id: attackerId,
      target_id: targetId,
      attack_roll: opts.attackRoll ?? null,
      modifier: opts.modifier ?? 0,
      advantage: opts.advantage ?? null,
      damage_dice: opts.damageDice ?? '1d6',
      damage_modifier: opts.damageModifier ?? 0,
      damage_type: opts.damageType ?? null,
    });
    return response.data;
  },

  damage: async (gameId: string, combatId: string, targetId: string, damage: number): Promise<CombatParticipant> => {
    const response = await api.post<CombatParticipant>(`/api/games/${gameId}/combat/${combatId}/damage`, { target_id: targetId, damage });
    return response.data;
  },

  heal: async (gameId: string, combatId: string, targetId: string, healing: number): Promise<CombatParticipant> => {
    const response = await api.post<CombatParticipant>(`/api/games/${gameId}/combat/${combatId}/heal`, { target_id: targetId, healing });
    return response.data;
  },

  nextTurn: async (gameId: string, combatId: string): Promise<CombatSession> => {
    const response = await api.post<CombatSession>(`/api/games/${gameId}/combat/${combatId}/next-turn`);
    return response.data;
  },

  manageCondition: async (
    gameId: string, combatId: string, participantId: string,
    action: 'add' | 'remove', condition: string
  ): Promise<CombatParticipant> => {
    const response = await api.post<CombatParticipant>(
      `/api/games/${gameId}/combat/${combatId}/participants/${participantId}/condition`,
      { action, condition }
    );
    return response.data;
  },

  deathSave: async (gameId: string, combatId: string, participantId: string): Promise<{
    roll: number; success: boolean; failure: boolean; stabilized: boolean;
    died: boolean; death_saves_success: number; death_saves_failure: number; regained_hp?: number;
  }> => {
    const response = await api.post(`/api/games/${gameId}/combat/${combatId}/participants/${participantId}/death-save`);
    return response.data;
  },

  savingThrow: async (
    gameId: string, combatId: string,
    participantId: string, ability: string, dc: number
  ): Promise<{
    participant_id: string; ability: string; dc: number;
    roll: number; modifier: number; total: number; success: boolean;
  }> => {
    const response = await api.post(`/api/games/${gameId}/combat/${combatId}/saving-throw`, {
      participant_id: participantId,
      ability,
      dc,
    });
    return response.data;
  },

  addMonster: async (
    gameId: string, combatId: string, monsterSlug: string,
    opts?: { x?: number; y?: number; use_average_hp?: boolean; custom_name?: string }
  ) => {
    const params = {
      monster_slug: monsterSlug,
      x: opts?.x ?? 50,
      y: opts?.y ?? 50,
      use_average_hp: opts?.use_average_hp ?? true,
      custom_name: opts?.custom_name,
    };
    const response = await api.post(`/api/games/${gameId}/combat/${combatId}/add-monster`, null, { params });
    return response.data;
  },
};

export const gameDataAPI = {
  getRaces: async (): Promise<RaceData[]> => {
    const response = await api.get<RaceData[]>('/api/data/races');
    return response.data;
  },

  getBackgrounds: async (): Promise<BackgroundData[]> => {
    const response = await api.get<BackgroundData[]>('/api/data/backgrounds');
    return response.data;
  },

  getWeapons: async (category?: string): Promise<WeaponData[]> => {
    const params = category ? { category } : {};
    const response = await api.get<WeaponData[]>('/api/data/weapons', { params });
    return response.data;
  },

  getArmors: async (category?: string): Promise<ArmorData[]> => {
    const params = category ? { category } : {};
    const response = await api.get<ArmorData[]>('/api/data/armors', { params });
    return response.data;
  },

  getItems: async (category?: string): Promise<ItemData[]> => {
    const params = category ? { category } : {};
    const response = await api.get<ItemData[]>('/api/data/items', { params });
    return response.data;
  },

  getSpells: async (filters?: { level?: number; school?: string; class?: string }): Promise<SpellData[]> => {
    const response = await api.get<SpellData[]>('/api/data/spells', { params: filters });
    return response.data;
  },

  getMonsters: async (filters?: { name?: string; type?: string; cr_min?: number; cr_max?: number }): Promise<MonsterListItem[]> => {
    const response = await api.get<MonsterListItem[]>('/api/data/monsters', { params: filters });
    return response.data;
  },

  getMonster: async (slug: string): Promise<MonsterData> => {
    const response = await api.get<MonsterData>(`/api/data/monsters/${slug}`);
    return response.data;
  },
};

export const inventoryAPI = {
  getInventory: async (characterId: string): Promise<{ items: InventoryItem[] }> => {
    const response = await api.get(`/api/characters/${characterId}/inventory`);
    return response.data;
  },

  addItem: async (characterId: string, item_type: string, item_id: string, quantity = 1): Promise<InventoryItem> => {
    const response = await api.post<InventoryItem>(`/api/characters/${characterId}/inventory`, {
      item_type, item_id, quantity,
    });
    return response.data;
  },

  removeItem: async (characterId: string, invId: string): Promise<void> => {
    await api.delete(`/api/characters/${characterId}/inventory/${invId}`);
  },

  equipItem: async (characterId: string, invId: string, is_equipped: boolean, slot?: string): Promise<InventoryItem> => {
    const response = await api.put<InventoryItem>(`/api/characters/${characterId}/inventory/${invId}/equip`, {
      is_equipped, slot,
    });
    return response.data;
  },
};

export const spellbookAPI = {
  getSpellbook: async (characterId: string): Promise<SpellbookData> => {
    const response = await api.get<SpellbookData>(`/api/characters/${characterId}/spellbook`);
    return response.data;
  },

  addSpell: async (characterId: string, spell_id: string): Promise<{ message: string; id: string }> => {
    const response = await api.post(`/api/characters/${characterId}/spells`, { spell_id });
    return response.data;
  },

  removeSpell: async (characterId: string, spellId: string): Promise<void> => {
    await api.delete(`/api/characters/${characterId}/spells/${spellId}`);
  },

  prepareSpell: async (characterId: string, spellId: string, is_prepared: boolean): Promise<{ is_prepared: boolean }> => {
    const response = await api.put(`/api/characters/${characterId}/spells/${spellId}/prepare`, { is_prepared });
    return response.data;
  },

  useSlot: async (characterId: string, spell_level: number): Promise<{ spell_level: number; used: number; max: number }> => {
    const response = await api.post(`/api/characters/${characterId}/spell-slots/use`, { spell_level });
    return response.data;
  },

  initializeSlots: async (characterId: string): Promise<{ slots_initialized: number }> => {
    const response = await api.post(`/api/characters/${characterId}/spell-slots/initialize`);
    return response.data;
  },
};

export const scenariosAPI = {
  list: async (): Promise<ScenarioListItem[]> => {
    const response = await api.get<ScenarioListItem[]>('/api/scenarios');
    return response.data;
  },

  create: async (data: { name: string; story?: string; map_url?: string }): Promise<Scenario> => {
    const response = await api.post<Scenario>('/api/scenarios', data);
    return response.data;
  },

  get: async (id: string): Promise<Scenario> => {
    const response = await api.get<Scenario>(`/api/scenarios/${id}`);
    return response.data;
  },

  update: async (id: string, data: { name?: string; story?: string; map_url?: string }): Promise<Scenario> => {
    const response = await api.put<Scenario>(`/api/scenarios/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/api/scenarios/${id}`);
  },

  uploadMap: async (scenarioId: string, file: File): Promise<{ map_url: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post<{ map_url: string }>(
      `/api/scenarios/${scenarioId}/upload-map`,
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
    return response.data;
  },

  launch: async (id: string): Promise<GameSession> => {
    const response = await api.post<GameSession>(`/api/scenarios/${id}/launch`);
    return response.data;
  },

  addNpc: async (scenarioId: string, data: Omit<ScenarioNPC, 'id' | 'scenario_id'>): Promise<ScenarioNPC> => {
    const response = await api.post<ScenarioNPC>(`/api/scenarios/${scenarioId}/npcs`, data);
    return response.data;
  },

  updateNpc: async (scenarioId: string, npcId: string, data: Partial<Omit<ScenarioNPC, 'id' | 'scenario_id'>>): Promise<ScenarioNPC> => {
    const response = await api.put<ScenarioNPC>(`/api/scenarios/${scenarioId}/npcs/${npcId}`, data);
    return response.data;
  },

  deleteNpc: async (scenarioId: string, npcId: string): Promise<void> => {
    await api.delete(`/api/scenarios/${scenarioId}/npcs/${npcId}`);
  },

  addItem: async (scenarioId: string, data: Omit<ScenarioHiddenItem, 'id' | 'scenario_id'>): Promise<ScenarioHiddenItem> => {
    const response = await api.post<ScenarioHiddenItem>(`/api/scenarios/${scenarioId}/items`, data);
    return response.data;
  },

  updateItem: async (scenarioId: string, itemId: string, data: Partial<Omit<ScenarioHiddenItem, 'id' | 'scenario_id'>>): Promise<ScenarioHiddenItem> => {
    const response = await api.put<ScenarioHiddenItem>(`/api/scenarios/${scenarioId}/items/${itemId}`, data);
    return response.data;
  },

  deleteItem: async (scenarioId: string, itemId: string): Promise<void> => {
    await api.delete(`/api/scenarios/${scenarioId}/items/${itemId}`);
  },
};

