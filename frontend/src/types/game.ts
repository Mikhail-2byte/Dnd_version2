export interface GameSession {
  id: string;
  name: string;
  invite_code: string;
  master_id: string;
  map_url: string | null;
  story: string | null;
  created_at: string;
}

export interface Token {
  id: string;
  game_id: string;
  name: string;
  x: number;
  y: number;
  image_url: string | null;
  is_hidden: boolean;
  token_type: 'npc' | 'item' | 'player';
  token_metadata: Record<string, unknown> | null;
}

export interface Player {
  user_id: string;
  username: string;
  role: 'master' | 'player';
  is_ready?: boolean;
  character_id?: string;
}

export interface Participant {
  user_id: string;
  username: string;
  role: string;
  is_ready: boolean;
  character_id?: string;
}

export interface LogEvent {
  id: string;
  type: 'attack' | 'damage' | 'heal' | 'death' | 'condition' | 'scene' | 'roll' | 'system';
  message: string;
  timestamp: string;
  isCritical?: boolean;
  actorName?: string;
  targetName?: string;
}

export interface ChatMessage {
  id: string;
  userId: string;
  userName: string;
  message: string;
  timestamp: string;
  isOOC: boolean;
}

