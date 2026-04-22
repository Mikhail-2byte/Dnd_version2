export interface LootEntry {
  item_type: 'weapon' | 'armor' | 'item';
  item_id: string;
  quantity: number;
}

export interface ScenarioNPC {
  id: string;
  scenario_id: string;
  name: string;
  x: number;
  y: number;
  image_url: string | null;
  is_hidden: boolean;
  monster_slug: string | null;
  loot: LootEntry[] | null;
  notes: string | null;
}

export interface ScenarioHiddenItem {
  id: string;
  scenario_id: string;
  name: string;
  x: number;
  y: number;
  image_url: string | null;
  item_type: 'weapon' | 'armor' | 'item';
  item_id: string | null;
  quantity: number;
  notes: string | null;
}

export interface Scenario {
  id: string;
  owner_id: string;
  name: string;
  story: string | null;
  map_url: string | null;
  created_at: string;
  updated_at: string | null;
  npcs: ScenarioNPC[];
  items: ScenarioHiddenItem[];
}

export interface ScenarioListItem {
  id: string;
  owner_id: string;
  name: string;
  story: string | null;
  map_url: string | null;
  created_at: string;
  npc_count: number;
  item_count: number;
}
