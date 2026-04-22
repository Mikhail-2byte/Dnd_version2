import { useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, ArrowRight, Check, Eye, EyeOff, Package, Trash2, Upload, User2 } from 'lucide-react';
import { Header } from '../components/Header';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Label } from '../components/ui/label';
import { Switch } from '../components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from '../components/ui/dialog';
import { useToast } from '../hooks/use-toast';
import { scenariosAPI, gameDataAPI } from '../services/api';
import type { Scenario, ScenarioNPC, ScenarioHiddenItem } from '../types/scenario';
import type { MonsterListItem, WeaponData, ArmorData, ItemData } from '../types/character';

const STEPS = ['Информация', 'Карта', 'НПС', 'Предметы', 'Обзор'];

interface LocalNPC extends Omit<ScenarioNPC, 'id' | 'scenario_id'> {
  localId: string;
}
interface LocalItem extends Omit<ScenarioHiddenItem, 'id' | 'scenario_id'> {
  localId: string;
}

export default function ScenarioBuilder() {
  const { scenarioId } = useParams<{ scenarioId: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const isEdit = !!scenarioId;

  const [step, setStep] = useState(0);
  const [saving, setSaving] = useState(false);

  // Step 1 — Info
  const [name, setName] = useState('');
  const [story, setStory] = useState('');

  // Step 2 — Map
  const [mapUrl, setMapUrl] = useState<string | null>(null);
  const [mapFile, setMapFile] = useState<File | null>(null);
  const [mapPreview, setMapPreview] = useState<string | null>(null);
  const [savedScenarioId, setSavedScenarioId] = useState<string | null>(scenarioId ?? null);

  // Step 3 — NPCs
  const [npcs, setNpcs] = useState<LocalNPC[]>([]);
  const [npcDialog, setNpcDialog] = useState(false);
  const [pendingNpcPos, setPendingNpcPos] = useState<{ x: number; y: number } | null>(null);
  const [npcForm, setNpcForm] = useState<Partial<LocalNPC>>({});
  const [monsters, setMonsters] = useState<MonsterListItem[]>([]);

  // Step 4 — Items
  const [items, setItems] = useState<LocalItem[]>([]);
  const [itemDialog, setItemDialog] = useState(false);
  const [pendingItemPos, setPendingItemPos] = useState<{ x: number; y: number } | null>(null);
  const [itemForm, setItemForm] = useState<Partial<LocalItem>>({});
  const [weapons, setWeapons] = useState<WeaponData[]>([]);
  const [armors, setArmors] = useState<ArmorData[]>([]);
  const [genericItems, setGenericItems] = useState<ItemData[]>([]);

  const mapRef = useRef<HTMLDivElement>(null);
  const apiBase = (import.meta as any).env?.VITE_API_URL ?? '';

  // Load existing scenario for editing
  useEffect(() => {
    if (!scenarioId) return;
    scenariosAPI.get(scenarioId).then((s: Scenario) => {
      setName(s.name);
      setStory(s.story ?? '');
      setMapUrl(s.map_url);
      setMapPreview(s.map_url ? `${apiBase}${s.map_url}` : null);
      setNpcs(s.npcs.map((n) => ({ ...n, localId: n.id })));
      setItems(s.items.map((i) => ({ ...i, localId: i.id })));
    });
  }, [scenarioId]);

  // Load reference data for step 3 & 4
  useEffect(() => {
    if (step === 2) {
      gameDataAPI.getMonsters({ cr_max: 30 }).then(setMonsters).catch(() => {});
    }
    if (step === 3) {
      gameDataAPI.getWeapons().then(setWeapons).catch(() => {});
      gameDataAPI.getArmors().then(setArmors).catch(() => {});
      gameDataAPI.getItems().then(setGenericItems).catch(() => {});
    }
  }, [step]);

  // Save step 1 data and get scenario ID
  const ensureSavedScenario = async (): Promise<string> => {
    if (savedScenarioId) {
      await scenariosAPI.update(savedScenarioId, { name, story: story || undefined });
      return savedScenarioId;
    }
    const s = await scenariosAPI.create({ name, story: story || undefined });
    setSavedScenarioId(s.id);
    return s.id;
  };

  const handleMapFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setMapFile(file);
    setMapPreview(URL.createObjectURL(file));
  };

  const uploadMapIfNeeded = async (sid: string) => {
    if (!mapFile) return;
    const result = await scenariosAPI.uploadMap(sid, mapFile);
    setMapUrl(result.map_url);
    setMapFile(null);
  };

  const handleNext = async () => {
    if (step === 0) {
      if (!name.trim()) {
        toast({ title: 'Введите название сценария', variant: 'destructive' });
        return;
      }
    }
    if (step === 1) {
      try {
        const sid = await ensureSavedScenario();
        await uploadMapIfNeeded(sid);
      } catch {
        toast({ title: 'Ошибка', description: 'Не удалось сохранить данные', variant: 'destructive' });
        return;
      }
    }
    setStep((s) => Math.min(s + 1, STEPS.length - 1));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const sid = savedScenarioId ?? (await scenariosAPI.create({ name, story: story || undefined })).id;
      setSavedScenarioId(sid);
      await scenariosAPI.update(sid, { name, story: story || undefined, map_url: mapUrl ?? undefined });
      await uploadMapIfNeeded(sid);

      // Sync NPCs
      for (const npc of npcs) {
        const payload = {
          name: npc.name, x: npc.x, y: npc.y, image_url: npc.image_url,
          is_hidden: npc.is_hidden, monster_slug: npc.monster_slug,
          loot: npc.loot, notes: npc.notes,
        };
        if (npc.localId.startsWith('local-')) {
          await scenariosAPI.addNpc(sid, payload as any);
        } else {
          await scenariosAPI.updateNpc(sid, npc.localId, payload as any);
        }
      }

      // Sync Items
      for (const item of items) {
        const payload = {
          name: item.name, x: item.x, y: item.y, image_url: item.image_url,
          item_type: item.item_type, item_id: item.item_id,
          quantity: item.quantity, notes: item.notes,
        };
        if (item.localId.startsWith('local-')) {
          await scenariosAPI.addItem(sid, payload as any);
        } else {
          await scenariosAPI.updateItem(sid, item.localId, payload as any);
        }
      }

      toast({ title: 'Сценарий сохранён!' });
      navigate('/scenarios');
    } catch {
      toast({ title: 'Ошибка сохранения', variant: 'destructive' });
    } finally {
      setSaving(false);
    }
  };

  const getClickPercent = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = mapRef.current?.getBoundingClientRect();
    if (!rect) return null;
    return {
      x: Math.round(((e.clientX - rect.left) / rect.width) * 100),
      y: Math.round(((e.clientY - rect.top) / rect.height) * 100),
    };
  };

  const handleMapClickNpc = (e: React.MouseEvent<HTMLDivElement>) => {
    const pos = getClickPercent(e);
    if (!pos) return;
    setPendingNpcPos(pos);
    setNpcForm({ is_hidden: true, x: pos.x, y: pos.y });
    setNpcDialog(true);
  };

  const handleMapClickItem = (e: React.MouseEvent<HTMLDivElement>) => {
    const pos = getClickPercent(e);
    if (!pos) return;
    setPendingItemPos(pos);
    setItemForm({ x: pos.x, y: pos.y, item_type: 'item', quantity: 1 });
    setItemDialog(true);
  };

  const addNpc = () => {
    if (!npcForm.name?.trim() || pendingNpcPos === null) return;
    setNpcs((prev) => [...prev, {
      localId: `local-${Date.now()}`,
      name: npcForm.name!,
      x: pendingNpcPos.x,
      y: pendingNpcPos.y,
      image_url: null,
      is_hidden: npcForm.is_hidden ?? true,
      monster_slug: npcForm.monster_slug ?? null,
      loot: [],
      notes: null,
    }]);
    setNpcDialog(false);
    setNpcForm({});
  };

  const addItem = () => {
    if (!itemForm.name?.trim() || !itemForm.item_type || pendingItemPos === null) return;
    setItems((prev) => [...prev, {
      localId: `local-${Date.now()}`,
      name: itemForm.name!,
      x: pendingItemPos.x,
      y: pendingItemPos.y,
      image_url: null,
      item_type: itemForm.item_type as 'weapon' | 'armor' | 'item',
      item_id: itemForm.item_id ?? null,
      quantity: itemForm.quantity ?? 1,
      notes: null,
    }]);
    setItemDialog(false);
    setItemForm({});
  };

  return (
    <div className="min-h-screen flex flex-col relative overflow-hidden"
      style={{
        backgroundImage: 'url(/assets/backgrounds/background2.png)',
        backgroundSize: 'cover', backgroundPosition: 'center',
      }}>
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" />
      <div className="relative z-10 flex flex-col flex-1">
        <Header />
        <main className="flex-1 p-6 overflow-y-auto">
          <div className="max-w-3xl mx-auto">
            <div className="flex items-center gap-3 mb-6">
              <Button variant="ghost" size="icon" onClick={() => navigate('/scenarios')}
                className="hover:bg-accent/10">
                <ArrowLeft className="w-5 h-5" />
              </Button>
              <h1 className="text-2xl font-bold">{isEdit ? 'Редактировать сценарий' : 'Новый сценарий'}</h1>
            </div>

            {/* Steps indicator */}
            <div className="flex items-center gap-1 mb-8">
              {STEPS.map((label, i) => (
                <div key={i} className="flex items-center gap-1 flex-1">
                  <div className={`flex items-center justify-center w-7 h-7 rounded-full text-xs font-bold border-2 transition-colors
                    ${i < step ? 'bg-primary border-primary text-primary-foreground'
                      : i === step ? 'border-primary text-primary'
                      : 'border-muted-foreground/30 text-muted-foreground'}`}>
                    {i < step ? <Check className="w-3 h-3" /> : i + 1}
                  </div>
                  <span className={`text-xs hidden sm:block ${i === step ? 'text-foreground font-medium' : 'text-muted-foreground'}`}>
                    {label}
                  </span>
                  {i < STEPS.length - 1 && <div className="h-px bg-border flex-1 mx-1" />}
                </div>
              ))}
            </div>

            {/* STEP 0 — Info */}
            {step === 0 && (
              <div className="bg-card/80 backdrop-blur-sm border border-border rounded-xl p-6 space-y-4">
                <h2 className="text-lg font-semibold">Информация о сценарии</h2>
                <div>
                  <Label htmlFor="name">Название *</Label>
                  <Input id="name" value={name} onChange={(e) => setName(e.target.value)}
                    placeholder="Тёмный замок Дракона" className="mt-1" />
                </div>
                <div>
                  <Label htmlFor="story">Сюжет / описание для мастера</Label>
                  <Textarea id="story" value={story} onChange={(e) => setStory(e.target.value)}
                    placeholder="Группа искателей приключений получила задание..."
                    className="mt-1 min-h-[140px]" />
                </div>
              </div>
            )}

            {/* STEP 1 — Map */}
            {step === 1 && (
              <div className="bg-card/80 backdrop-blur-sm border border-border rounded-xl p-6 space-y-4">
                <h2 className="text-lg font-semibold">Карта сценария</h2>
                <label className="flex flex-col items-center justify-center border-2 border-dashed border-border rounded-lg p-8 cursor-pointer hover:border-primary/50 transition-colors">
                  <Upload className="w-10 h-10 text-muted-foreground mb-2" />
                  <span className="text-sm text-muted-foreground">Нажмите для выбора карты (PNG, JPG, WebP, до 10 МБ)</span>
                  <input type="file" accept="image/*" className="hidden" onChange={handleMapFileChange} />
                </label>
                {mapPreview && (
                  <div className="relative rounded-lg overflow-hidden border border-border">
                    <img src={mapPreview} alt="Map preview" className="w-full max-h-64 object-contain bg-black/20" />
                    <Button variant="destructive" size="sm"
                      className="absolute top-2 right-2"
                      onClick={() => { setMapPreview(null); setMapFile(null); setMapUrl(null); }}>
                      Удалить
                    </Button>
                  </div>
                )}
                {!mapPreview && <p className="text-sm text-muted-foreground text-center">Карта необязательна. Можно добавить позже.</p>}
              </div>
            )}

            {/* STEP 2 — NPCs */}
            {step === 2 && (
              <div className="bg-card/80 backdrop-blur-sm border border-border rounded-xl p-6 space-y-4">
                <h2 className="text-lg font-semibold">НПС на карте</h2>
                <p className="text-sm text-muted-foreground">
                  {mapPreview ? 'Кликните на карте чтобы добавить НПС' : 'Карта не загружена — добавьте НПС списком ниже.'}
                </p>
                {mapPreview && (
                  <div ref={mapRef} className="relative rounded-lg overflow-hidden border border-border cursor-crosshair"
                    onClick={handleMapClickNpc}>
                    <img src={mapPreview} alt="Map" className="w-full max-h-80 object-contain bg-black/20" />
                    {npcs.map((npc) => (
                      <div key={npc.localId}
                        className="absolute -translate-x-1/2 -translate-y-1/2 flex flex-col items-center"
                        style={{ left: `${npc.x}%`, top: `${npc.y}%` }}>
                        <div className={`w-6 h-6 rounded-full flex items-center justify-center text-white text-xs border-2 ${npc.is_hidden ? 'bg-amber-600 border-amber-400' : 'bg-blue-600 border-blue-400'}`}>
                          <User2 className="w-3 h-3" />
                        </div>
                        <span className="text-xs bg-black/70 text-white px-1 rounded mt-0.5 whitespace-nowrap">{npc.name}</span>
                      </div>
                    ))}
                  </div>
                )}
                <Button variant="outline" size="sm" onClick={() => {
                  setPendingNpcPos({ x: 50, y: 50 });
                  setNpcForm({ is_hidden: true, x: 50, y: 50 });
                  setNpcDialog(true);
                }}>
                  + Добавить НПС
                </Button>
                {npcs.length > 0 && (
                  <div className="space-y-2">
                    {npcs.map((npc) => (
                      <div key={npc.localId} className="flex items-center justify-between bg-muted/40 rounded px-3 py-2">
                        <div className="flex items-center gap-2">
                          {npc.is_hidden ? <EyeOff className="w-4 h-4 text-amber-400" /> : <Eye className="w-4 h-4 text-blue-400" />}
                          <span className="text-sm font-medium">{npc.name}</span>
                          {npc.monster_slug && <span className="text-xs text-muted-foreground">({npc.monster_slug})</span>}
                        </div>
                        <Button variant="ghost" size="icon" className="h-6 w-6 text-destructive"
                          onClick={() => setNpcs((prev) => prev.filter((n) => n.localId !== npc.localId))}>
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* STEP 3 — Items */}
            {step === 3 && (
              <div className="bg-card/80 backdrop-blur-sm border border-border rounded-xl p-6 space-y-4">
                <h2 className="text-lg font-semibold">Скрытые предметы</h2>
                <p className="text-sm text-muted-foreground">
                  {mapPreview ? 'Кликните на карте чтобы добавить скрытый предмет' : 'Добавьте предметы списком ниже.'}
                </p>
                {mapPreview && (
                  <div ref={mapRef} className="relative rounded-lg overflow-hidden border border-border cursor-crosshair"
                    onClick={handleMapClickItem}>
                    <img src={mapPreview} alt="Map" className="w-full max-h-80 object-contain bg-black/20" />
                    {items.map((item) => (
                      <div key={item.localId}
                        className="absolute -translate-x-1/2 -translate-y-1/2 flex flex-col items-center"
                        style={{ left: `${item.x}%`, top: `${item.y}%` }}>
                        <div className="w-6 h-6 rounded-full bg-purple-600 border-2 border-purple-400 flex items-center justify-center text-white">
                          <Package className="w-3 h-3" />
                        </div>
                        <span className="text-xs bg-black/70 text-white px-1 rounded mt-0.5 whitespace-nowrap">{item.name}</span>
                      </div>
                    ))}
                  </div>
                )}
                <Button variant="outline" size="sm" onClick={() => {
                  setPendingItemPos({ x: 50, y: 50 });
                  setItemForm({ x: 50, y: 50, item_type: 'item', quantity: 1 });
                  setItemDialog(true);
                }}>
                  + Добавить предмет
                </Button>
                {items.length > 0 && (
                  <div className="space-y-2">
                    {items.map((item) => (
                      <div key={item.localId} className="flex items-center justify-between bg-muted/40 rounded px-3 py-2">
                        <div className="flex items-center gap-2">
                          <Package className="w-4 h-4 text-purple-400" />
                          <span className="text-sm font-medium">{item.name}</span>
                          <span className="text-xs text-muted-foreground">×{item.quantity}</span>
                        </div>
                        <Button variant="ghost" size="icon" className="h-6 w-6 text-destructive"
                          onClick={() => setItems((prev) => prev.filter((i) => i.localId !== item.localId))}>
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* STEP 4 — Review */}
            {step === 4 && (
              <div className="bg-card/80 backdrop-blur-sm border border-border rounded-xl p-6 space-y-4">
                <h2 className="text-lg font-semibold">Сводка сценария</h2>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">Название</p>
                    <p className="font-medium">{name || '—'}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Карта</p>
                    <p className="font-medium">{mapPreview ? 'Загружена' : 'Не задана'}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">НПС</p>
                    <p className="font-medium">{npcs.length} ({npcs.filter((n) => n.is_hidden).length} скрытых)</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Скрытые предметы</p>
                    <p className="font-medium">{items.length}</p>
                  </div>
                </div>
                {story && (
                  <div>
                    <p className="text-muted-foreground text-sm mb-1">Сюжет</p>
                    <p className="text-sm bg-muted/40 rounded p-3 max-h-32 overflow-y-auto">{story}</p>
                  </div>
                )}
              </div>
            )}

            {/* Navigation */}
            <div className="flex justify-between mt-6">
              <Button variant="outline" onClick={() => setStep((s) => Math.max(s - 1, 0))} disabled={step === 0}>
                <ArrowLeft className="w-4 h-4 mr-1" /> Назад
              </Button>
              {step < STEPS.length - 1 ? (
                <Button onClick={handleNext}>
                  Далее <ArrowRight className="w-4 h-4 ml-1" />
                </Button>
              ) : (
                <Button onClick={handleSave} disabled={saving}>
                  {saving
                    ? <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                    : <Check className="w-4 h-4 mr-1" />}
                  Сохранить
                </Button>
              )}
            </div>
          </div>
        </main>
      </div>

      {/* NPC Dialog */}
      <Dialog open={npcDialog} onOpenChange={setNpcDialog}>
        <DialogContent>
          <DialogHeader><DialogTitle>Добавить НПС</DialogTitle></DialogHeader>
          <div className="space-y-3">
            <div>
              <Label>Имя НПС *</Label>
              <Input value={npcForm.name ?? ''} onChange={(e) => setNpcForm((f) => ({ ...f, name: e.target.value }))}
                placeholder="Стражник, Goblin Boss..." className="mt-1" />
            </div>
            <div>
              <Label>Монстр из бестиария (необязательно)</Label>
              <Select value={npcForm.monster_slug ?? ''} onValueChange={(v) => setNpcForm((f) => ({ ...f, monster_slug: v || null }))}>
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder="Выберите монстра..." />
                </SelectTrigger>
                <SelectContent className="max-h-48">
                  <SelectItem value="">— Без шаблона —</SelectItem>
                  {monsters.map((m) => (
                    <SelectItem key={m.slug} value={m.slug}>{m.name} (CR {m.cr})</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-center gap-3">
              <Switch checked={npcForm.is_hidden ?? true}
                onCheckedChange={(v) => setNpcForm((f) => ({ ...f, is_hidden: v }))} />
              <Label className="cursor-pointer">
                {npcForm.is_hidden ? <span className="flex items-center gap-1"><EyeOff className="w-4 h-4 text-amber-400" /> Скрыт от игроков</span>
                  : <span className="flex items-center gap-1"><Eye className="w-4 h-4 text-blue-400" /> Виден игрокам</span>}
              </Label>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setNpcDialog(false)}>Отмена</Button>
            <Button onClick={addNpc} disabled={!npcForm.name?.trim()}>Добавить</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Item Dialog */}
      <Dialog open={itemDialog} onOpenChange={setItemDialog}>
        <DialogContent>
          <DialogHeader><DialogTitle>Добавить скрытый предмет</DialogTitle></DialogHeader>
          <div className="space-y-3">
            <div>
              <Label>Название *</Label>
              <Input value={itemForm.name ?? ''} onChange={(e) => setItemForm((f) => ({ ...f, name: e.target.value }))}
                placeholder="Зачарованный меч, Свиток..." className="mt-1" />
            </div>
            <div>
              <Label>Тип предмета</Label>
              <Select value={itemForm.item_type ?? 'item'}
                onValueChange={(v) => setItemForm((f) => ({ ...f, item_type: v as 'weapon' | 'armor' | 'item', item_id: undefined }))}>
                <SelectTrigger className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="weapon">Оружие</SelectItem>
                  <SelectItem value="armor">Броня</SelectItem>
                  <SelectItem value="item">Предмет</SelectItem>
                </SelectContent>
              </Select>
            </div>
            {itemForm.item_type === 'weapon' && weapons.length > 0 && (
              <div>
                <Label>Оружие из каталога</Label>
                <Select value={itemForm.item_id ?? ''} onValueChange={(v) => setItemForm((f) => ({ ...f, item_id: v }))}>
                  <SelectTrigger className="mt-1"><SelectValue placeholder="Выберите..." /></SelectTrigger>
                  <SelectContent className="max-h-48">
                    {weapons.map((w) => <SelectItem key={w.id} value={w.id}>{w.name}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
            )}
            {itemForm.item_type === 'armor' && armors.length > 0 && (
              <div>
                <Label>Броня из каталога</Label>
                <Select value={itemForm.item_id ?? ''} onValueChange={(v) => setItemForm((f) => ({ ...f, item_id: v }))}>
                  <SelectTrigger className="mt-1"><SelectValue placeholder="Выберите..." /></SelectTrigger>
                  <SelectContent className="max-h-48">
                    {armors.map((a) => <SelectItem key={a.id} value={a.id}>{a.name}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
            )}
            {itemForm.item_type === 'item' && genericItems.length > 0 && (
              <div>
                <Label>Предмет из каталога</Label>
                <Select value={itemForm.item_id ?? ''} onValueChange={(v) => setItemForm((f) => ({ ...f, item_id: v }))}>
                  <SelectTrigger className="mt-1"><SelectValue placeholder="Выберите..." /></SelectTrigger>
                  <SelectContent className="max-h-48">
                    {genericItems.map((i) => <SelectItem key={i.id} value={i.id}>{i.name}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
            )}
            <div>
              <Label>Количество</Label>
              <Input type="number" min={1} value={itemForm.quantity ?? 1}
                onChange={(e) => setItemForm((f) => ({ ...f, quantity: parseInt(e.target.value) || 1 }))}
                className="mt-1 w-24" />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setItemDialog(false)}>Отмена</Button>
            <Button onClick={addItem} disabled={!itemForm.name?.trim()}>Добавить</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
