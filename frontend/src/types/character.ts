export interface Character {
  id: string;
  user_id: string;
  name: string;
  race: string;
  class: string;
  level: number;
  strength: number;
  dexterity: number;
  constitution: number;
  intelligence: number;
  wisdom: number;
  charisma: number;
  max_hp?: number | null;
  current_hp?: number | null;
  armor_class?: number | null;
  skill_proficiencies?: string[] | null;
  saving_throw_proficiencies?: string[] | null;
  experience_points?: number | null;
  proficiency_bonus?: number | null;
  character_history?: string | null;
  equipment_and_features?: string | null;
  avatar_url?: string | null;
  created_at: string;
  updated_at?: string;
}

export interface CharacterCreate {
  name: string;
  race: string;
  class: string;
  level?: number;
  strength?: number;
  dexterity?: number;
  constitution?: number;
  intelligence?: number;
  wisdom?: number;
  charisma?: number;
  race_slug?: string;
  background_slug?: string;
  character_history?: string;
  equipment_and_features?: string;
  avatar_url?: string;
}

export interface CharacterUpdate {
  name?: string;
  race?: string;
  class?: string;
  level?: number;
  strength?: number;
  dexterity?: number;
  constitution?: number;
  intelligence?: number;
  wisdom?: number;
  charisma?: number;
  current_hp?: number;
  max_hp?: number;
  armor_class?: number;
  skill_proficiencies?: string[];
  saving_throw_proficiencies?: string[];
  experience_points?: number;
  character_history?: string;
  equipment_and_features?: string;
  avatar_url?: string;
}

export interface CharacterBackground {
  name: string;
  description: string;
  skill_bonuses: string[];
  features: string;
}

export interface CharacterTemplate {
  class: string;
  description: string;
  default_stats: {
    strength: number;
    dexterity: number;
    constitution: number;
    intelligence: number;
    wisdom: number;
    charisma: number;
  };
  starting_equipment: string[];
  suggested_names: string[];
  suggested_background: string;
  backgrounds?: CharacterBackground[];
  icon: string;
}

// Game data types (from /api/data/*)
export interface RaceData {
  id: string;
  slug: string;
  name: string;
  name_en?: string;
  speed: number;
  size: string;
  darkvision: number;
  ability_bonuses?: Record<string, number>;
  traits?: Array<{ name: string; description: string }>;
  languages?: string[];
  description?: string;
  subraces?: SubRaceData[];
}

export interface SubRaceData {
  id: string;
  slug: string;
  name: string;
  ability_bonuses?: Record<string, number>;
  traits?: Array<{ name: string; description: string }>;
  darkvision?: number;
}

export interface BackgroundData {
  id: string;
  slug: string;
  name: string;
  name_en?: string;
  skill_proficiencies?: string[];
  tool_proficiencies?: string[];
  equipment?: string[];
  feature_name?: string;
  feature_description?: string;
  description?: string;
}

// ── Inventory ──────────────────────────────────────────────────────────────

export interface InventoryItem {
  id: string;
  character_id: string;
  item_type: 'weapon' | 'armor' | 'item';
  item_id: string;
  quantity: number;
  is_equipped: boolean;
  slot?: string | null;
  item_data?: {
    name: string;
    category?: string;
    damage_dice?: string;
    damage_type?: string;
    properties?: string[];
    ability?: string;
    base_ac?: number;
    dex_modifier?: string;
    min_strength?: number;
    stealth_disadvantage?: boolean;
    weight?: number;
    cost_gp?: number;
  } | null;
}

export interface WeaponData {
  id: string;
  slug: string;
  name: string;
  category: string;
  damage_dice?: string;
  damage_type?: string;
  properties?: string[];
  ability?: string;
  weight?: number;
  cost_gp?: number;
}

export interface ArmorData {
  id: string;
  slug: string;
  name: string;
  category: string;
  base_ac: number;
  dex_modifier?: string;
  min_strength?: number;
  stealth_disadvantage?: boolean;
  weight?: number;
  cost_gp?: number;
}

// ── Spellbook ─────────────────────────────────────────────────────────────

export interface SpellbookEntry {
  id: string;
  spell_id: string;
  is_prepared: boolean;
  is_ritual: boolean;
  learned_at_level?: number;
  name?: string;
  level?: number;
  school?: string;
  concentration?: boolean;
  ritual?: boolean;
  casting_time?: string;
  spell_range?: string;
  components?: Record<string, boolean | string>;
  duration?: string;
  description?: string;
}

export interface SpellSlotInfo {
  spell_level: number;
  max_slots: number;
  used_slots: number;
  available: number;
}

export interface SpellbookData {
  spells: SpellbookEntry[];
  slots: SpellSlotInfo[];
}

export interface SpellData {
  id: string;
  slug: string;
  name: string;
  level: number;
  school?: string;
  casting_time?: string;
  spell_range?: string;
  components?: Record<string, boolean | string>;
  duration?: string;
  concentration: boolean;
  ritual: boolean;
  description?: string;
  higher_levels?: string;
  classes?: string[];
}

// ── Monsters ──────────────────────────────────────────────────────────────

export interface MonsterAction {
  id: string;
  name: string;
  action_type: string;
  description?: string;
  attack_bonus?: number;
  damage_dice?: string;
  damage_type?: string;
  reach_ft?: number;
  targets?: string;
}

export interface MonsterData {
  id: string;
  slug: string;
  name: string;
  name_en?: string;
  monster_type?: string;
  size?: string;
  alignment?: string;
  cr?: number;
  xp_reward?: number;
  strength: number;
  dexterity: number;
  constitution: number;
  intelligence: number;
  wisdom: number;
  charisma: number;
  hp_dice?: string;
  hp_average?: number;
  armor_class: number;
  armor_type?: string;
  speed?: Record<string, number>;
  damage_resistances?: string[];
  damage_immunities?: string[];
  damage_vulnerabilities?: string[];
  condition_immunities?: string[];
  saving_throws?: Record<string, string>;
  skills?: Record<string, string>;
  senses?: Record<string, number | string>;
  languages?: string;
  description?: string;
  source?: string;
  all_actions?: MonsterAction[];
}

export interface MonsterListItem {
  id: string;
  slug: string;
  name: string;
  monster_type?: string;
  size?: string;
  cr?: number;
  xp_reward?: number;
  hp_average?: number;
  armor_class: number;
}
