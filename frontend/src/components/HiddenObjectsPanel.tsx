import { useState } from 'react';
import { Eye, Package, User2, ChevronDown, ChevronUp } from 'lucide-react';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { useGameStore } from '../store/gameStore';
import { gamesAPI } from '../services/api';
import { useToast } from '../hooks/use-toast';

interface Props {
  gameId: string;
}

export default function HiddenObjectsPanel({ gameId }: Props) {
  const { hiddenTokens, revealHiddenToken, participants } = useGameStore();
  const { toast } = useToast();
  const [expanded, setExpanded] = useState(true);
  const [givingLoot, setGivingLoot] = useState<Record<string, boolean>>({});

  const hiddenNpcs = hiddenTokens.filter((t) => t.token_type === 'npc');
  const hiddenItems = hiddenTokens.filter((t) => t.token_type === 'item');

  const playersWithCharacters = participants.filter(
    (p) => p.role === 'player' && p.character_id
  );

  const handleReveal = async (tokenId: string) => {
    try {
      await gamesAPI.revealToken(gameId, tokenId);
      revealHiddenToken(tokenId);
      toast({ title: 'Токен раскрыт', description: 'Игроки теперь видят его на карте' });
    } catch {
      toast({ title: 'Ошибка', description: 'Не удалось раскрыть токен', variant: 'destructive' });
    }
  };

  const handleGiveLoot = async (tokenId: string, lootEntry: {
    item_type: string; item_id: string; quantity: number;
  }, characterId: string) => {
    setGivingLoot((prev) => ({ ...prev, [tokenId]: true }));
    try {
      await gamesAPI.giveItem(gameId, {
        character_id: characterId,
        item_type: lootEntry.item_type,
        item_id: lootEntry.item_id,
        quantity: lootEntry.quantity,
      });
      toast({ title: 'Предмет выдан', description: 'Предмет добавлен в инвентарь персонажа' });
    } catch {
      toast({ title: 'Ошибка', description: 'Не удалось выдать предмет', variant: 'destructive' });
    } finally {
      setGivingLoot((prev) => ({ ...prev, [tokenId]: false }));
    }
  };

  const handleGiveItemToken = async (tokenId: string, characterId: string) => {
    const token = hiddenItems.find((t) => t.id === tokenId);
    if (!token || !token.token_metadata) return;
    const meta = token.token_metadata as { item_type?: string; item_id?: string; quantity?: number };
    if (!meta.item_type || !meta.item_id) return;
    await handleGiveLoot(tokenId, {
      item_type: meta.item_type,
      item_id: meta.item_id,
      quantity: meta.quantity ?? 1,
    }, characterId);
  };

  if (hiddenTokens.length === 0) return null;

  return (
    <div className="bg-card/90 backdrop-blur-sm border border-border rounded-lg overflow-hidden mt-2">
      <button
        className="w-full flex items-center justify-between px-3 py-2 text-sm font-medium hover:bg-accent/10 transition-colors"
        onClick={() => setExpanded((v) => !v)}
      >
        <span className="flex items-center gap-2">
          <Eye className="w-4 h-4 text-amber-400" />
          Скрытые объекты ({hiddenTokens.length})
        </span>
        {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>

      {expanded && (
        <div className="px-3 pb-3 space-y-3 max-h-80 overflow-y-auto">
          {hiddenNpcs.length > 0 && (
            <div>
              <p className="text-xs text-muted-foreground uppercase tracking-wide mb-1 flex items-center gap-1">
                <User2 className="w-3 h-3" /> НПС
              </p>
              {hiddenNpcs.map((token) => {
                const loot = (token.token_metadata as { loot?: Array<{ item_type: string; item_id: string; quantity: number }> } | null)?.loot ?? [];
                return (
                  <div key={token.id} className="bg-muted/40 rounded p-2 mb-1">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-sm font-medium truncate">{token.name}</span>
                      <Button size="sm" variant="outline" className="shrink-0 h-6 text-xs"
                        onClick={() => handleReveal(token.id)}>
                        Раскрыть
                      </Button>
                    </div>
                    {loot.length > 0 && playersWithCharacters.length > 0 && (
                      <div className="mt-2 space-y-1">
                        <p className="text-xs text-muted-foreground">Добыча:</p>
                        {loot.map((entry, i) => (
                          <LootGiveRow
                            key={i}
                            entry={entry}
                            players={playersWithCharacters}
                            loading={!!givingLoot[token.id]}
                            onGive={(charId) => handleGiveLoot(token.id, entry, charId)}
                          />
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}

          {hiddenItems.length > 0 && (
            <div>
              <p className="text-xs text-muted-foreground uppercase tracking-wide mb-1 flex items-center gap-1">
                <Package className="w-3 h-3" /> Предметы
              </p>
              {hiddenItems.map((token) => (
                <div key={token.id} className="bg-muted/40 rounded p-2 mb-1">
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-sm font-medium truncate">{token.name}</span>
                    <Button size="sm" variant="outline" className="shrink-0 h-6 text-xs"
                      onClick={() => handleReveal(token.id)}>
                      Раскрыть
                    </Button>
                  </div>
                  {playersWithCharacters.length > 0 && (
                    <div className="mt-1">
                      <GiveToPlayerSelect
                        players={playersWithCharacters}
                        loading={!!givingLoot[token.id]}
                        onGive={(charId) => handleGiveItemToken(token.id, charId)}
                      />
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function LootGiveRow({ entry, players, loading, onGive }: {
  entry: { item_type: string; item_id: string; quantity: number };
  players: Array<{ user_id: string; username: string; character_id?: string }>;
  loading: boolean;
  onGive: (charId: string) => void;
}) {
  const [selected, setSelected] = useState('');
  return (
    <div className="flex gap-1 items-center">
      <span className="text-xs text-muted-foreground flex-1">×{entry.quantity} {entry.item_type}</span>
      <Select value={selected} onValueChange={setSelected}>
        <SelectTrigger className="h-6 text-xs w-28">
          <SelectValue placeholder="Игрок" />
        </SelectTrigger>
        <SelectContent>
          {players.map((p) => (
            <SelectItem key={p.user_id} value={p.character_id!}>{p.username}</SelectItem>
          ))}
        </SelectContent>
      </Select>
      <Button size="sm" variant="secondary" className="h-6 text-xs px-2" disabled={!selected || loading}
        onClick={() => selected && onGive(selected)}>
        Дать
      </Button>
    </div>
  );
}

function GiveToPlayerSelect({ players, loading, onGive }: {
  players: Array<{ user_id: string; username: string; character_id?: string }>;
  loading: boolean;
  onGive: (charId: string) => void;
}) {
  const [selected, setSelected] = useState('');
  return (
    <div className="flex gap-1 items-center mt-1">
      <Select value={selected} onValueChange={setSelected}>
        <SelectTrigger className="h-6 text-xs flex-1">
          <SelectValue placeholder="Выдать игроку" />
        </SelectTrigger>
        <SelectContent>
          {players.map((p) => (
            <SelectItem key={p.user_id} value={p.character_id!}>{p.username}</SelectItem>
          ))}
        </SelectContent>
      </Select>
      <Button size="sm" variant="secondary" className="h-6 text-xs px-2" disabled={!selected || loading}
        onClick={() => selected && onGive(selected)}>
        Дать
      </Button>
    </div>
  );
}
