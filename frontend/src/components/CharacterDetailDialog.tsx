import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from './ui/dialog';
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { ScrollArea } from './ui/scroll-area';
import { Button } from './ui/button';
import { Sword, Shield, Heart, Zap, Brain, Users, BookOpen, Package, Star, TrendingUp, Moon, Clock } from 'lucide-react';
import type { Character } from '../types/character';
import { charactersAPI } from '../services/api';
import { useToast } from '../hooks/use-toast';

// XP thresholds to reach each level (PHB)
const XP_THRESHOLDS: Record<number, number> = {
  1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500,
  6: 14000, 7: 23000, 8: 34000, 9: 48000, 10: 64000,
  11: 85000, 12: 100000, 13: 120000, 14: 140000, 15: 165000,
  16: 195000, 17: 225000, 18: 265000, 19: 305000, 20: 355000,
};

interface Props {
  character: Character | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onCharacterUpdated?: (character: Character) => void;
}

function fallbackHP(level: number, constitution: number): number {
  const con = Math.floor((constitution - 10) / 2);
  return Math.max(1, 8 + con + (level - 1) * (5 + con));
}

function mod(score: number) { return Math.floor((score - 10) / 2); }
function modStr(score: number) { const m = mod(score); return m >= 0 ? `+${m}` : `${m}`; }

function StatBox({ icon: Icon, label, value }: { icon: any; label: string; value: number }) {
  return (
    <div className="bg-muted/50 rounded-md p-3 text-center border border-border">
      <Icon className="w-5 h-5 mx-auto mb-1 text-muted-foreground" />
      <div className="text-xs text-muted-foreground font-medium mb-1">{label}</div>
      <div className="text-xl font-bold text-foreground">{value}</div>
      <div className="text-lg font-semibold text-accent">{modStr(value)}</div>
    </div>
  );
}

export default function CharacterDetailDialog({ character, open, onOpenChange, onCharacterUpdated }: Props) {
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [localChar, setLocalChar] = useState<Character | null>(null);

  const char = localChar ?? character;
  if (!char) return null;

  const maxHp = char.max_hp ?? fallbackHP(char.level, char.constitution);
  const hp = char.current_hp ?? maxHp;
  const ac = char.armor_class ?? (10 + mod(char.dexterity));
  const xp = char.experience_points ?? 0;
  const profBonus = char.proficiency_bonus ?? (char.level <= 4 ? 2 : char.level <= 8 ? 3 : char.level <= 12 ? 4 : char.level <= 16 ? 5 : 6);

  const nextLevelXP = char.level < 20 ? XP_THRESHOLDS[char.level + 1] : null;
  const curLevelXP = XP_THRESHOLDS[char.level] ?? 0;
  const xpProgress = nextLevelXP ? Math.min(100, ((xp - curLevelXP) / (nextLevelXP - curLevelXP)) * 100) : 100;
  const levelUpAvailable = nextLevelXP !== null && xp >= nextLevelXP;

  const handleLevelUp = async (takeAverage: boolean) => {
    if (!char) return;
    setIsLoading(true);
    try {
      const updated = await charactersAPI.levelUp(char.id, takeAverage);
      setLocalChar(updated);
      onCharacterUpdated?.(updated);
      toast({ title: `Уровень ${updated.level}!`, description: `HP +${(updated.max_hp ?? 0) - maxHp}` });
    } catch {
      toast({ title: 'Ошибка', description: 'Не удалось повысить уровень', variant: 'destructive' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleRest = async (type: 'short' | 'long', hitDice = 1) => {
    if (!char) return;
    setIsLoading(true);
    try {
      const updated = await charactersAPI.rest(char.id, type, hitDice);
      setLocalChar(updated);
      onCharacterUpdated?.(updated);
      const healed = (updated.current_hp ?? 0) - hp;
      toast({
        title: type === 'long' ? 'Долгий отдых' : 'Короткий отдых',
        description: healed > 0 ? `Восстановлено ${healed} HP` : 'HP уже максимальны',
      });
    } catch {
      toast({ title: 'Ошибка', description: 'Не удалось отдохнуть', variant: 'destructive' });
    } finally {
      setIsLoading(false);
    }
  };

  // Reset local state when dialog closes/character changes
  const handleOpenChange = (v: boolean) => {
    if (!v) setLocalChar(null);
    onOpenChange(v);
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="!max-w-5xl w-[90vw] max-h-[90vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <div className="flex items-center gap-4">
            <Avatar className="w-20 h-20 border-4 border-border shadow-lg">
              <AvatarImage
                src={char.avatar_url?.startsWith('/') ? char.avatar_url : `/${char.avatar_url}`}
                alt={char.name}
                onError={(e) => { (e.target as HTMLImageElement).src = '/assets/images/placeholder-user.jpg'; }}
              />
              <AvatarFallback className="text-3xl font-bold bg-primary text-primary-foreground">
                {char.name[0].toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1 min-w-0">
              <DialogTitle className="text-2xl mb-1">{char.name}</DialogTitle>
              <div className="flex items-center gap-2 flex-wrap">
                <Badge variant="secondary" className="bg-primary/20 text-primary-foreground border-primary/30">
                  {char.class}
                </Badge>
                <Badge variant="outline" className="border-accent/50 text-accent-foreground">
                  {char.race}
                </Badge>
                <Badge className="bg-yellow-500/20 text-yellow-700 dark:text-yellow-400 border-yellow-500/30">
                  Уровень {char.level}
                </Badge>
                <Badge className="bg-purple-500/20 text-purple-700 dark:text-purple-400 border-purple-500/30">
                  Мастерство +{profBonus}
                </Badge>
              </div>
            </div>
          </div>
        </DialogHeader>

        <ScrollArea className="flex-1 pr-4">
          <div className="space-y-5">

            {/* HP / AC / Initiative */}
            <div className="grid grid-cols-3 gap-3">
              <div className="bg-muted/50 rounded-lg p-3 border border-red-500/30">
                <div className="flex items-center gap-1.5 mb-1">
                  <Heart className="w-4 h-4 text-red-500" />
                  <span className="text-sm font-semibold">HP</span>
                </div>
                <div className="text-2xl font-bold text-red-500">{hp} <span className="text-sm text-muted-foreground font-normal">/ {maxHp}</span></div>
                <div className="w-full h-1.5 bg-muted rounded-full mt-2">
                  <div className="h-full bg-red-500 rounded-full transition-all" style={{ width: `${Math.max(0, (hp / maxHp) * 100)}%` }} />
                </div>
              </div>
              <div className="bg-muted/50 rounded-lg p-3 border border-blue-500/30">
                <div className="flex items-center gap-1.5 mb-1">
                  <Shield className="w-4 h-4 text-blue-500" />
                  <span className="text-sm font-semibold">КБ</span>
                </div>
                <div className="text-2xl font-bold text-blue-500">{ac}</div>
              </div>
              <div className="bg-muted/50 rounded-lg p-3 border border-yellow-500/30">
                <div className="flex items-center gap-1.5 mb-1">
                  <Zap className="w-4 h-4 text-yellow-500" />
                  <span className="text-sm font-semibold">Инициатива</span>
                </div>
                <div className="text-2xl font-bold text-yellow-500">{modStr(char.dexterity)}</div>
              </div>
            </div>

            {/* XP bar */}
            <div className="bg-muted/50 rounded-lg p-3 border border-border">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-1.5">
                  <Star className="w-4 h-4 text-amber-500" />
                  <span className="text-sm font-semibold">Опыт (XP)</span>
                </div>
                <span className="text-sm text-muted-foreground">
                  {xp.toLocaleString()} {nextLevelXP ? `/ ${nextLevelXP.toLocaleString()}` : '(макс.)'}
                </span>
              </div>
              <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                <div className="h-full bg-gradient-to-r from-amber-500 to-yellow-400 rounded-full transition-all" style={{ width: `${xpProgress}%` }} />
              </div>
              {levelUpAvailable && (
                <div className="mt-3 p-2 bg-yellow-500/10 border border-yellow-500/40 rounded flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-yellow-500" />
                    <span className="text-sm font-semibold text-yellow-600 dark:text-yellow-400">Доступен уровень {char.level + 1}!</span>
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline" className="h-7 text-xs border-yellow-500/50" disabled={isLoading} onClick={() => handleLevelUp(false)}>
                      Бросить кубик
                    </Button>
                    <Button size="sm" className="h-7 text-xs bg-yellow-500 hover:bg-yellow-400 text-black" disabled={isLoading} onClick={() => handleLevelUp(true)}>
                      Среднее HP
                    </Button>
                  </div>
                </div>
              )}
            </div>

            {/* Rest buttons */}
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                className="flex-1 gap-2 border-blue-500/40 hover:bg-blue-500/10"
                disabled={isLoading || hp >= maxHp}
                onClick={() => handleRest('short', Math.ceil(char.level / 2))}
              >
                <Clock className="w-4 h-4 text-blue-500" />
                Короткий отдых
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="flex-1 gap-2 border-indigo-500/40 hover:bg-indigo-500/10"
                disabled={isLoading || hp >= maxHp}
                onClick={() => handleRest('long')}
              >
                <Moon className="w-4 h-4 text-indigo-500" />
                Долгий отдых
              </Button>
            </div>

            <Separator />

            {/* Ability scores */}
            <div>
              <h3 className="text-sm font-semibold uppercase tracking-wide mb-3 text-muted-foreground">Характеристики</h3>
              <div className="grid grid-cols-3 gap-3">
                <StatBox icon={Sword} label="Сила" value={char.strength} />
                <StatBox icon={Zap} label="Ловкость" value={char.dexterity} />
                <StatBox icon={Shield} label="Телосложение" value={char.constitution} />
                <StatBox icon={Brain} label="Интеллект" value={char.intelligence} />
                <StatBox icon={Users} label="Мудрость" value={char.wisdom} />
                <StatBox icon={Heart} label="Харизма" value={char.charisma} />
              </div>
            </div>

            {/* Saving throws & skills */}
            {(char.saving_throw_proficiencies?.length || char.skill_proficiencies?.length) && (
              <>
                <Separator />
                <div className="grid grid-cols-2 gap-4">
                  {char.saving_throw_proficiencies && char.saving_throw_proficiencies.length > 0 && (
                    <div>
                      <h3 className="text-sm font-semibold uppercase tracking-wide mb-2 text-muted-foreground">Спасброски</h3>
                      <div className="flex flex-wrap gap-1">
                        {char.saving_throw_proficiencies.map(st => (
                          <span key={st} className="text-xs bg-primary/20 text-primary px-2 py-0.5 rounded">{st}</span>
                        ))}
                      </div>
                    </div>
                  )}
                  {char.skill_proficiencies && char.skill_proficiencies.length > 0 && (
                    <div>
                      <h3 className="text-sm font-semibold uppercase tracking-wide mb-2 text-muted-foreground">Навыки</h3>
                      <div className="flex flex-wrap gap-1">
                        {char.skill_proficiencies.map(sk => (
                          <span key={sk} className="text-xs bg-accent/20 text-accent-foreground px-2 py-0.5 rounded">{sk}</span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </>
            )}

            {/* History & Equipment */}
            {char.character_history && (
              <>
                <Separator />
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <BookOpen className="w-4 h-4 text-accent" />
                    <h3 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">История</h3>
                  </div>
                  <p className="text-sm text-foreground leading-relaxed whitespace-pre-wrap">{char.character_history}</p>
                </div>
              </>
            )}
            {char.equipment_and_features && (
              <>
                <Separator />
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <Package className="w-4 h-4 text-accent" />
                    <h3 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">Снаряжение</h3>
                  </div>
                  <p className="text-sm text-foreground leading-relaxed whitespace-pre-wrap">{char.equipment_and_features}</p>
                </div>
              </>
            )}

          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
}
