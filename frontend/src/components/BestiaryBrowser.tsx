import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { ScrollArea } from './ui/scroll-area';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from './ui/dialog';
import { gameDataAPI, combatAPI } from '../services/api';
import type { MonsterListItem, MonsterData } from '../types/character';
import { Skull, Search, ChevronRight, Plus, X } from 'lucide-react';

interface BestiaryBrowserProps {
  gameId: string;
  combatId: string | null;
}

function crLabel(cr?: number) {
  if (cr === undefined || cr === null) return '?';
  if (cr === 0.125) return '1/8';
  if (cr === 0.25) return '1/4';
  if (cr === 0.5) return '1/2';
  return String(cr);
}

function abilityMod(score: number) {
  const m = Math.floor((score - 10) / 2);
  return m >= 0 ? `+${m}` : String(m);
}

export default function BestiaryBrowser({ gameId, combatId }: BestiaryBrowserProps) {
  const [monsters, setMonsters] = useState<MonsterListItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [selected, setSelected] = useState<MonsterData | null>(null);
  const [detailOpen, setDetailOpen] = useState(false);
  const [spawning, setSpawning] = useState(false);

  useEffect(() => {
    loadMonsters();
  }, []);

  async function loadMonsters() {
    setLoading(true);
    try {
      const data = await gameDataAPI.getMonsters();
      setMonsters(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  async function openDetail(slug: string) {
    try {
      const data = await gameDataAPI.getMonster(slug);
      setSelected(data);
      setDetailOpen(true);
    } catch (e) {
      console.error(e);
    }
  }

  async function handleSpawn() {
    if (!selected || !combatId) return;
    setSpawning(true);
    try {
      await combatAPI.addMonster(gameId, combatId, selected.slug);
      setDetailOpen(false);
    } catch (e: any) {
      console.error(e?.response?.data?.detail ?? e);
    } finally {
      setSpawning(false);
    }
  }

  const filtered = monsters.filter(m =>
    m.name.toLowerCase().includes(search.toLowerCase())
  );

  const ABILITY_NAMES = [
    ['strength', 'СИЛ'], ['dexterity', 'ЛОВ'], ['constitution', 'ТЕЛ'],
    ['intelligence', 'ИНТ'], ['wisdom', 'МДР'], ['charisma', 'ХАР'],
  ] as const;

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-2">
        <CardTitle className="text-base flex items-center gap-2">
          <Skull className="h-4 w-4" /> Бестиарий
        </CardTitle>
      </CardHeader>

      <CardContent className="flex-1 overflow-hidden p-3 space-y-2">
        <div className="relative">
          <Search className="absolute left-2 top-1/2 -translate-y-1/2 h-3 w-3 text-muted-foreground" />
          <Input
            placeholder="Поиск монстра..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="pl-7 h-8 text-sm"
          />
        </div>

        <ScrollArea className="h-full">
          {loading ? (
            <p className="text-muted-foreground text-sm text-center py-4">Загрузка...</p>
          ) : filtered.length === 0 ? (
            <p className="text-muted-foreground text-sm text-center py-4">Ничего не найдено</p>
          ) : (
            <div className="space-y-0.5 pr-2">
              {filtered.map(m => (
                <div
                  key={m.id}
                  className="flex items-center justify-between p-2 hover:bg-muted/30 rounded cursor-pointer group"
                  onClick={() => openDetail(m.slug)}
                >
                  <div className="min-w-0">
                    <p className="font-medium text-sm truncate">{m.name}</p>
                    <p className="text-xs text-muted-foreground">
                      КО {crLabel(m.cr)} · HP {m.hp_average ?? '?'} · КБ {m.armor_class}
                      {m.monster_type ? ` · ${m.monster_type}` : ''}
                    </p>
                  </div>
                  <ChevronRight className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity shrink-0" />
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </CardContent>

      <Dialog open={detailOpen} onOpenChange={setDetailOpen}>
        <DialogContent className="max-w-lg max-h-[80vh] overflow-y-auto">
          {selected && (
            <>
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2">
                  <Skull className="h-4 w-4" /> {selected.name}
                  {selected.name_en && <span className="text-sm font-normal text-muted-foreground">({selected.name_en})</span>}
                </DialogTitle>
              </DialogHeader>

              <div className="space-y-3 text-sm">
                {/* Meta */}
                <div className="flex flex-wrap gap-2">
                  {selected.size && <Badge variant="outline">{selected.size}</Badge>}
                  {selected.monster_type && <Badge variant="outline">{selected.monster_type}</Badge>}
                  {selected.alignment && <span className="text-muted-foreground">{selected.alignment}</span>}
                </div>

                {/* Combat stats */}
                <div className="grid grid-cols-3 gap-2 py-2 border-y border-border">
                  <div className="text-center">
                    <p className="text-xs text-muted-foreground">КБ</p>
                    <p className="font-bold">{selected.armor_class}{selected.armor_type ? ` (${selected.armor_type})` : ''}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-muted-foreground">HP</p>
                    <p className="font-bold">{selected.hp_average ?? '?'} <span className="text-muted-foreground text-xs">({selected.hp_dice})</span></p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-muted-foreground">КО / XP</p>
                    <p className="font-bold">{crLabel(selected.cr)} / {selected.xp_reward ?? 0}</p>
                  </div>
                </div>

                {/* Ability scores */}
                <div className="grid grid-cols-6 gap-1 text-center">
                  {ABILITY_NAMES.map(([key, label]) => (
                    <div key={key} className="bg-muted/30 rounded p-1">
                      <p className="text-xs text-muted-foreground">{label}</p>
                      <p className="font-bold text-sm">{selected[key]}</p>
                      <p className="text-xs text-muted-foreground">{abilityMod(selected[key])}</p>
                    </div>
                  ))}
                </div>

                {/* Resistances */}
                {selected.damage_resistances?.length ? (
                  <p className="text-xs"><span className="font-semibold">Сопротивления:</span> {selected.damage_resistances.join(', ')}</p>
                ) : null}
                {selected.damage_immunities?.length ? (
                  <p className="text-xs"><span className="font-semibold">Иммунитеты:</span> {selected.damage_immunities.join(', ')}</p>
                ) : null}
                {selected.damage_vulnerabilities?.length ? (
                  <p className="text-xs"><span className="font-semibold">Уязвимости:</span> {selected.damage_vulnerabilities.join(', ')}</p>
                ) : null}
                {selected.senses && Object.keys(selected.senses).length > 0 && (
                  <p className="text-xs"><span className="font-semibold">Чувства:</span> {
                    Object.entries(selected.senses).map(([k, v]) => `${k} ${v}`).join(', ')
                  }</p>
                )}
                {selected.languages && (
                  <p className="text-xs"><span className="font-semibold">Языки:</span> {selected.languages}</p>
                )}

                {/* Actions */}
                {selected.all_actions && selected.all_actions.length > 0 && (
                  <div className="space-y-2">
                    <p className="font-semibold border-b border-border pb-1">Действия</p>
                    {selected.all_actions.filter(a => a.action_type === 'action').map(action => (
                      <div key={action.id}>
                        <p className="font-medium text-sm">
                          {action.name}
                          {action.attack_bonus !== undefined && action.attack_bonus !== null
                            ? ` · +${action.attack_bonus} к атаке` : ''}
                          {action.damage_dice ? `, ${action.damage_dice} ${action.damage_type ?? ''}` : ''}
                        </p>
                        {action.description && <p className="text-xs text-muted-foreground">{action.description}</p>}
                      </div>
                    ))}
                    {selected.all_actions.filter(a => a.action_type === 'legendary').length > 0 && (
                      <>
                        <p className="font-semibold border-b border-border pb-1">Легендарные действия</p>
                        {selected.all_actions.filter(a => a.action_type === 'legendary').map(action => (
                          <div key={action.id}>
                            <p className="font-medium text-sm">{action.name}</p>
                            {action.description && <p className="text-xs text-muted-foreground">{action.description}</p>}
                          </div>
                        ))}
                      </>
                    )}
                  </div>
                )}

                {selected.description && (
                  <p className="text-xs text-muted-foreground">{selected.description}</p>
                )}
              </div>

              <DialogFooter>
                <Button variant="outline" onClick={() => setDetailOpen(false)}>
                  <X className="h-4 w-4 mr-1" /> Закрыть
                </Button>
                {combatId && (
                  <Button onClick={handleSpawn} disabled={spawning}>
                    <Plus className="h-4 w-4 mr-1" /> {spawning ? 'Добавляю...' : 'Добавить в бой'}
                  </Button>
                )}
              </DialogFooter>
            </>
          )}
        </DialogContent>
      </Dialog>
    </Card>
  );
}
