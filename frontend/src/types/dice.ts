/**
 * Типы для системы бросков кубиков
 */

export interface DieRoll {
  die_id: string;
  value: number;
}

export interface DiceRollResult {
  rolls: DieRoll[];
  total: number;
}

export interface DiceRollHistoryItem {
  id: string;
  user_id: string;
  username: string;
  count: number;
  faces: number;
  rolls: DieRoll[];
  total: number;
  roll_type?: string | null; // "attack", "save", "skill", "custom"
  modifier?: number | null;
  advantage_type?: string | null; // "advantage", "disadvantage", или null
  advantage_rolls?: DieRoll[] | null;
  selected_roll?: DieRoll | null;
  created_at: string;
}

export interface DiceRollHistoryFilters {
  user_id?: string;
  roll_type?: string;
  limit?: number;
  offset?: number;
}

export type RollType = "attack" | "save" | "skill" | "custom";

export interface DiceTemplate {
  label: string;
  count: number;
  faces: number;
  modifier_source?: string;
  roll_type: RollType;
}

