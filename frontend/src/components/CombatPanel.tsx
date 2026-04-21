import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { ScrollArea } from './ui/scroll-area';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from './ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Input } from './ui/input';
import { combatAPI } from '../services/api';
import { socketService } from '../services/socket';
import type { CombatSession, CombatParticipant } from '../types/combat';
import HPBar from './HPBar';
import { Sword, Shield, Zap, X, Crosshair, SkipForward, Heart, Skull } from 'lucide-react';

interface CombatPanelProps {
  gameId: string;
  isMaster: boolean;
  onCombatChange?: (combatId: string | null) => void;
}

export default function CombatPanel({ gameId, isMaster, onCombatChange }: CombatPanelProps) {
  const [combat, setCombat] = useState<CombatSession | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedParticipants] = useState<string[]>([]);

  const [attackDialogOpen, setAttackDialogOpen] = useState(false);
  const [attackingParticipant, setAttackingParticipant] = useState<CombatParticipant | null>(null);
  const [selectedTargetId, setSelectedTargetId] = useState<string>('');
  const [attackModifier, setAttackModifier] = useState(0);
  const [lastAttackResult, setLastAttackResult] = useState<string | null>(null);

  const [deathSaveResult, setDeathSaveResult] = useState<Record<string, string>>({});

  useEffect(() => {
    loadCurrentCombat();
  }, [gameId]);

  useEffect(() => {
    const handleCombatStarted = (data: CombatSession) => {
      setCombat(data);
      onCombatChange?.(data.id);
    };

    const handleInitiativeRolled = (data: CombatParticipant) => {
      setCombat(prev => prev ? {
        ...prev,
        participants: prev.participants.map(p => p.id === data.id ? data : p),
      } : prev);
    };

    const handleTurnChanged = (data: CombatSession) => {
      setCombat(data);
    };

    const handleCombatEnded = () => {
      setCombat(null);
      onCombatChange?.(null);
    };

    const handleCombatDamage = (data: {
      participant_id: string; damage: number; current_hp: number; max_hp: number; was_defeated: boolean;
    }) => {
      setCombat(prev => prev ? {
        ...prev,
        participants: prev.participants.map(p =>
          p.id === data.participant_id ? { ...p, current_hp: data.current_hp, max_hp: data.max_hp } : p
        ),
      } : prev);
    };

    const handleCombatHeal = (data: {
      participant_id: string; healing: number; current_hp: number; max_hp: number;
    }) => {
      setCombat(prev => prev ? {
        ...prev,
        participants: prev.participants.map(p =>
          p.id === data.participant_id ? { ...p, current_hp: data.current_hp, max_hp: data.max_hp } : p
        ),
      } : prev);
    };

    const handleCombatAttack = () => loadCurrentCombat();

    socketService.onCombatStarted(handleCombatStarted);
    socketService.onInitiativeRolled(handleInitiativeRolled);
    socketService.onCombatEnded(handleCombatEnded);
    socketService.onCombatAttack(handleCombatAttack);
    socketService.onCombatDamage(handleCombatDamage);
    socketService.onCombatHeal(handleCombatHeal);
    socketService.onTurnChanged(handleTurnChanged);

    return () => {
      socketService.off('combat:started');
      socketService.off('combat:initiative_rolled');
      socketService.off('combat:ended');
      socketService.off('combat:attack');
      socketService.off('combat:damage');
      socketService.off('combat:heal');
      socketService.off('combat:turn_changed');
    };
  }, []);

  const updateCombat = (c: CombatSession | null) => {
    setCombat(c);
    onCombatChange?.(c?.id ?? null);
  };

  const loadCurrentCombat = async () => {
    try {
      setIsLoading(true);
      const currentCombat = await combatAPI.getCurrent(gameId);
      updateCombat(currentCombat);
    } catch {
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
      const newCombat = await combatAPI.start(gameId, { participant_ids: selectedParticipants });
      updateCombat(newCombat);
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Ошибка при начале боя');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRollInitiative = async (participantId: string) => {
    if (!combat) return;
    try {
      await combatAPI.rollInitiative(gameId, combat.id, { participant_id: participantId });
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Ошибка при броске инициативы');
    }
  };

  const handleNextTurn = async () => {
    if (!combat) return;
    try {
      setIsLoading(true);
      const updated = await combatAPI.nextTurn(gameId, combat.id);
      updateCombat(updated);
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Ошибка при смене хода');
    } finally {
      setIsLoading(false);
    }
  };

  const handleEndCombat = async () => {
    if (!combat) return;
    try {
      setIsLoading(true);
      await combatAPI.end(gameId, combat.id);
      updateCombat(null);
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Ошибка при завершении боя');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAttackClick = (participant: CombatParticipant) => {
    setAttackingParticipant(participant);
    setSelectedTargetId('');
    setAttackModifier(0);
    setLastAttackResult(null);
    setAttackDialogOpen(true);
  };

  const handlePerformAttack = async () => {
    if (!combat || !attackingParticipant || !selectedTargetId) return;
    try {
      setIsLoading(true);
      const result = await combatAPI.attack(gameId, combat.id, attackingParticipant.id, selectedTargetId, {
        modifier: attackModifier,
      });
      const target = orderedParticipants.find(p => p.id === selectedTargetId);
      const targetName = target?.character_name || target?.token_name || 'Цель';
      if (result.hit) {
        setLastAttackResult(
          `✅ Попадание! Бросок: ${result.attack_roll}${result.critical ? ' (КРИТ!)' : ''} vs КБ ${result.target_ac} → ${result.damage} урона по ${targetName}`
        );
      } else {
        setLastAttackResult(
          `❌ Промах! Бросок: ${result.attack_roll}${result.auto_miss ? ' (авт. промах)' : ''} vs КБ ${result.target_ac}`
        );
      }
      await loadCurrentCombat();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Ошибка при выполнении атаки');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeathSave = async (participant: CombatParticipant) => {
    if (!combat) return;
    try {
      const result = await combatAPI.deathSave(gameId, combat.id, participant.id);
      let msg = `Спасбросок от смерти: ${result.roll} — `;
      if (result.stabilized) msg += result.regained_hp ? `🌟 Возрождение! +${result.regained_hp} HP` : '✅ Стабилизирован';
      else if (result.died) msg += '💀 Погиб';
      else if (result.success) msg += `✅ Успех (${result.death_saves_success}/3)`;
      else msg += `❌ Провал (${result.death_saves_failure}/3)`;
      setDeathSaveResult(prev => ({ ...prev, [participant.id]: msg }));
      await loadCurrentCombat();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Ошибка спасброска');
    }
  };

  const orderedParticipants = combat
    ? [...combat.participants].sort((a, b) => (b.initiative ?? -1) - (a.initiative ?? -1))
    : [];

  const currentParticipant =
    combat && orderedParticipants.length > 0
      ? orderedParticipants[combat.current_turn_index % orderedParticipants.length]
      : null;

  const isCurrentUserTurn = currentParticipant?.is_player_controlled &&
    !isMaster; // simplified check — player controls their own turn

  if (!combat) {
    if (!isMaster) return null;
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
        <div className="flex items-center justify-between flex-wrap gap-2">
          <CardTitle className="flex items-center gap-2">
            <Sword className="w-5 h-5" />
            Бой · Раунд {combat.round_number}
          </CardTitle>
          <div className="flex gap-2">
            {isMaster && (
              <Button size="sm" variant="outline" onClick={handleNextTurn} disabled={isLoading}>
                <SkipForward className="w-4 h-4 mr-1" />
                След. ход
              </Button>
            )}
            {isMaster && (
              <Button size="sm" variant="destructive" onClick={handleEndCombat} disabled={isLoading}>
                <X className="w-4 h-4 mr-1" />
                Завершить
              </Button>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <ScrollArea className="h-[480px]">
          <div className="space-y-2">
            {orderedParticipants.map((participant) => {
              const isCurrentTurn = participant.id === currentParticipant?.id;
              const participantName = participant.character_name || participant.token_name || 'Неизвестно';
              const isDying = participant.current_hp <= 0 && !participant.is_dead;
              const isDead = participant.is_dead;

              return (
                <div
                  key={participant.id}
                  className={`p-3 border rounded-lg ${
                    isDead ? 'border-gray-700 bg-gray-900/30 opacity-60' :
                    isDying ? 'border-red-500 bg-red-950/20' :
                    isCurrentTurn ? 'border-primary bg-primary/10' : 'border-border'
                  }`}
                >
                  {/* Header row */}
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-medium">{participantName}</span>
                      {isCurrentTurn && !isDead && (
                        <Badge variant="default" className="text-xs">Текущий ход</Badge>
                      )}
                      {isDying && <Badge variant="destructive" className="text-xs">Без сознания</Badge>}
                      {isDead && <Badge variant="outline" className="text-xs text-gray-500">Мёртв</Badge>}
                    </div>
                    {participant.initiative !== null && participant.initiative !== undefined ? (
                      <Badge variant="secondary" className="text-xs">
                        Инициатива: {participant.initiative}
                      </Badge>
                    ) : (
                      <Button size="sm" variant="outline" onClick={() => handleRollInitiative(participant.id)} disabled={isLoading}>
                        <Zap className="w-3 h-3 mr-1" />
                        Инициатива
                      </Button>
                    )}
                  </div>

                  {/* HP bar */}
                  {!isDead && (
                    <div className="mb-2">
                      <HPBar current={participant.current_hp} max={participant.max_hp} />
                    </div>
                  )}

                  {/* Stats row */}
                  <div className="flex items-center gap-3 text-sm mb-2">
                    <span className="flex items-center gap-1 text-muted-foreground">
                      <Shield className="w-3 h-3" />КБ {participant.armor_class}
                    </span>
                    <span className="flex items-center gap-1 text-muted-foreground">
                      <Heart className="w-3 h-3" />{participant.current_hp}/{participant.max_hp}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {participant.is_player_controlled ? 'Игрок' : 'НПС'}
                    </span>
                  </div>

                  {/* Action economy (only for current turn participant) */}
                  {isCurrentTurn && !isDying && !isDead && (
                    <div className="flex gap-3 mb-2 text-xs">
                      <span className={participant.actions_used ? 'text-muted-foreground line-through' : 'text-green-500 font-medium'}>
                        ⚔️ Действие
                      </span>
                      <span className={participant.bonus_actions_used ? 'text-muted-foreground line-through' : 'text-blue-500 font-medium'}>
                        ⚡ Бонус
                      </span>
                      <span className={participant.reaction_used ? 'text-muted-foreground line-through' : 'text-yellow-500 font-medium'}>
                        🛡️ Реакция
                      </span>
                    </div>
                  )}

                  {/* Resistances */}
                  {(participant.damage_immunities?.length || participant.damage_resistances?.length || participant.damage_vulnerabilities?.length) && (
                    <div className="text-xs text-muted-foreground mb-2 space-y-0.5">
                      {participant.damage_immunities?.length ? (
                        <span className="block">🛡️ Иммун: {participant.damage_immunities.join(', ')}</span>
                      ) : null}
                      {participant.damage_resistances?.length ? (
                        <span className="block">🔰 Сопрот: {participant.damage_resistances.join(', ')}</span>
                      ) : null}
                      {participant.damage_vulnerabilities?.length ? (
                        <span className="block">⚠️ Уязвим: {participant.damage_vulnerabilities.join(', ')}</span>
                      ) : null}
                    </div>
                  )}

                  {/* Conditions */}
                  {participant.conditions && participant.conditions.length > 0 && (
                    <div className="flex flex-wrap gap-1 mb-2">
                      {participant.conditions.map((condition, idx) => (
                        <Badge key={idx} variant="outline" className="text-xs">
                          {condition}
                        </Badge>
                      ))}
                    </div>
                  )}

                  {/* Death save section */}
                  {isDying && (
                    <div className="mt-2 p-2 bg-red-950/30 rounded border border-red-900">
                      <p className="text-xs font-medium text-red-400 mb-1">Спасброски от смерти</p>
                      <div className="flex gap-4 text-xs mb-2">
                        <span>
                          ✅ {Array.from({ length: 3 }, (_, i) =>
                            <span key={i}>{i < (participant.death_saves_success || 0) ? '●' : '○'}</span>
                          )}
                        </span>
                        <span>
                          ❌ {Array.from({ length: 3 }, (_, i) =>
                            <span key={i}>{i < (participant.death_saves_failure || 0) ? '●' : '○'}</span>
                          )}
                        </span>
                      </div>
                      {deathSaveResult[participant.id] && (
                        <p className="text-xs text-muted-foreground mb-1">{deathSaveResult[participant.id]}</p>
                      )}
                      {(isMaster || (isCurrentTurn && participant.is_player_controlled)) && (
                        <Button size="sm" variant="destructive" className="w-full text-xs h-7"
                          onClick={() => handleDeathSave(participant)} disabled={isLoading}>
                          <Skull className="w-3 h-3 mr-1" />
                          Бросить спасбросок от смерти
                        </Button>
                      )}
                    </div>
                  )}

                  {/* Attack button */}
                  {!isDead && !isDying && (isMaster || participant.is_player_controlled) && (
                    <Button
                      size="sm"
                      variant="outline"
                      className="w-full mt-2"
                      onClick={() => handleAttackClick(participant)}
                      disabled={isLoading}
                    >
                      <Crosshair className="w-4 h-4 mr-1" />
                      Атаковать
                    </Button>
                  )}
                </div>
              );
            })}
          </div>
        </ScrollArea>
      </CardContent>

      {/* Attack dialog */}
      <Dialog open={attackDialogOpen} onOpenChange={setAttackDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Атака — {attackingParticipant?.character_name || attackingParticipant?.token_name}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
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
            <p className="text-xs text-muted-foreground">
              d20 бросается автоматически. Попадание: бросок + модификатор ≥ КБ цели.
            </p>
            {lastAttackResult && (
              <div className="p-2 bg-muted rounded text-sm">
                {lastAttackResult}
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setAttackDialogOpen(false)}>Отмена</Button>
            <Button onClick={handlePerformAttack} disabled={!selectedTargetId || isLoading}>
              Атаковать
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Card>
  );
}
