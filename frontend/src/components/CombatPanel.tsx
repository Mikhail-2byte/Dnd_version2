import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { ScrollArea } from './ui/scroll-area';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from './ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Input } from './ui/input';
import { useAuthStore } from '../store/authStore';
import { useGameStore } from '../store/gameStore';
import { combatAPI } from '../services/api';
import { socketService } from '../services/socket';
import type { CombatSession, CombatParticipant } from '../types/combat';
import HPBar from './HPBar';
import { Sword, Shield, Heart, Zap, X, Crosshair } from 'lucide-react';

interface CombatPanelProps {
  gameId: string;
  isMaster: boolean;
  onCombatChange?: (combatId: string | null) => void;
}

export default function CombatPanel({ gameId, isMaster, onCombatChange }: CombatPanelProps) {
  const { user } = useAuthStore();
  const [combat, setCombat] = useState<CombatSession | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedParticipants, setSelectedParticipants] = useState<string[]>([]);
  
  // Состояние для модального окна атаки
  const [attackDialogOpen, setAttackDialogOpen] = useState(false);
  const [attackingParticipant, setAttackingParticipant] = useState<CombatParticipant | null>(null);
  const [selectedTargetId, setSelectedTargetId] = useState<string>('');
  const [attackModifier, setAttackModifier] = useState(0);

  // Загружаем текущий бой при монтировании
  useEffect(() => {
    loadCurrentCombat();
  }, [gameId]);

  // Подписываемся на WebSocket события
  useEffect(() => {
    const handleCombatStarted = (data: CombatSession) => {
      setCombat(data);
    };

    const handleInitiativeRolled = (data: CombatParticipant) => {
      if (combat) {
        setCombat({
          ...combat,
          participants: combat.participants.map(p =>
            p.id === data.id ? data : p
          ),
        });
      }
    };

    const handleCombatEnded = () => {
      setCombat(null);
    };

    const handleCombatAttack = (data: any) => {
      // Обновляем состояние, если нужно
      loadCurrentCombat();
    };

    const handleCombatDamage = (data: {
      participant_id: string;
      damage: number;
      current_hp: number;
      max_hp: number;
      was_defeated: boolean;
    }) => {
      if (combat) {
        setCombat({
          ...combat,
          participants: combat.participants.map(p =>
            p.id === data.participant_id
              ? { ...p, current_hp: data.current_hp, max_hp: data.max_hp }
              : p
          ),
        });
      }
    };

    const handleCombatHeal = (data: {
      participant_id: string;
      healing: number;
      current_hp: number;
      max_hp: number;
    }) => {
      if (combat) {
        setCombat({
          ...combat,
          participants: combat.participants.map(p =>
            p.id === data.participant_id
              ? { ...p, current_hp: data.current_hp, max_hp: data.max_hp }
              : p
          ),
        });
      }
    };

    socketService.onCombatStarted(handleCombatStarted);
    socketService.onInitiativeRolled(handleInitiativeRolled);
    socketService.onCombatEnded(handleCombatEnded);
    socketService.onCombatAttack(handleCombatAttack);
    socketService.onCombatDamage(handleCombatDamage);
    socketService.onCombatHeal(handleCombatHeal);

    return () => {
      socketService.off('combat:started');
      socketService.off('combat:initiative_rolled');
      socketService.off('combat:ended');
      socketService.off('combat:attack');
      socketService.off('combat:damage');
      socketService.off('combat:heal');
    };
  }, [combat]);

  const updateCombat = (c: CombatSession | null) => {
    setCombat(c);
    onCombatChange?.(c?.id ?? null);
  };

  const loadCurrentCombat = async () => {
    try {
      setIsLoading(true);
      const currentCombat = await combatAPI.getCurrent(gameId);
      updateCombat(currentCombat);
    } catch (error) {
      console.error('Error loading combat:', error);
      updateCombat(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartCombat = async () => {
    if (selectedParticipants.length === 0) {
      alert('Выберите участников для боя');
      return;
    }

    try {
      setIsLoading(true);
      const newCombat = await combatAPI.start(gameId, {
        participant_ids: selectedParticipants,
      });
      updateCombat(newCombat);
      setSelectedParticipants([]);
    } catch (error: any) {
      console.error('Error starting combat:', error);
      alert(error.response?.data?.detail || 'Ошибка при начале боя');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRollInitiative = async (participantId: string) => {
    if (!combat) return;

    try {
      await combatAPI.rollInitiative(gameId, combat.id, {
        participant_id: participantId,
      });
    } catch (error: any) {
      console.error('Error rolling initiative:', error);
      alert(error.response?.data?.detail || 'Ошибка при броске инициативы');
    }
  };

  const handleEndCombat = async () => {
    if (!combat) return;

    try {
      setIsLoading(true);
      await combatAPI.end(gameId, combat.id);
      updateCombat(null);
    } catch (error: any) {
      console.error('Error ending combat:', error);
      alert(error.response?.data?.detail || 'Ошибка при завершении боя');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAttackClick = (participant: CombatParticipant) => {
    setAttackingParticipant(participant);
    setSelectedTargetId('');
    setAttackModifier(0);
    setAttackDialogOpen(true);
  };

  const handlePerformAttack = async () => {
    if (!combat || !attackingParticipant || !selectedTargetId) return;

    try {
      setIsLoading(true);
      await combatAPI.attack(
        gameId,
        combat.id,
        attackingParticipant.id,
        selectedTargetId,
        undefined, // Автоматический бросок
        attackModifier
      );
      setAttackDialogOpen(false);
    } catch (error: any) {
      console.error('Error performing attack:', error);
      alert(error.response?.data?.detail || 'Ошибка при выполнении атаки');
    } finally {
      setIsLoading(false);
    }
  };

  // Получаем упорядоченный список участников по инициативе
  const orderedParticipants = combat
    ? [...combat.participants].sort((a, b) => {
        const aInitiative = a.initiative ?? -1;
        const bInitiative = b.initiative ?? -1;
        return bInitiative - aInitiative;
      })
    : [];

  // Получаем текущего участника (чей ход)
  const currentParticipant =
    combat && orderedParticipants.length > 0
      ? orderedParticipants[combat.current_turn_index % orderedParticipants.length]
      : null;

  if (!combat) {
    // Панель для начала боя (только для мастера)
    if (!isMaster) {
      return null;
    }

    // TODO: Получить список доступных персонажей и токенов для выбора
    // Пока просто показываем кнопку "Начать бой" с заглушкой
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sword className="w-5 h-5" />
            Боевая система
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-4">
            Выберите участников для начала боевой сессии
          </p>
          <Button onClick={handleStartCombat} disabled={isLoading || selectedParticipants.length === 0}>
            Начать бой
          </Button>
          <p className="text-xs text-muted-foreground mt-4">
            Примечание: Выбор участников будет реализован в следующем шаге
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Sword className="w-5 h-5" />
            Бой (Раунд {combat.round_number})
          </CardTitle>
          {isMaster && (
            <Button
              variant="destructive"
              size="sm"
              onClick={handleEndCombat}
              disabled={isLoading}
            >
              <X className="w-4 h-4 mr-2" />
              Завершить бой
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[400px]">
          <div className="space-y-2">
            {orderedParticipants.map((participant, index) => {
              const isCurrentTurn = participant.id === currentParticipant?.id;
              const participantName =
                participant.character_name || participant.token_name || 'Неизвестно';

              return (
                <div
                  key={participant.id}
                  className={`p-3 border rounded-lg ${
                    isCurrentTurn
                      ? 'border-primary bg-primary/10'
                      : 'border-border'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Badge variant={isCurrentTurn ? 'default' : 'outline'}>
                        {index + 1}
                      </Badge>
                      <span className="font-medium">{participantName}</span>
                      {isCurrentTurn && (
                        <Badge variant="default" className="ml-2">
                          Текущий ход
                        </Badge>
                      )}
                    </div>
                    {participant.initiative !== null && participant.initiative !== undefined ? (
                      <Badge variant="secondary">
                        Инициатива: {participant.initiative}
                      </Badge>
                    ) : (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleRollInitiative(participant.id)}
                        disabled={isLoading}
                      >
                        <Zap className="w-4 h-4 mr-1" />
                        Бросить инициативу
                      </Button>
                    )}
                  </div>
                  <div className="mb-2">
                    <HPBar current={participant.current_hp} max={participant.max_hp} />
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-sm mb-2">
                    <div className="flex items-center gap-1">
                      <Shield className="w-4 h-4 text-blue-500" />
                      <span>КБ: {participant.armor_class}</span>
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {participant.is_player_controlled ? 'Игрок' : 'Мастер'}
                    </div>
                  </div>
                  {(isMaster || participant.is_player_controlled) && (
                    <Button
                      size="sm"
                      variant="outline"
                      className="w-full mt-2"
                      onClick={() => handleAttackClick(participant)}
                      disabled={isLoading || participant.current_hp <= 0}
                    >
                      <Crosshair className="w-4 h-4 mr-1" />
                      Атаковать
                    </Button>
                  )}
                  {participant.conditions && participant.conditions.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {participant.conditions.map((condition, idx) => (
                        <Badge key={idx} variant="outline" className="text-xs">
                          {condition}
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </ScrollArea>
      </CardContent>

      {/* Модальное окно атаки */}
      <Dialog open={attackDialogOpen} onOpenChange={setAttackDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Атака</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <label className="text-sm font-medium mb-2 block">
                Атакующий: {attackingParticipant?.character_name || attackingParticipant?.token_name || 'Неизвестно'}
              </label>
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Цель</label>
              <Select value={selectedTargetId} onValueChange={setSelectedTargetId}>
                <SelectTrigger>
                  <SelectValue placeholder="Выберите цель" />
                </SelectTrigger>
                <SelectContent>
                  {orderedParticipants
                    .filter(p => p.id !== attackingParticipant?.id && p.current_hp > 0)
                    .map(p => (
                      <SelectItem key={p.id} value={p.id}>
                        {p.character_name || p.token_name || 'Неизвестно'} (КБ: {p.armor_class})
                      </SelectItem>
                    ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Модификатор атаки</label>
              <Input
                type="number"
                value={attackModifier}
                onChange={(e) => setAttackModifier(parseInt(e.target.value) || 0)}
                placeholder="0"
              />
            </div>
            <div className="text-sm text-muted-foreground">
              Бросок d20 будет выполнен автоматически. Попадание: бросок + модификатор ≥ КБ цели.
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setAttackDialogOpen(false)}>
              Отмена
            </Button>
            <Button onClick={handlePerformAttack} disabled={!selectedTargetId || isLoading}>
              Атаковать
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Card>
  );
}

