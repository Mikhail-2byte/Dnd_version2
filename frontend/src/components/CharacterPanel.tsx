import { useState } from 'react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar';
import { Shield, Heart, Sword, Zap, Brain, Users, Info, ChevronDown, ChevronUp } from 'lucide-react';
import type { Character } from '../types/character';
import type { Participant } from '../types/game';
import CharacterDetailDialog from './CharacterDetailDialog';
import { createPlayerColorMap, getCharacterOwner, type PlayerColor } from '../utils/playerColors';

interface CharacterPanelProps {
  characters: Character[];
  selectedId?: string | null;
  participants?: Participant[];
  onSelect?: (character: Character) => void;
  onEdit?: (character: Character) => void;
  onDelete?: (character: Character) => void;
  showSelect?: boolean;
}

function fallbackHP(level: number, constitution: number): number {
  const con = Math.floor((constitution - 10) / 2);
  return Math.max(1, 8 + con + (level - 1) * (5 + con));
}

function fallbackAC(dexterity: number): number {
  return 10 + Math.floor((dexterity - 10) / 2);
}

// D&D 5e 18 skills: {key, Russian name, ability}
const SKILLS: { key: string; label: string; ability: keyof Character }[] = [
  { key: 'acrobatics',      label: 'Акробатика',        ability: 'dexterity'    },
  { key: 'animal_handling', label: 'Уход за животными',  ability: 'wisdom'       },
  { key: 'arcana',          label: 'Магия',              ability: 'intelligence' },
  { key: 'athletics',       label: 'Атлетика',           ability: 'strength'     },
  { key: 'deception',       label: 'Обман',              ability: 'charisma'     },
  { key: 'history',         label: 'История',            ability: 'intelligence' },
  { key: 'insight',         label: 'Проницательность',   ability: 'wisdom'       },
  { key: 'intimidation',    label: 'Запугивание',        ability: 'charisma'     },
  { key: 'investigation',   label: 'Анализ',             ability: 'intelligence' },
  { key: 'medicine',        label: 'Медицина',           ability: 'wisdom'       },
  { key: 'nature',          label: 'Природа',            ability: 'intelligence' },
  { key: 'perception',      label: 'Внимательность',     ability: 'wisdom'       },
  { key: 'performance',     label: 'Выступление',        ability: 'charisma'     },
  { key: 'persuasion',      label: 'Убеждение',          ability: 'charisma'     },
  { key: 'religion',        label: 'Религия',            ability: 'intelligence' },
  { key: 'sleight_of_hand', label: 'Ловкость рук',       ability: 'dexterity'    },
  { key: 'stealth',         label: 'Скрытность',         ability: 'dexterity'    },
  { key: 'survival',        label: 'Выживание',          ability: 'wisdom'       },
];

const SAVE_ABILITIES: { key: string; label: string; ability: keyof Character }[] = [
  { key: 'strength',     label: 'СИЛ', ability: 'strength'     },
  { key: 'dexterity',    label: 'ЛОВ', ability: 'dexterity'    },
  { key: 'constitution', label: 'ТЕЛ', ability: 'constitution' },
  { key: 'intelligence', label: 'ИНТ', ability: 'intelligence' },
  { key: 'wisdom',       label: 'МДР', ability: 'wisdom'       },
  { key: 'charisma',     label: 'ХАР', ability: 'charisma'     },
];

function profBonus(level: number): number {
  return Math.floor((level - 1) / 4) + 2;
}

function mod(score: number): number {
  return Math.floor((score - 10) / 2);
}

function fmtMod(n: number): string {
  return (n >= 0 ? '+' : '') + n;
}

export default function CharacterPanel({
  characters,
  selectedId,
  participants = [],
  onSelect,
  onEdit,
  onDelete,
  showSelect = true,
}: CharacterPanelProps) {
  const [selectedCharacter, setSelectedCharacter] = useState<Character | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  
  // Создаем карту цветов для участников
  const playerColorMap = createPlayerColorMap(participants);

  if (characters.length === 0) {
    return (
      <div className="flex-1 rounded-lg border-2 border-border bg-card p-8 flex items-center justify-center">
        <p className="text-muted-foreground text-lg">У вас пока нет персонажей. Создайте первого!</p>
      </div>
    );
  }

  const handleSelectCharacter = (character: Character) => {
    onSelect?.(character);
  };

  const handleShowDetails = (character: Character) => {
    setSelectedCharacter(character);
    setIsDialogOpen(true);
  };

  return (
    <>
      <div className="flex-1 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
        {characters.map((character) => {
          const maxHp = character.max_hp ?? fallbackHP(character.level || 1, character.constitution);
          const hp = character.current_hp ?? maxHp;
          const ac = character.armor_class ?? fallbackAC(character.dexterity);
          
          const isSelected = selectedId === character.id;
          const owner = getCharacterOwner(character.id, participants);
          const ownerColor = owner ? playerColorMap.get(owner.user_id) : null;
          
          // Определяем классы для границы карточки
          let borderClasses = 'border-2';
          if (ownerColor) {
            borderClasses += ` ${ownerColor.border} ${ownerColor.ring ? `ring-2 ${ownerColor.ring}` : ''}`;
          } else if (isSelected) {
            borderClasses += ' border-accent shadow-md ring-1 ring-accent/30';
          } else {
            borderClasses += ' border-border';
          }
          
          return (
            <Card
              key={character.id}
              className={`p-3 ${borderClasses} transition-all bg-card/95 ${
                owner ? 'shadow-md' : ''
              }`}
            >
              <div className="flex flex-col gap-2">
                {/* Аватар и имя */}
                <div className="flex flex-col items-center gap-2">
                  <Avatar className="w-16 h-16 border-2 border-border shadow-sm">
                    <AvatarImage 
                      src={character.avatar_url?.startsWith('/') ? character.avatar_url : `/${character.avatar_url}`} 
                      alt={character.name}
                      onError={(e) => {
                        const target = e.target as HTMLImageElement;
                        target.src = '/assets/images/placeholder-user.jpg';
                      }}
                    />
                    <AvatarFallback className="text-lg font-bold bg-primary text-primary-foreground">
                      {character.name[0].toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  
                  <div className="text-center w-full">
                    <h3 className="text-sm font-bold text-foreground truncate">{character.name}</h3>
                    <div className="flex items-center justify-center gap-1.5 mt-1 flex-wrap">
                      <Badge variant="secondary" className="bg-primary/20 text-primary-foreground border-primary/30 text-xs px-1.5 py-0">
                        {character.class}
                      </Badge>
                      <span className="text-xs text-muted-foreground truncate">{character.race}</span>
                    </div>
                    {owner && (
                      <div className={`mt-1.5 text-xs font-medium px-2 py-0.5 rounded-full inline-block ${ownerColor?.bg || ''} ${ownerColor?.text || 'text-muted-foreground'}`}>
                        Выбран: {owner.username}
                      </div>
                    )}
                  </div>
                </div>

                {/* HP и AC - компактно */}
                <div className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-1">
                      <Heart className="w-3 h-3 text-red-600" />
                      <span className="font-medium text-foreground">{hp}/{maxHp}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Shield className="w-3 h-3 text-blue-600" />
                      <span className="font-medium text-foreground">{ac}</span>
                    </div>
                  </div>
                  <div className="w-full h-1.5 bg-muted rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-red-600 to-red-500 transition-all"
                      style={{ width: `${(hp / maxHp) * 100}%` }}
                    />
                  </div>
                </div>

                {/* Основные характеристики - компактно */}
                <div className="grid grid-cols-3 gap-1.5 pt-1.5 border-t border-border">
                  <StatBox icon={Sword} label="СИЛ" value={character.strength} />
                  <StatBox icon={Zap} label="ЛОВ" value={character.dexterity} />
                  <StatBox icon={Shield} label="ТЕЛ" value={character.constitution} />
                  <StatBox icon={Brain} label="ИНТ" value={character.intelligence} />
                  <StatBox icon={Users} label="МДР" value={character.wisdom} />
                  <StatBox icon={Heart} label="ХАР" value={character.charisma} />
                </div>

                {/* Кнопки действий */}
                <div className="flex flex-col sm:flex-row gap-2 pt-2 border-t border-border">
                  {showSelect && (
                    <Button
                      onClick={() => handleSelectCharacter(character)}
                      variant={isSelected ? "default" : "outline"}
                      size="sm"
                      className="flex-1 text-xs"
                    >
                      {isSelected ? 'Выбран' : 'Выбрать'}
                    </Button>
                  )}
                  <Button
                    onClick={() => handleShowDetails(character)}
                    variant="ghost"
                    size="sm"
                    className="flex-1 text-xs"
                  >
                    <Info className="w-3 h-3 mr-1.5" />
                    Детали
                  </Button>
                </div>

                {/* Expand toggle */}
                <Button
                  variant="ghost"
                  size="sm"
                  className="w-full text-xs text-muted-foreground h-6 mt-1"
                  onClick={() => setExpandedId(expandedId === character.id ? null : character.id)}
                >
                  {expandedId === character.id
                    ? <><ChevronUp className="w-3 h-3 mr-1" />Скрыть</>
                    : <><ChevronDown className="w-3 h-3 mr-1" />Умения и спасброски</>}
                </Button>

                {/* Expanded section */}
                {expandedId === character.id && (() => {
                  const pb = character.proficiency_bonus ?? profBonus(character.level || 1);
                  const saves = character.saving_throw_proficiencies ?? [];
                  const skillProfs = character.skill_proficiencies ?? [];
                  const dexMod = mod(character.dexterity);
                  return (
                    <div className="pt-1 border-t border-border space-y-2 text-xs">
                      {/* Quick stats row */}
                      <div className="flex justify-between text-muted-foreground">
                        <span>Инициатива: <span className="text-foreground font-medium">{fmtMod(dexMod)}</span></span>
                        <span>Проф.: <span className="text-foreground font-medium">+{pb}</span></span>
                        <span>Скорость: <span className="text-foreground font-medium">30 фт.</span></span>
                      </div>

                      {/* Saving throws */}
                      <div>
                        <p className="text-[10px] uppercase tracking-wide text-muted-foreground mb-1 font-semibold">Спасброски</p>
                        <div className="grid grid-cols-3 gap-1">
                          {SAVE_ABILITIES.map(({ key, label, ability }) => {
                            const isProficient = saves.includes(key);
                            const bonus = mod(character[ability] as number) + (isProficient ? pb : 0);
                            return (
                              <div key={key} className={`flex items-center gap-0.5 rounded px-1 py-0.5 ${isProficient ? 'bg-primary/10' : 'bg-muted/30'}`}>
                                <span className={`w-2 h-2 rounded-full shrink-0 ${isProficient ? 'bg-primary' : 'bg-muted-foreground/30'}`} />
                                <span className="text-muted-foreground">{label}</span>
                                <span className={`ml-auto font-medium ${isProficient ? 'text-primary' : 'text-foreground'}`}>{fmtMod(bonus)}</span>
                              </div>
                            );
                          })}
                        </div>
                      </div>

                      {/* Skills */}
                      <div>
                        <p className="text-[10px] uppercase tracking-wide text-muted-foreground mb-1 font-semibold">Умения</p>
                        <div className="grid grid-cols-2 gap-0.5">
                          {SKILLS.map(({ key, label, ability }) => {
                            const isProficient = skillProfs.includes(key);
                            const bonus = mod(character[ability] as number) + (isProficient ? pb : 0);
                            return (
                              <div key={key} className="flex items-center gap-0.5">
                                <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${isProficient ? 'bg-primary' : 'bg-muted-foreground/30'}`} />
                                <span className={`truncate ${isProficient ? 'text-foreground' : 'text-muted-foreground'}`}>{label}</span>
                                <span className={`ml-auto font-medium shrink-0 ${isProficient ? 'text-primary' : ''}`}>{fmtMod(bonus)}</span>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    </div>
                  );
                })()}
              </div>
            </Card>
          );
        })}
      </div>

      <CharacterDetailDialog
        character={selectedCharacter}
        open={isDialogOpen}
        onOpenChange={setIsDialogOpen}
        onCharacterUpdated={(updated) => setSelectedCharacter(updated)}
      />
    </>
  );
}

// Компонент для отображения характеристики с иконкой и модификатором
function StatBox({ icon: Icon, label, value }: { icon: any; label: string; value: number }) {
  const modifier = Math.floor((value - 10) / 2);
  return (
    <div className="bg-muted/50 rounded p-1 text-center border border-border">
      <Icon className="w-3 h-3 mx-auto text-muted-foreground" />
      <div className="text-[10px] text-muted-foreground font-medium leading-tight">{label}</div>
      <div className="text-sm font-bold text-foreground leading-tight">{value}</div>
      <div className="text-[10px] text-accent font-medium leading-tight">
        {modifier >= 0 ? '+' : ''}{modifier}
      </div>
    </div>
  );
}

