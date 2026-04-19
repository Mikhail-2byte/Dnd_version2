import { useState, useEffect, useRef } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Header } from './Header';
import { ArrowLeft, Save, Scroll, Shield, Heart, Zap } from 'lucide-react';
import { charactersAPI, gameDataAPI } from '../services/api';
import ClassTemplateSelector from './ClassTemplateSelector';
import type { CharacterCreate, CharacterTemplate, RaceData, BackgroundData } from '../types/character';

const characterSchema = z.object({
  name: z.string().min(1, 'Имя обязательно'),
  race: z.string().min(1, 'Раса обязательна'),
  class: z.string().min(1, 'Класс обязателен'),
  level: z.number().min(1).max(20).default(1),
  strength: z.number().min(1).max(30).default(10),
  dexterity: z.number().min(1).max(30).default(10),
  constitution: z.number().min(1).max(30).default(10),
  intelligence: z.number().min(1).max(30).default(10),
  wisdom: z.number().min(1).max(30).default(10),
  charisma: z.number().min(1).max(30).default(10),
  character_history: z.string().optional(),
  equipment_and_features: z.string().optional(),
});

type FormValues = z.infer<typeof characterSchema>;

// Hit dice for HP preview
const HIT_DICE: Record<string, number> = {
  'Варвар': 12, 'Воин': 10, 'Паладин': 10, 'Следопыт': 10,
  'Бард': 8, 'Жрец': 8, 'Друид': 8, 'Монах': 8, 'Плут': 8, 'Колдун': 8,
  'Чародей': 6, 'Маг': 6,
};

// AC preview per class
const BASE_AC_TYPE: Record<string, 'unarmored' | 'leather' | 'chainmail' | 'unarmored_con'> = {
  'Варвар': 'unarmored_con',
  'Маг': 'unarmored', 'Чародей': 'unarmored', 'Колдун': 'unarmored',
  'Плут': 'leather', 'Бард': 'leather', 'Следопыт': 'leather', 'Монах': 'leather', 'Друид': 'leather',
  'Воин': 'chainmail', 'Паладин': 'chainmail', 'Жрец': 'chainmail',
};

function mod(score: number) { return Math.floor((score - 10) / 2); }
function modStr(score: number) { const m = mod(score); return m >= 0 ? `+${m}` : `${m}`; }

function previewHP(charClass: string, level: number, con: number): number {
  const hd = HIT_DICE[charClass] ?? 8;
  const conMod = mod(con);
  return Math.max(1, hd + conMod + (level - 1) * (Math.floor(hd / 2) + 1 + conMod));
}

function previewAC(charClass: string, dex: number, con: number): number {
  const type = BASE_AC_TYPE[charClass] ?? 'leather';
  if (type === 'unarmored_con') return 10 + mod(dex) + mod(con);
  if (type === 'unarmored') return 10 + mod(dex);
  if (type === 'leather') return 11 + mod(dex);
  return 16; // chainmail
}

interface Props {
  onSubmit: (data: CharacterCreate) => Promise<void>;
  onCancel?: () => void;
}

export default function CharacterCreation({ onSubmit, onCancel }: Props) {
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(characterSchema),
    defaultValues: { level: 1, strength: 10, dexterity: 10, constitution: 10, intelligence: 10, wisdom: 10, charisma: 10 },
  });

  const [templates, setTemplates] = useState<Record<string, CharacterTemplate>>({});
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const [generationMethod, setGenerationMethod] = useState('standard_array');
  const [isGenerating, setIsGenerating] = useState(false);

  // Race / background from DB
  const [races, setRaces] = useState<RaceData[]>([]);
  const [backgrounds, setBackgrounds] = useState<BackgroundData[]>([]);
  const [selectedRaceSlug, setSelectedRaceSlug] = useState<string>('');
  const [selectedBgSlug, setSelectedBgSlug] = useState<string>('');
  // Base stats before racial bonuses
  const baseStats = useRef<Record<string, number>>({ strength: 10, dexterity: 10, constitution: 10, intelligence: 10, wisdom: 10, charisma: 10 });

  const w = watch();

  useEffect(() => {
    const load = async () => {
      try {
        const [t, r, bg] = await Promise.all([
          charactersAPI.getTemplates(),
          gameDataAPI.getRaces(),
          gameDataAPI.getBackgrounds(),
        ]);
        setTemplates(t);
        setRaces(r);
        setBackgrounds(bg);
      } catch (e) {
        console.error('Failed to load game data', e);
      }
    };
    load();
  }, []);

  const applyRaceBonuses = (raceSlug: string) => {
    const race = races.find(r => r.slug === raceSlug);
    const bonuses = race?.ability_bonuses ?? {};
    const base = baseStats.current;
    setValue('strength', (base.strength ?? 10) + (bonuses['str'] ?? 0));
    setValue('dexterity', (base.dexterity ?? 10) + (bonuses['dex'] ?? 0));
    setValue('constitution', (base.constitution ?? 10) + (bonuses['con'] ?? 0));
    setValue('intelligence', (base.intelligence ?? 10) + (bonuses['int'] ?? 0));
    setValue('wisdom', (base.wisdom ?? 10) + (bonuses['wis'] ?? 0));
    setValue('charisma', (base.charisma ?? 10) + (bonuses['cha'] ?? 0));
    if (race) setValue('race', race.name);
  };

  const handleRaceChange = (slug: string) => {
    // Save current stats as base (without bonuses from previous race)
    const prev = races.find(r => r.slug === selectedRaceSlug);
    const prevBonuses = prev?.ability_bonuses ?? {};
    const statKeys = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma'] as const;
    const bonusKeys = ['str', 'dex', 'con', 'int', 'wis', 'cha'];
    statKeys.forEach((k, i) => {
      const cur = (w[k] as number) ?? 10;
      baseStats.current[k] = cur - (prevBonuses[bonusKeys[i]] ?? 0);
    });

    setSelectedRaceSlug(slug);
    if (slug) {
      applyRaceBonuses(slug);
    } else {
      // No race: reset to base
      statKeys.forEach(k => setValue(k, baseStats.current[k] ?? 10));
      setValue('race', '');
    }
  };

  const handleStatChange = (key: string, value: number) => {
    const bonusKeys: Record<string, string> = { strength: 'str', dexterity: 'dex', constitution: 'con', intelligence: 'int', wisdom: 'wis', charisma: 'cha' };
    const race = races.find(r => r.slug === selectedRaceSlug);
    const bonus = race?.ability_bonuses?.[bonusKeys[key]] ?? 0;
    baseStats.current[key] = value - bonus;
  };

  const handleTemplateSelect = (templateKey: string) => {
    setSelectedTemplate(templateKey);
    const template = templates[templateKey];
    if (!template) return;
    setValue('class', template.class);
    const stats = template.default_stats;
    const statKeys = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma'] as const;
    statKeys.forEach(k => {
      baseStats.current[k] = stats[k];
    });
    applyRaceBonuses(selectedRaceSlug); // re-apply current race bonuses on top of new base
    setValue('equipment_and_features', template.starting_equipment.join(', '));
    if (template.suggested_names?.length && !w.name) {
      setValue('name', template.suggested_names[0]);
    }
  };

  const handleGenerateAbilities = async () => {
    setIsGenerating(true);
    try {
      const result = await charactersAPI.generateAbilities(generationMethod, selectedTemplate || undefined);
      const statKeys = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma'] as const;
      statKeys.forEach(k => { baseStats.current[k] = result[k]; });
      applyRaceBonuses(selectedRaceSlug);
    } catch (e) {
      console.error('Failed to generate abilities', e);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleFormSubmit = async (values: FormValues) => {
    const payload: CharacterCreate = {
      ...values,
      race_slug: selectedRaceSlug || undefined,
      background_slug: selectedBgSlug || undefined,
    };
    await onSubmit(payload);
  };

  const selectedRace = races.find(r => r.slug === selectedRaceSlug);
  const selectedBg = backgrounds.find(b => b.slug === selectedBgSlug);
  const hp = previewHP(w.class ?? '', w.level ?? 1, w.constitution ?? 10);
  const ac = previewAC(w.class ?? '', w.dexterity ?? 10, w.constitution ?? 10);

  const statFields = [
    { key: 'strength' as const, label: 'Сила' },
    { key: 'dexterity' as const, label: 'Ловкость' },
    { key: 'constitution' as const, label: 'Телосложение' },
    { key: 'intelligence' as const, label: 'Интеллект' },
    { key: 'wisdom' as const, label: 'Мудрость' },
    { key: 'charisma' as const, label: 'Харизма' },
  ];

  return (
    <div className="min-h-screen flex flex-col parchment-bg">
      <Header />

      <main className="flex-1 p-4 md:p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8 text-center">
            <div className="inline-block relative">
              <div className="absolute inset-0 bg-gradient-to-r from-primary/20 via-transparent to-primary/20 blur-xl" />
              <h1 className="relative font-serif text-4xl md:text-5xl text-foreground tracking-wide px-8 py-4 border-t-4 border-b-4 border-primary bg-card/80">
                Создание персонажа
              </h1>
            </div>
            <div className="mt-2 flex items-center justify-center gap-2 text-primary">
              <div className="h-px w-16 bg-gradient-to-r from-transparent to-primary" />
              <Scroll className="w-5 h-5" />
              <div className="h-px w-16 bg-gradient-to-l from-transparent to-primary" />
            </div>
          </div>

          {Object.keys(templates).length > 0 && (
            <Card className="bg-card border-4 border-primary shadow-2xl p-6 mb-6">
              <ClassTemplateSelector
                templates={templates}
                selectedTemplate={selectedTemplate}
                onSelect={handleTemplateSelect}
              />
            </Card>
          )}

          <form onSubmit={handleSubmit(handleFormSubmit)}>
            <div className="grid lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <Card className="bg-card border-4 border-primary shadow-2xl p-6 relative overflow-hidden">
                  <div className="absolute top-0 left-0 w-16 h-16 border-t-4 border-l-4 border-accent opacity-50" />
                  <div className="absolute top-0 right-0 w-16 h-16 border-t-4 border-r-4 border-accent opacity-50" />
                  <div className="absolute bottom-0 left-0 w-16 h-16 border-b-4 border-l-4 border-accent opacity-50" />
                  <div className="absolute bottom-0 right-0 w-16 h-16 border-b-4 border-r-4 border-accent opacity-50" />

                  {/* Basic info */}
                  <div className="bg-muted border-2 border-primary rounded p-4 mb-6 shadow-inner">
                    <div className="grid md:grid-cols-2 gap-4 mb-4">
                      <div>
                        <Label htmlFor="name" className="text-sm font-bold text-foreground uppercase tracking-wider mb-2 block">Имя персонажа</Label>
                        <Input id="name" {...register('name')} className="bg-card border-2 border-primary font-serif text-lg" placeholder="Введите имя героя" />
                        {errors.name && <p className="text-sm text-destructive mt-1">{errors.name.message}</p>}
                      </div>
                      <div>
                        <Label htmlFor="level" className="text-sm font-bold text-foreground uppercase tracking-wider mb-2 block">Уровень</Label>
                        <Input id="level" type="number" {...register('level', { valueAsNumber: true })} className="bg-card border-2 border-primary font-serif text-center text-xl font-bold" min="1" max="20" />
                      </div>
                    </div>

                    {/* Race dropdown */}
                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <Label className="text-sm font-bold text-foreground uppercase tracking-wider mb-2 block">Раса</Label>
                        {races.length > 0 ? (
                          <select
                            value={selectedRaceSlug}
                            onChange={e => handleRaceChange(e.target.value)}
                            className="w-full bg-card border-2 border-primary rounded px-3 py-2 font-serif text-foreground"
                          >
                            <option value="">— Выберите расу —</option>
                            {races.map(r => (
                              <option key={r.slug} value={r.slug}>{r.name}</option>
                            ))}
                          </select>
                        ) : (
                          <Input
                            className="bg-card border-2 border-primary font-serif"
                            placeholder="Человек, эльф..."
                            onChange={e => setValue('race', e.target.value)}
                          />
                        )}
                        {errors.race && <p className="text-sm text-destructive mt-1">{errors.race.message}</p>}
                        {selectedRace && (
                          <p className="text-xs text-muted-foreground mt-1">
                            Скорость {selectedRace.speed} фт{selectedRace.darkvision > 0 ? ` · Тёмное зрение ${selectedRace.darkvision} фт` : ''}
                            {selectedRace.ability_bonuses && Object.keys(selectedRace.ability_bonuses).length > 0 && (
                              <> · Бонусы: {Object.entries(selectedRace.ability_bonuses).map(([k, v]) => `${k.toUpperCase()} +${v}`).join(', ')}</>
                            )}
                          </p>
                        )}
                      </div>

                      {/* Background dropdown */}
                      <div>
                        <Label className="text-sm font-bold text-foreground uppercase tracking-wider mb-2 block">Предыстория</Label>
                        {backgrounds.length > 0 ? (
                          <select
                            value={selectedBgSlug}
                            onChange={e => setSelectedBgSlug(e.target.value)}
                            className="w-full bg-card border-2 border-primary rounded px-3 py-2 font-serif text-foreground"
                          >
                            <option value="">— Выберите предысторию —</option>
                            {backgrounds.map(b => (
                              <option key={b.slug} value={b.slug}>{b.name}</option>
                            ))}
                          </select>
                        ) : null}
                        {selectedBg?.skill_proficiencies && selectedBg.skill_proficiencies.length > 0 && (
                          <p className="text-xs text-muted-foreground mt-1">
                            Навыки: {selectedBg.skill_proficiencies.join(', ')}
                          </p>
                        )}
                        {selectedBg?.feature_name && (
                          <p className="text-xs text-accent mt-1">Черта: {selectedBg.feature_name}</p>
                        )}
                      </div>
                    </div>

                    {/* Hidden race field for form validation */}
                    <input type="hidden" {...register('race')} />
                    {/* Class hidden (set by template selector) */}
                    <input type="hidden" {...register('class')} />
                    {errors.class && <p className="text-sm text-destructive mt-1">{errors.class.message}</p>}
                  </div>

                  {/* Ability scores */}
                  <div className="mb-6">
                    <div className="flex items-center justify-between mb-4 pb-2 border-b-2 border-primary">
                      <h3 className="text-lg font-bold text-foreground uppercase tracking-wider flex items-center gap-2">
                        <span className="text-accent">⚔</span> Характеристики
                      </h3>
                      <div className="flex items-center gap-2">
                        <select
                          value={generationMethod}
                          onChange={e => setGenerationMethod(e.target.value)}
                          className="bg-card border-2 border-primary rounded px-2 py-1 text-sm"
                          disabled={isGenerating}
                        >
                          <option value="standard_array">Стандартный массив</option>
                          <option value="point_buy">Point Buy</option>
                          <option value="random">Случайно (4d6)</option>
                        </select>
                        <Button type="button" onClick={handleGenerateAbilities} disabled={isGenerating} variant="outline" size="sm" className="border-2 border-primary">
                          {isGenerating ? 'Генерация...' : 'Автогенерация'}
                        </Button>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                      {statFields.map((stat) => {
                        const val = (w[stat.key] as number) ?? 10;
                        const raceBonusKey: Record<string, string> = { strength: 'str', dexterity: 'dex', constitution: 'con', intelligence: 'int', wisdom: 'wis', charisma: 'cha' };
                        const bonus = selectedRace?.ability_bonuses?.[raceBonusKey[stat.key]] ?? 0;
                        return (
                          <div key={stat.key} className="bg-muted border-2 border-primary rounded p-3 shadow-md">
                            <Label htmlFor={stat.key} className="text-xs font-bold text-foreground uppercase tracking-wide mb-2 block text-center">
                              {stat.label}
                              {bonus > 0 && <span className="text-green-500 ml-1">(+{bonus})</span>}
                            </Label>
                            <div className="flex items-center justify-center gap-2">
                              <Input
                                id={stat.key}
                                type="number"
                                {...register(stat.key, {
                                  valueAsNumber: true,
                                  onChange: e => handleStatChange(stat.key, Number(e.target.value)),
                                })}
                                className="w-16 h-16 text-center font-bold text-2xl border-2 border-primary bg-card rounded-full"
                                min="1"
                                max="30"
                              />
                              <div className="w-12 h-12 rounded-full bg-primary flex items-center justify-center text-accent font-bold text-lg shadow-md">
                                {modStr(val)}
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Narrative */}
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="character_history" className="text-sm font-bold text-foreground uppercase tracking-wider mb-2 block">
                        <span className="text-accent mr-2">📜</span>История персонажа
                      </Label>
                      <Textarea id="character_history" {...register('character_history')} className="bg-card border-2 border-primary min-h-32 font-serif text-foreground" placeholder="Расскажите историю вашего героя..." />
                    </div>
                    <div>
                      <Label htmlFor="equipment_and_features" className="text-sm font-bold text-foreground uppercase tracking-wider mb-2 block">
                        <span className="text-accent mr-2">⚔️</span>Снаряжение и особенности
                      </Label>
                      <Textarea id="equipment_and_features" {...register('equipment_and_features')} className="bg-card border-2 border-primary min-h-24 font-serif text-foreground" placeholder="Оружие, доспехи, особые предметы..." />
                    </div>
                  </div>
                </Card>

                <div className="flex gap-4 mt-6">
                  {onCancel && (
                    <Button type="button" onClick={onCancel} variant="outline" className="flex-1 border-2 border-primary text-foreground hover:bg-primary hover:text-primary-foreground font-bold py-6 text-lg bg-card">
                      <ArrowLeft className="w-5 h-5 mr-2" />Вернуться в лобби
                    </Button>
                  )}
                  <Button type="submit" disabled={isSubmitting} className="flex-1 bg-primary hover:bg-primary/90 text-primary-foreground font-bold py-6 text-lg shadow-lg border-2 border-primary/80">
                    <Save className="w-5 h-5 mr-2" />
                    {isSubmitting ? 'Сохранение...' : 'Сохранить персонажа'}
                  </Button>
                </div>
              </div>

              {/* Preview panel */}
              <div className="lg:col-span-1">
                <div className="sticky top-8">
                  <h3 className="text-xl font-bold text-foreground mb-4 uppercase tracking-wide text-center">Предпросмотр</h3>
                  <Card className="bg-card border-4 border-primary shadow-2xl p-6 relative">
                    <div className="absolute top-0 left-0 w-12 h-12 border-t-2 border-l-2 border-accent" />
                    <div className="absolute top-0 right-0 w-12 h-12 border-t-2 border-r-2 border-accent" />
                    <div className="absolute bottom-0 left-0 w-12 h-12 border-b-2 border-l-2 border-accent" />
                    <div className="absolute bottom-0 right-0 w-12 h-12 border-b-2 border-r-2 border-accent" />

                    <div className="text-center space-y-4">
                      <div className="w-32 h-32 mx-auto bg-gradient-to-br from-primary to-primary/80 rounded-full flex items-center justify-center border-4 border-accent shadow-xl">
                        <span className="text-6xl text-primary-foreground font-bold font-serif">
                          {w.name?.[0]?.toUpperCase() || '?'}
                        </span>
                      </div>

                      <div className="border-t-2 border-b-2 border-primary py-3">
                        <h4 className="font-serif text-2xl text-foreground font-bold">{w.name || 'Имя героя'}</h4>
                        <p className="text-primary font-semibold mt-1">
                          {w.class || 'Класс'} · Ур. {w.level || 1}
                        </p>
                        <p className="text-sm text-primary italic">
                          {selectedRace ? selectedRace.name : (w.race || 'Раса')}
                          {selectedBg ? ` · ${selectedBg.name}` : ''}
                        </p>
                      </div>

                      {/* Combat stats preview */}
                      <div className="grid grid-cols-3 gap-2 pt-1">
                        <div className="bg-muted border-2 border-red-500/50 rounded p-2 text-center">
                          <Heart className="w-4 h-4 mx-auto mb-1 text-red-500" />
                          <div className="text-xs text-muted-foreground">HP</div>
                          <div className="text-xl font-bold text-red-500">{hp}</div>
                        </div>
                        <div className="bg-muted border-2 border-blue-500/50 rounded p-2 text-center">
                          <Shield className="w-4 h-4 mx-auto mb-1 text-blue-500" />
                          <div className="text-xs text-muted-foreground">КБ</div>
                          <div className="text-xl font-bold text-blue-500">{ac}</div>
                        </div>
                        <div className="bg-muted border-2 border-yellow-500/50 rounded p-2 text-center">
                          <Zap className="w-4 h-4 mx-auto mb-1 text-yellow-500" />
                          <div className="text-xs text-muted-foreground">Инит.</div>
                          <div className="text-xl font-bold text-yellow-500">{modStr(w.dexterity ?? 10)}</div>
                        </div>
                      </div>

                      {/* Ability scores */}
                      <div className="grid grid-cols-2 gap-2 pt-1">
                        {statFields.map((stat) => (
                          <div key={stat.key} className="bg-muted border-2 border-primary rounded p-2">
                            <div className="text-xs text-foreground font-bold uppercase">{stat.label}</div>
                            <div className="text-2xl font-bold text-primary">{(w[stat.key] as number) || 10}</div>
                            <div className="text-sm text-accent font-semibold">{modStr((w[stat.key] as number) || 10)}</div>
                          </div>
                        ))}
                      </div>

                      {/* Skill proficiencies from background */}
                      {selectedBg?.skill_proficiencies && selectedBg.skill_proficiencies.length > 0 && (
                        <div className="pt-2 border-t border-primary/40">
                          <p className="text-xs text-muted-foreground font-bold uppercase mb-1">Владение навыками</p>
                          <div className="flex flex-wrap gap-1 justify-center">
                            {selectedBg.skill_proficiencies.map(s => (
                              <span key={s} className="text-xs bg-primary/20 text-primary px-2 py-0.5 rounded">{s}</span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </Card>
                </div>
              </div>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
}
