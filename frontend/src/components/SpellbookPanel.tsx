import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Input } from './ui/input';
import { ScrollArea } from './ui/scroll-area';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { spellbookAPI, gameDataAPI } from '../services/api';
import type { SpellbookEntry, SpellSlotInfo, SpellData } from '../types/character';
import { BookOpen, Plus, Trash2, Eye, EyeOff, Circle, Zap } from 'lucide-react';

interface SpellbookPanelProps {
  characterId: string;
  characterClass: string;
  combatId?: string | null;
}

const SCHOOL_NAMES: Record<string, string> = {
  evocation: 'Воплощение', conjuration: 'Вызов', illusion: 'Иллюзия',
  necromancy: 'Некромантия', abjuration: 'Ограждение', enchantment: 'Очарование',
  transmutation: 'Преобразование', divination: 'Прорицание',
};

export default function SpellbookPanel({ characterId, characterClass, combatId }: SpellbookPanelProps) {
  const [spells, setSpells] = useState<SpellbookEntry[]>([]);
  const [slots, setSlots] = useState<SpellSlotInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [addOpen, setAddOpen] = useState(false);
  const [catalog, setCatalog] = useState<SpellData[]>([]);
  const [search, setSearch] = useState('');
  const [levelFilter, setLevelFilter] = useState<string>('all');
  const [schoolFilter, setSchoolFilter] = useState<string>('all');
  const [expandedSpell, setExpandedSpell] = useState<string | null>(null);
  const [castingSpell, setCastingSpell] = useState<SpellbookEntry | null>(null);
  const [concentrationSpell, setConcentrationSpell] = useState<string | null>(null);

  useEffect(() => {
    loadSpellbook();
  }, [characterId]);

  async function loadSpellbook() {
    setLoading(true);
    try {
      const data = await spellbookAPI.getSpellbook(characterId);
      setSpells(data.spells);
      setSlots(data.slots);
    } catch (e) {
      console.error('Failed to load spellbook', e);
    } finally {
      setLoading(false);
    }
  }

  async function openAddDialog() {
    setAddOpen(true);
    try {
      const data = await gameDataAPI.getSpells({ class: characterClass.toLowerCase() });
      setCatalog(data);
    } catch {
      const data = await gameDataAPI.getSpells();
      setCatalog(data);
    }
  }

  async function handleAdd(spellId: string) {
    try {
      await spellbookAPI.addSpell(characterId, spellId);
      await loadSpellbook();
      setAddOpen(false);
    } catch (e: any) {
      if (e?.response?.status !== 409) console.error(e);
    }
  }

  async function handleRemove(spellId: string) {
    try {
      await spellbookAPI.removeSpell(characterId, spellId);
      setSpells(prev => prev.filter(s => s.spell_id !== spellId));
    } catch (e) {
      console.error(e);
    }
  }

  async function handlePrepare(spell: SpellbookEntry) {
    if (spell.level === 0) return; // cantrips always prepared
    try {
      const res = await spellbookAPI.prepareSpell(characterId, spell.spell_id, !spell.is_prepared);
      setSpells(prev => prev.map(s => s.spell_id === spell.spell_id ? { ...s, is_prepared: res.is_prepared } : s));
    } catch (e) {
      console.error(e);
    }
  }

  async function handleUseSlot(spellLevel: number) {
    try {
      const res = await spellbookAPI.useSlot(characterId, spellLevel);
      setSlots(prev => prev.map(s =>
        s.spell_level === res.spell_level
          ? { ...s, used_slots: res.used, available: res.max - res.used }
          : s
      ));
    } catch (e: any) {
      console.error(e?.response?.data?.detail ?? e);
    }
  }

  async function handleCastInCombat(spell: SpellbookEntry, slotLevel?: number) {
    const level = slotLevel ?? (spell.level ?? 0);
    if (spell.concentration && concentrationSpell && concentrationSpell !== spell.name) {
      if (!confirm(`Прервать концентрацию на "${concentrationSpell}" и наложить "${spell.name}"?`)) return;
    }
    if (level > 0) {
      await handleUseSlot(level);
    }
    if (spell.concentration) {
      setConcentrationSpell(spell.name ?? null);
    }
    setCastingSpell(null);
  }

  const knownSpellIds = new Set(spells.map(s => s.spell_id));
  const filteredCatalog = catalog.filter(s => {
    const matchSearch = s.name.toLowerCase().includes(search.toLowerCase());
    const matchLevel = levelFilter === 'all' || s.level === parseInt(levelFilter);
    const notKnown = !knownSpellIds.has(s.id);
    return matchSearch && matchLevel && notKnown;
  });

  const filteredSpells = schoolFilter === 'all'
    ? spells
    : spells.filter(s => s.school === schoolFilter);

  const cantrips = filteredSpells.filter(s => s.level === 0);
  const spellsByLevel = filteredSpells.filter(s => (s.level ?? 0) > 0).reduce((acc, s) => {
    const lvl = s.level ?? 1;
    if (!acc[lvl]) acc[lvl] = [];
    acc[lvl].push(s);
    return acc;
  }, {} as Record<number, SpellbookEntry[]>);

  function slotDots(slot: SpellSlotInfo) {
    return Array.from({ length: slot.max_slots }, (_, i) => (
      <Circle
        key={i}
        className={`h-3 w-3 ${i < slot.used_slots ? 'fill-muted-foreground text-muted-foreground' : 'fill-primary text-primary'}`}
      />
    ));
  }

  function renderSpell(spell: SpellbookEntry) {
    const isExpanded = expandedSpell === spell.id;
    const isConcentrating = concentrationSpell === spell.name;
    const canCast = combatId && (spell.level === 0 || spell.is_prepared);

    return (
      <div key={spell.id} className={`border rounded p-2 space-y-1 ${isConcentrating ? 'border-purple-500/60 bg-purple-500/5' : 'border-border'}`}>
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2 min-w-0">
            <span className="font-medium text-sm truncate">{spell.name}</span>
            {spell.concentration && <Badge variant={isConcentrating ? 'default' : 'outline'} className="text-xs px-1" title="Концентрация">К</Badge>}
            {spell.ritual && <Badge variant="outline" className="text-xs px-1">Р</Badge>}
            {spell.school && <span className="text-xs text-muted-foreground">{SCHOOL_NAMES[spell.school] ?? spell.school}</span>}
          </div>
          <div className="flex items-center gap-1 shrink-0">
            {canCast && (
              <Button
                variant="outline"
                size="icon"
                className="h-6 w-6 text-purple-400 border-purple-500/50 hover:bg-purple-500/10"
                title="Применить в бою"
                onClick={() => {
                  if ((spell.level ?? 0) > 0) {
                    setCastingSpell(spell);
                  } else {
                    handleCastInCombat(spell, 0);
                  }
                }}
              >
                <Zap className="h-3 w-3" />
              </Button>
            )}
            {(spell.level ?? 0) > 0 && (
              <Button
                variant={spell.is_prepared ? 'default' : 'ghost'}
                size="icon"
                className="h-6 w-6"
                title={spell.is_prepared ? 'Отложить' : 'Подготовить'}
                onClick={() => handlePrepare(spell)}
              >
                {spell.is_prepared ? <Eye className="h-3 w-3" /> : <EyeOff className="h-3 w-3" />}
              </Button>
            )}
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6 text-muted-foreground"
              onClick={() => setExpandedSpell(isExpanded ? null : spell.id)}
            >
              <BookOpen className="h-3 w-3" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6 text-destructive"
              onClick={() => handleRemove(spell.spell_id)}
            >
              <Trash2 className="h-3 w-3" />
            </Button>
          </div>
        </div>
        {isExpanded && spell.description && (
          <p className="text-xs text-muted-foreground leading-relaxed">{spell.description}</p>
        )}
        {isExpanded && (
          <div className="flex gap-3 text-xs text-muted-foreground">
            {spell.casting_time && <span>Время: {spell.casting_time}</span>}
            {spell.spell_range && <span>Дист.: {spell.spell_range}</span>}
            {spell.duration && <span>Длит.: {spell.duration}</span>}
          </div>
        )}
      </div>
    );
  }

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <CardTitle className="text-base flex items-center gap-2">
            <BookOpen className="h-4 w-4" /> Спеллбук
          </CardTitle>
          <div className="flex items-center gap-2">
            <Select value={schoolFilter} onValueChange={setSchoolFilter}>
              <SelectTrigger className="w-32 h-7 text-xs">
                <SelectValue placeholder="Школа" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Все школы</SelectItem>
                {Object.entries(SCHOOL_NAMES).map(([key, label]) => (
                  <SelectItem key={key} value={key}>{label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button size="sm" variant="outline" onClick={openAddDialog}>
              <Plus className="h-3 w-3 mr-1" /> Добавить
            </Button>
          </div>
        </div>
        {concentrationSpell && (
          <div className="flex items-center justify-between mt-1 px-2 py-1 rounded bg-purple-500/10 border border-purple-500/30">
            <span className="text-xs text-purple-400">
              <Zap className="h-3 w-3 inline mr-1" />Концентрация: {concentrationSpell}
            </span>
            <Button
              variant="ghost"
              size="icon"
              className="h-5 w-5 text-purple-400 hover:text-destructive"
              onClick={() => setConcentrationSpell(null)}
            >
              <Trash2 className="h-3 w-3" />
            </Button>
          </div>
        )}
      </CardHeader>

      <CardContent className="flex-1 overflow-hidden p-3 space-y-3">
        {/* Slot tracker */}
        {slots.length > 0 && (
          <div className="space-y-1">
            <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Ячейки заклинаний</p>
            <div className="grid grid-cols-3 gap-1">
              {slots.map(s => (
                <div
                  key={s.spell_level}
                  className="flex items-center justify-between px-2 py-1 rounded border border-border cursor-pointer hover:bg-muted/30"
                  onClick={() => s.available > 0 && handleUseSlot(s.spell_level)}
                  title={`Уровень ${s.spell_level}: ${s.available}/${s.max_slots} доступно`}
                >
                  <span className="text-xs font-medium">{s.spell_level} ур.</span>
                  <div className="flex gap-0.5">{slotDots(s)}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        <ScrollArea className="flex-1 h-64">
          {loading ? (
            <p className="text-muted-foreground text-sm text-center py-4">Загрузка...</p>
          ) : spells.length === 0 ? (
            <p className="text-muted-foreground text-sm text-center py-4">Заклинаний нет</p>
          ) : (
            <div className="space-y-3 pr-2">
              {cantrips.length > 0 && (
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-1">Заговоры</p>
                  <div className="space-y-1">{cantrips.map(renderSpell)}</div>
                </div>
              )}
              {Object.entries(spellsByLevel).sort(([a], [b]) => +a - +b).map(([lvl, group]) => (
                <div key={lvl}>
                  <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-1">
                    {lvl} уровень
                  </p>
                  <div className="space-y-1">{group.map(renderSpell)}</div>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </CardContent>

      {/* Диалог выбора ячейки для кастинга */}
      <Dialog open={!!castingSpell} onOpenChange={open => { if (!open) setCastingSpell(null); }}>
        <DialogContent className="max-w-xs">
          <DialogHeader>
            <DialogTitle>Применить: {castingSpell?.name}</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground mb-3">Выберите уровень ячейки заклинания:</p>
          <div className="space-y-2">
            {slots
              .filter(s => s.spell_level >= (castingSpell?.level ?? 1) && s.available > 0)
              .map(s => (
                <Button
                  key={s.spell_level}
                  variant="outline"
                  className="w-full justify-between"
                  onClick={() => castingSpell && handleCastInCombat(castingSpell, s.spell_level)}
                >
                  <span>{s.spell_level} уровень</span>
                  <span className="text-xs text-muted-foreground">{s.available}/{s.max_slots} доступно</span>
                </Button>
              ))
            }
            {slots.filter(s => s.spell_level >= (castingSpell?.level ?? 1) && s.available > 0).length === 0 && (
              <p className="text-sm text-muted-foreground text-center py-2">Нет доступных ячеек нужного уровня</p>
            )}
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={addOpen} onOpenChange={setAddOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Добавить заклинание</DialogTitle>
          </DialogHeader>
          <div className="flex gap-2 mb-3">
            <Input
              placeholder="Поиск..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="flex-1"
            />
            <Select value={levelFilter} onValueChange={setLevelFilter}>
              <SelectTrigger className="w-28">
                <SelectValue placeholder="Уровень" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Все</SelectItem>
                {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9].map(l => (
                  <SelectItem key={l} value={String(l)}>{l === 0 ? 'Заговоры' : `${l} ур.`}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <ScrollArea className="h-72">
            {filteredCatalog.map(s => (
              <div
                key={s.id}
                className="flex items-center justify-between p-2 hover:bg-muted/30 rounded cursor-pointer"
                onClick={() => handleAdd(s.id)}
              >
                <div className="min-w-0">
                  <p className="font-medium text-sm truncate">{s.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {s.level === 0 ? 'Заговор' : `${s.level} ур.`}
                    {s.school ? ` · ${SCHOOL_NAMES[s.school] ?? s.school}` : ''}
                    {s.concentration ? ' · Концентрация' : ''}
                  </p>
                </div>
                <Plus className="h-4 w-4 text-primary shrink-0 ml-2" />
              </div>
            ))}
            {filteredCatalog.length === 0 && (
              <p className="text-muted-foreground text-sm text-center py-4">Ничего не найдено</p>
            )}
          </ScrollArea>
        </DialogContent>
      </Dialog>
    </Card>
  );
}
