export interface CombatParticipant {
  id: string;
  combat_id: string;
  character_id?: string | null;
  token_id?: string | null;
  name?: string | null;
  initiative?: number | null;
  current_hp: number;
  max_hp: number;
  armor_class: number;
  conditions?: string[] | null;
  is_player_controlled: boolean;
  // Action economy
  actions_used?: number;
  bonus_actions_used?: number;
  reaction_used?: boolean;
  // Death saves
  death_saves_success?: number;
  death_saves_failure?: number;
  is_dead?: boolean;
  character_name?: string | null;
  token_name?: string | null;
}

export interface CombatSession {
  id: string;
  game_id: string;
  is_active: boolean;
  current_turn_index: number;
  round_number: number;
  started_at: string;
  ended_at?: string | null;
  participants: CombatParticipant[];
}

// D&D 5e conditions with display names and icons
export const CONDITIONS: Record<string, { label: string; color: string; icon: string }> = {
  blinded:       { label: 'Ослеплён',      color: 'bg-gray-500',   icon: '👁️' },
  charmed:       { label: 'Очарован',      color: 'bg-pink-500',   icon: '💕' },
  deafened:      { label: 'Оглушён',       color: 'bg-yellow-600', icon: '🔇' },
  exhaustion:    { label: 'Истощён',       color: 'bg-orange-500', icon: '😴' },
  frightened:    { label: 'Испуган',       color: 'bg-purple-600', icon: '😱' },
  grappled:      { label: 'Схвачен',       color: 'bg-amber-600',  icon: '🤝' },
  incapacitated: { label: 'Недееспособен', color: 'bg-red-600',    icon: '🚫' },
  invisible:     { label: 'Невидим',       color: 'bg-cyan-500',   icon: '👻' },
  paralyzed:     { label: 'Парализован',   color: 'bg-blue-600',   icon: '⚡' },
  petrified:     { label: 'Окаменел',      color: 'bg-stone-600',  icon: '🪨' },
  poisoned:      { label: 'Отравлен',      color: 'bg-green-600',  icon: '☠️' },
  prone:         { label: 'Лежит',         color: 'bg-yellow-500', icon: '⬇️' },
  restrained:    { label: 'Обездвижен',    color: 'bg-indigo-600', icon: '⛓️' },
  stunned:       { label: 'Ошеломлён',     color: 'bg-violet-600', icon: '💫' },
  unconscious:   { label: 'Без сознания',  color: 'bg-slate-600',  icon: '💤' },
  dead:          { label: 'Мёртв',         color: 'bg-black',      icon: '💀' },
};

export interface StartCombatRequest {
  participant_ids: string[];
}

export interface RollInitiativeRequest {
  participant_id: string;
  initiative_roll?: number | null;
}
