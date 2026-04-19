import type { Character } from './character';

export interface GameTemplate {
  id: string;
  name: string;
  description: string;
  previewImage: string;
  story: string;
  mapUrl?: string;
  characters?: Character[];
  masterScenario?: string[];
}

