import { useState } from 'react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar';
import { Shield, Heart, Sword, Zap, Brain, Users, Info } from 'lucide-react';
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
}

function fallbackHP(level: number, constitution: number): number {
  const con = Math.floor((constitution - 10) / 2);
  return Math.max(1, 8 + con + (level - 1) * (5 + con));
}

function fallbackAC(dexterity: number): number {
  return 10 + Math.floor((dexterity - 10) / 2);
}

export default function CharacterPanel({
  characters,
  selectedId,
  participants = [],
  onSelect,
  onEdit,
  onDelete,
}: CharacterPanelProps) {
  const [selectedCharacter, setSelectedCharacter] = useState<Character | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  
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
                  <Button
                    onClick={() => handleSelectCharacter(character)}
                    variant={isSelected ? "default" : "outline"}
                    size="sm"
                    className="flex-1 text-xs"
                  >
                    {isSelected ? 'Выбран' : 'Выбрать'}
                  </Button>
                  <Button
                    onClick={() => handleShowDetails(character)}
                    variant="ghost"
                    size="sm"
                    className="flex-1 text-xs"
                  >
                    <Info className="w-3 h-3 mr-1.5" />
                    Подробнее
                  </Button>
                </div>
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

