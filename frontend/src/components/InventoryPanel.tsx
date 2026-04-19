import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Input } from './ui/input';
import { ScrollArea } from './ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { inventoryAPI, gameDataAPI } from '../services/api';
import type { InventoryItem, WeaponData, ArmorData } from '../types/character';
import { Sword, Shield, Package, Plus, Trash2, Star } from 'lucide-react';

interface InventoryPanelProps {
  characterId: string;
}

export default function InventoryPanel({ characterId }: InventoryPanelProps) {
  const [items, setItems] = useState<InventoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [addOpen, setAddOpen] = useState(false);
  const [addTab, setAddTab] = useState<'weapon' | 'armor'>('weapon');
  const [weapons, setWeapons] = useState<WeaponData[]>([]);
  const [armors, setArmors] = useState<ArmorData[]>([]);
  const [search, setSearch] = useState('');

  useEffect(() => {
    loadInventory();
  }, [characterId]);

  async function loadInventory() {
    setLoading(true);
    try {
      const data = await inventoryAPI.getInventory(characterId);
      setItems(data.items);
    } catch (e) {
      console.error('Failed to load inventory', e);
    } finally {
      setLoading(false);
    }
  }

  async function openAddDialog() {
    setAddOpen(true);
    const [ws, as] = await Promise.all([gameDataAPI.getWeapons(), gameDataAPI.getArmors()]);
    setWeapons(ws);
    setArmors(as);
  }

  async function handleAdd(itemType: 'weapon' | 'armor', itemId: string) {
    try {
      await inventoryAPI.addItem(characterId, itemType, itemId);
      await loadInventory();
      setAddOpen(false);
    } catch (e: any) {
      console.error(e);
    }
  }

  async function handleRemove(invId: string) {
    try {
      await inventoryAPI.removeItem(characterId, invId);
      setItems(prev => prev.filter(i => i.id !== invId));
    } catch (e) {
      console.error(e);
    }
  }

  async function handleEquip(item: InventoryItem) {
    const newEquipped = !item.is_equipped;
    const slot = newEquipped
      ? item.item_type === 'armor' ? 'armor'
      : item.item_type === 'weapon' ? 'main_hand'
      : undefined
      : undefined;
    try {
      const updated = await inventoryAPI.equipItem(characterId, item.id, newEquipped, slot);
      setItems(prev => prev.map(i => i.id === updated.id ? updated : i));
    } catch (e) {
      console.error(e);
    }
  }

  const weapons_inv = items.filter(i => i.item_type === 'weapon');
  const armor_inv = items.filter(i => i.item_type === 'armor');
  const other_inv = items.filter(i => i.item_type === 'item');

  const filteredWeapons = weapons.filter(w => w.name.toLowerCase().includes(search.toLowerCase()));
  const filteredArmors = armors.filter(a => a.name.toLowerCase().includes(search.toLowerCase()));

  function renderItem(item: InventoryItem) {
    const name = item.item_data?.name ?? '???';
    const detail = item.item_type === 'weapon'
      ? item.item_data?.damage_dice ? `${item.item_data.damage_dice} ${item.item_data.damage_type ?? ''}` : ''
      : item.item_type === 'armor'
      ? `КБ ${item.item_data?.base_ac ?? '?'}`
      : '';

    return (
      <div key={item.id} className="flex items-center justify-between p-2 rounded border border-border hover:bg-muted/30 gap-2">
        <div className="flex items-center gap-2 min-w-0">
          {item.item_type === 'weapon' ? <Sword className="h-4 w-4 shrink-0 text-red-400" />
            : item.item_type === 'armor' ? <Shield className="h-4 w-4 shrink-0 text-blue-400" />
            : <Package className="h-4 w-4 shrink-0 text-yellow-400" />}
          <span className="font-medium truncate">{name}</span>
          {detail && <span className="text-xs text-muted-foreground">{detail}</span>}
          {item.quantity > 1 && <Badge variant="outline" className="text-xs">×{item.quantity}</Badge>}
        </div>
        <div className="flex items-center gap-1 shrink-0">
          <Button
            variant={item.is_equipped ? 'default' : 'outline'}
            size="icon"
            className="h-7 w-7"
            title={item.is_equipped ? 'Снять' : 'Надеть'}
            onClick={() => handleEquip(item)}
          >
            <Star className="h-3 w-3" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="h-7 w-7 text-destructive"
            onClick={() => handleRemove(item.id)}
          >
            <Trash2 className="h-3 w-3" />
          </Button>
        </div>
      </div>
    );
  }

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base flex items-center gap-2">
            <Package className="h-4 w-4" /> Инвентарь
          </CardTitle>
          <Button size="sm" variant="outline" onClick={openAddDialog}>
            <Plus className="h-3 w-3 mr-1" /> Добавить
          </Button>
        </div>
      </CardHeader>

      <CardContent className="flex-1 overflow-hidden p-3">
        <ScrollArea className="h-full">
          {loading ? (
            <p className="text-muted-foreground text-sm text-center py-4">Загрузка...</p>
          ) : items.length === 0 ? (
            <p className="text-muted-foreground text-sm text-center py-4">Инвентарь пуст</p>
          ) : (
            <div className="space-y-3">
              {weapons_inv.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-muted-foreground mb-1 uppercase tracking-wide">Оружие</p>
                  <div className="space-y-1">{weapons_inv.map(renderItem)}</div>
                </div>
              )}
              {armor_inv.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-muted-foreground mb-1 uppercase tracking-wide">Доспехи</p>
                  <div className="space-y-1">{armor_inv.map(renderItem)}</div>
                </div>
              )}
              {other_inv.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-muted-foreground mb-1 uppercase tracking-wide">Прочее</p>
                  <div className="space-y-1">{other_inv.map(renderItem)}</div>
                </div>
              )}
            </div>
          )}
        </ScrollArea>
      </CardContent>

      <Dialog open={addOpen} onOpenChange={setAddOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Добавить предмет</DialogTitle>
          </DialogHeader>
          <Input
            placeholder="Поиск..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="mb-3"
          />
          <Tabs value={addTab} onValueChange={v => setAddTab(v as any)}>
            <TabsList className="w-full">
              <TabsTrigger value="weapon" className="flex-1">Оружие</TabsTrigger>
              <TabsTrigger value="armor" className="flex-1">Доспехи</TabsTrigger>
            </TabsList>
            <TabsContent value="weapon">
              <ScrollArea className="h-64">
                {filteredWeapons.map(w => (
                  <div
                    key={w.id}
                    className="flex items-center justify-between p-2 hover:bg-muted/30 rounded cursor-pointer"
                    onClick={() => handleAdd('weapon', w.id)}
                  >
                    <div>
                      <p className="font-medium text-sm">{w.name}</p>
                      <p className="text-xs text-muted-foreground">{w.damage_dice} {w.damage_type} · {w.category}</p>
                    </div>
                    <Plus className="h-4 w-4 text-primary" />
                  </div>
                ))}
              </ScrollArea>
            </TabsContent>
            <TabsContent value="armor">
              <ScrollArea className="h-64">
                {filteredArmors.map(a => (
                  <div
                    key={a.id}
                    className="flex items-center justify-between p-2 hover:bg-muted/30 rounded cursor-pointer"
                    onClick={() => handleAdd('armor', a.id)}
                  >
                    <div>
                      <p className="font-medium text-sm">{a.name}</p>
                      <p className="text-xs text-muted-foreground">КБ {a.base_ac} · {a.category}</p>
                    </div>
                    <Plus className="h-4 w-4 text-primary" />
                  </div>
                ))}
              </ScrollArea>
            </TabsContent>
          </Tabs>
        </DialogContent>
      </Dialog>
    </Card>
  );
}
