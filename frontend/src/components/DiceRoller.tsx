import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { ScrollArea } from './ui/scroll-area';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Input } from './ui/input';
import { Dices, Search, Filter } from 'lucide-react';
import { socketService } from '../services/socket';
import { gamesAPI, diceAPI } from '../services/api';
import { useAuthStore } from '../store/authStore';
import type { DiceRollHistoryItem, RollType, DiceTemplate } from '../types/dice';

interface DiceRollerProps {
  gameId: string;
  selectedCharacterId?: string | null;
  onRoll: (count: number, faces: number, rollType?: string, modifier?: number, advantage?: boolean) => void;
}

const DICE_TYPES = [
  { faces: 4, label: 'd4' },
  { faces: 6, label: 'd6' },
  { faces: 8, label: 'd8' },
  { faces: 10, label: 'd10' },
  { faces: 12, label: 'd12' },
  { faces: 20, label: 'd20' },
];

const ROLL_TYPES: { value: RollType | 'all'; label: string }[] = [
  { value: 'all', label: 'Все типы' },
  { value: 'attack', label: 'Атака' },
  { value: 'save', label: 'Спасбросок' },
  { value: 'skill', label: 'Навык' },
  { value: 'custom', label: 'Произвольный' },
];

export default function DiceRoller({ gameId, selectedCharacterId, onRoll }: DiceRollerProps) {
  const { user } = useAuthStore();
  const [selectedFaces, setSelectedFaces] = useState(20);
  const [count, setCount] = useState(1);
  const [advantage, setAdvantage] = useState<boolean | null>(null); // null = обычный, true = преимущество, false = помеха
  const [history, setHistory] = useState<DiceRollHistoryItem[]>([]);
  const [isRolling, setIsRolling] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  
  // Шаблоны бросков
  const [templates, setTemplates] = useState<Record<string, DiceTemplate>>({});
  const [isLoadingTemplates, setIsLoadingTemplates] = useState(false);
  
  // Фильтры
  const [filterUserId, setFilterUserId] = useState<string>('all');
  const [filterRollType, setFilterRollType] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [historyOffset, setHistoryOffset] = useState(0);
  const [hasMoreHistory, setHasMoreHistory] = useState(true);
  const HISTORY_LIMIT = 50;

  // Загрузка истории с сервера
  const loadHistory = async (offset: number = 0, append: boolean = false) => {
    if (isLoadingHistory) return;
    
    setIsLoadingHistory(true);
    try {
      const filters = {
        limit: HISTORY_LIMIT,
        offset,
        ...(filterUserId !== 'all' && { user_id: filterUserId }),
        ...(filterRollType !== 'all' && { roll_type: filterRollType }),
      };
      
      const serverHistory = await gamesAPI.getDiceHistory(gameId, filters);
      
      if (append) {
        setHistory((prev) => [...prev, ...serverHistory]);
      } else {
        setHistory(serverHistory);
      }
      
      setHasMoreHistory(serverHistory.length === HISTORY_LIMIT);
      setHistoryOffset(offset + serverHistory.length);
    } catch (error) {
      console.error('Failed to load dice history:', error);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  // Загружаем шаблоны при монтировании
  useEffect(() => {
    const loadTemplates = async () => {
      setIsLoadingTemplates(true);
      try {
        const loadedTemplates = await diceAPI.getTemplates();
        setTemplates(loadedTemplates);
      } catch (error) {
        console.error('Failed to load dice templates:', error);
      } finally {
        setIsLoadingTemplates(false);
      }
    };
    loadTemplates();
  }, []);

  // Загружаем историю при монтировании и при изменении фильтров
  useEffect(() => {
    setHistoryOffset(0);
    loadHistory(0, false);
  }, [filterUserId, filterRollType]);

  // Обработка новых бросков через WebSocket
  useEffect(() => {
    const handleDiceRolled = (data: {
      game_id: string;
      user_id: string;
      username: string;
      count: number;
      faces: number;
      rolls: Array<{ die_id: string; value: number }>;
      total: number;
      roll_type?: string;
      modifier?: number;
    }) => {
      if (data.game_id !== gameId) return;
      
      setIsRolling(false);
      
      // Добавляем новый бросок в начало истории
      const newHistoryItem: DiceRollHistoryItem = {
        id: crypto.randomUUID(),
        user_id: data.user_id,
        username: data.username,
        count: data.count,
        faces: data.faces,
        rolls: data.rolls,
        total: data.total,
        roll_type: data.roll_type || null,
        modifier: data.modifier || null,
        advantage_type: data.advantage_type || null,
        advantage_rolls: data.advantage_rolls || null,
        selected_roll: data.selected_roll || null,
        created_at: new Date().toISOString(),
      };
      
      setHistory((prev) => {
        const updated = [newHistoryItem, ...prev];
        // Ограничиваем локальную историю до 100 записей
        return updated.slice(0, 100);
      });
    };

    socketService.onDiceRolled(handleDiceRolled);

    return () => {
      socketService.off('dice:rolled');
    };
  }, [gameId]);

  const handleRoll = () => {
    setIsRolling(true);
    // Advantage/disadvantage применяется только для одного кубика
    const advantageValue = (count === 1 && advantage !== null) ? advantage : undefined;
    onRoll(count, selectedFaces, undefined, undefined, advantageValue);
  };

  // Обработчик быстрого броска по шаблону
  const handleTemplateRoll = async (templateName: string) => {
    setIsRolling(true);
    try {
      const templateResult = await diceAPI.applyTemplate(
        templateName,
        selectedCharacterId || undefined
      );
      
      // Вызываем onRoll с параметрами из шаблона
      onRoll(
        templateResult.count,
        templateResult.faces,
        templateResult.roll_type,
        templateResult.modifier || undefined
      );
    } catch (error) {
      console.error('Failed to apply template:', error);
      setIsRolling(false);
    }
  };

  // Группируем шаблоны по типу
  const templatesByType = {
    attack: Object.entries(templates).filter(([_, t]) => t.roll_type === 'attack'),
    save: Object.entries(templates).filter(([_, t]) => t.roll_type === 'save'),
    skill: Object.entries(templates).filter(([_, t]) => t.roll_type === 'skill'),
  };

  // Фильтрация истории по поисковому запросу
  const filteredHistory = history.filter((roll) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      roll.username.toLowerCase().includes(query) ||
      `${roll.count}d${roll.faces}`.toLowerCase().includes(query) ||
      roll.total.toString().includes(query) ||
      (roll.roll_type && roll.roll_type.toLowerCase().includes(query))
    );
  });

  // Получаем список уникальных пользователей из истории для фильтра
  const uniqueUsers = Array.from(
    new Set(history.map((roll) => ({ id: roll.user_id, username: roll.username })))
  ).reduce((acc, user) => {
    if (!acc.find((u) => u.id === user.id)) {
      acc.push(user);
    }
    return acc;
  }, [] as Array<{ id: string; username: string }>);

  return (
    <Card className="w-80">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Dices className="w-5 h-5" />
          Бросок кубиков
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Выбор типа кубика */}
        <div>
          <label className="text-sm font-medium mb-2 block">Тип кубика</label>
          <div className="grid grid-cols-3 gap-2">
            {DICE_TYPES.map((dice) => (
              <Button
                key={dice.faces}
                variant={selectedFaces === dice.faces ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedFaces(dice.faces)}
              >
                {dice.label}
              </Button>
            ))}
          </div>
        </div>

        {/* Количество кубиков */}
        <div>
          <label className="text-sm font-medium mb-2 block">Количество</label>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                const newCount = Math.max(1, count - 1);
                setCount(newCount);
                // Сбрасываем advantage если количество больше 1
                if (newCount > 1) {
                  setAdvantage(null);
                }
              }}
            >
              -
            </Button>
            <span className="flex-1 text-center font-bold">{count}</span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                const newCount = Math.min(10, count + 1);
                setCount(newCount);
                // Сбрасываем advantage если количество больше 1
                if (newCount > 1) {
                  setAdvantage(null);
                }
              }}
            >
              +
            </Button>
          </div>
        </div>

        {/* Преимущество/Помеха (только для одного кубика) */}
        {count === 1 && (
          <div>
            <label className="text-sm font-medium mb-2 block">Преимущество/Помеха</label>
            <div className="grid grid-cols-3 gap-2">
              <Button
                variant={advantage === true ? "default" : "outline"}
                size="sm"
                onClick={() => setAdvantage(advantage === true ? null : true)}
                className="text-xs"
              >
                Преимущество
              </Button>
              <Button
                variant={advantage === null ? "default" : "outline"}
                size="sm"
                onClick={() => setAdvantage(null)}
                className="text-xs"
              >
                Обычно
              </Button>
              <Button
                variant={advantage === false ? "default" : "outline"}
                size="sm"
                onClick={() => setAdvantage(advantage === false ? null : false)}
                className="text-xs"
              >
                Помеха
              </Button>
            </div>
            {advantage !== null && (
              <p className="text-xs text-muted-foreground mt-1">
                {advantage 
                  ? "Бросится 2 кубика, выберется лучший результат"
                  : "Бросится 2 кубика, выберется худший результат"}
              </p>
            )}
          </div>
        )}

        {/* Кнопка броска */}
        <Button 
          onClick={handleRoll} 
          className="w-full" 
          size="lg"
          disabled={isRolling}
        >
          {isRolling ? (
            <>
              <Dices className="w-4 h-4 mr-2 animate-spin" />
              Бросок...
            </>
          ) : (
            <>
              <Dices className="w-4 h-4 mr-2" />
              Бросить {count}d{selectedFaces}
            </>
          )}
        </Button>

        {/* Панель быстрых бросков (шаблоны) */}
        {Object.keys(templates).length > 0 && (
          <div className="space-y-2 pt-2 border-t">
            <div className="text-sm font-medium">Быстрые броски</div>
            {!selectedCharacterId && (
              <div className="text-xs text-muted-foreground">
                Выберите персонажа для применения модификаторов
              </div>
            )}
            
            {/* Атаки */}
            {templatesByType.attack.length > 0 && (
              <div>
                <div className="text-xs text-muted-foreground mb-1">Атаки</div>
                <div className="grid grid-cols-2 gap-1">
                  {templatesByType.attack.map(([key, template]) => (
                    <Button
                      key={key}
                      variant="outline"
                      size="sm"
                      onClick={() => handleTemplateRoll(key)}
                      disabled={isRolling}
                      className="text-xs"
                    >
                      {template.label}
                    </Button>
                  ))}
                </div>
              </div>
            )}

            {/* Спасброски */}
            {templatesByType.save.length > 0 && (
              <div>
                <div className="text-xs text-muted-foreground mb-1">Спасброски</div>
                <div className="grid grid-cols-2 gap-1">
                  {templatesByType.save.map(([key, template]) => (
                    <Button
                      key={key}
                      variant="outline"
                      size="sm"
                      onClick={() => handleTemplateRoll(key)}
                      disabled={isRolling}
                      className="text-xs"
                    >
                      {template.label}
                    </Button>
                  ))}
                </div>
              </div>
            )}

            {/* Проверки навыков */}
            {templatesByType.skill.length > 0 && (
              <div>
                <div className="text-xs text-muted-foreground mb-1">Проверки</div>
                <div className="grid grid-cols-2 gap-1">
                  {templatesByType.skill.map(([key, template]) => (
                    <Button
                      key={key}
                      variant="outline"
                      size="sm"
                      onClick={() => handleTemplateRoll(key)}
                      disabled={isRolling}
                      className="text-xs"
                    >
                      {template.label}
                    </Button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Фильтры истории */}
        <div className="space-y-2 pt-2 border-t">
          <div className="flex items-center gap-2 text-sm font-medium">
            <Filter className="w-4 h-4" />
            Фильтры истории
          </div>
          
          {/* Поиск */}
          <div className="relative">
            <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Поиск по истории..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-8"
            />
          </div>

          {/* Фильтр по пользователю */}
          <Select value={filterUserId} onValueChange={setFilterUserId}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Все игроки" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Все игроки</SelectItem>
              {uniqueUsers.map((u) => (
                <SelectItem key={u.id} value={u.id}>
                  {u.username}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {/* Фильтр по типу проверки */}
          <Select value={filterRollType} onValueChange={setFilterRollType}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Все типы" />
            </SelectTrigger>
            <SelectContent>
              {ROLL_TYPES.map((type) => (
                <SelectItem key={type.value} value={type.value}>
                  {type.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* История бросков */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="text-sm font-medium">История бросков</label>
            {history.length > 0 && (
              <span className="text-xs text-muted-foreground">
                {filteredHistory.length} из {history.length}
              </span>
            )}
          </div>
          <ScrollArea className="h-64">
            <div className="space-y-2 pr-4">
              {filteredHistory.length === 0 ? (
                <div className="text-center text-sm text-muted-foreground py-8">
                  {isLoadingHistory ? 'Загрузка...' : 'История бросков пуста'}
                </div>
              ) : (
                <>
                  {filteredHistory.map((roll) => {
                    const isOwnRoll = roll.user_id === user?.id;
                    // Вычисляем сумму бросков без модификатора
                    const rollSum = roll.rolls.reduce((sum, die) => sum + die.value, 0);
                    const displayTotal = roll.modifier !== null && roll.modifier !== undefined
                      ? `${roll.total} (${rollSum} + ${roll.modifier >= 0 ? '+' : ''}${roll.modifier})`
                      : roll.total;
                    
                    return (
                      <div
                        key={roll.id}
                        className={`p-3 rounded-md text-sm border-2 transition-all ${
                          isOwnRoll
                            ? 'bg-primary/10 border-primary/30'
                            : 'bg-muted border-border'
                        }`}
                      >
                        <div className="flex justify-between items-center mb-2">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="font-medium">
                              {roll.count}d{roll.faces}
                            </span>
                            {roll.roll_type && (
                              <Badge variant="outline" className="text-xs">
                                {roll.roll_type === 'attack' ? 'Атака' :
                                 roll.roll_type === 'save' ? 'Спасбросок' :
                                 roll.roll_type === 'skill' ? 'Навык' :
                                 'Произвольный'}
                              </Badge>
                            )}
                            {roll.advantage_type && (
                              <Badge 
                                variant={roll.advantage_type === 'advantage' ? 'default' : 'destructive'} 
                                className="text-xs"
                              >
                                {roll.advantage_type === 'advantage' ? 'Преимущество' : 'Помеха'}
                              </Badge>
                            )}
                            <span className="text-xs text-muted-foreground">
                              {isOwnRoll ? '(Вы)' : roll.username}
                            </span>
                          </div>
                          <Badge 
                            variant={isOwnRoll ? 'default' : 'secondary'}
                            className="text-base font-bold"
                          >
                            {displayTotal}
                          </Badge>
                        </div>
                        <div className="flex gap-1 flex-wrap items-center">
                          {/* Показываем advantage_rolls если есть */}
                          {roll.advantage_rolls && roll.advantage_rolls.length === 2 ? (
                            <>
                              {roll.advantage_rolls.map((die, i) => {
                                const isSelected = roll.selected_roll && 
                                  die.die_id === roll.selected_roll.die_id && 
                                  die.value === roll.selected_roll.value;
                                return (
                                  <Badge
                                    key={i}
                                    variant={isSelected ? (roll.advantage_type === 'advantage' ? 'default' : 'destructive') : 'outline'}
                                    className={`text-xs font-mono ${isSelected ? 'ring-2 ring-offset-1' : ''}`}
                                  >
                                    {die.value}
                                  </Badge>
                                );
                              })}
                              <span className="text-xs text-muted-foreground mx-1">
                                {roll.advantage_type === 'advantage' ? '→' : '←'}
                              </span>
                              <Badge
                                variant="default"
                                className="text-xs font-mono font-bold"
                              >
                                {roll.selected_roll?.value || roll.total}
                              </Badge>
                            </>
                          ) : (
                            // Обычные броски
                            roll.rolls.map((die, i) => (
                              <Badge
                                key={i}
                                variant="outline"
                                className="text-xs font-mono"
                              >
                                {die.value}
                              </Badge>
                            ))
                          )}
                        </div>
                        <div className="text-xs text-muted-foreground mt-1">
                          {new Date(roll.created_at).toLocaleString('ru-RU')}
                        </div>
                      </div>
                    );
                  })}
                  
                  {/* Кнопка "Загрузить еще" */}
                  {hasMoreHistory && !isLoadingHistory && (
                    <Button
                      variant="outline"
                      className="w-full"
                      onClick={() => loadHistory(historyOffset, true)}
                    >
                      Показать больше
                    </Button>
                  )}
                  {isLoadingHistory && (
                    <div className="text-center text-sm text-muted-foreground py-4">
                      Загрузка...
                    </div>
                  )}
                </>
              )}
            </div>
          </ScrollArea>
        </div>
      </CardContent>
    </Card>
  );
}
