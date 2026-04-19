import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { ScrollArea } from './ui/scroll-area';
import { BookOpen, Send, History, X } from 'lucide-react';
import { socketService } from '../services/socket';

interface MasterScenePanelProps {
  gameId: string;
}

interface SceneHistoryItem {
  id: string;
  title?: string;
  description: string;
  timestamp: Date;
}

const QUICK_PHRASES = [
  "Вы слышите...",
  "В воздухе...",
  "Перед вами...",
  "Внезапно...",
  "Из темноты...",
  "Вы чувствуете...",
];

export default function MasterScenePanel({ gameId }: MasterScenePanelProps) {
  const [description, setDescription] = useState('');
  const [title, setTitle] = useState('');
  const [history, setHistory] = useState<SceneHistoryItem[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [isSending, setIsSending] = useState(false);

  const handleSend = () => {
    if (!description.trim()) {
      return;
    }

    setIsSending(true);
    socketService.sendSceneDescription(gameId, description.trim(), title.trim() || undefined);
    
    // Добавляем в историю
    const newItem: SceneHistoryItem = {
      id: Date.now().toString(),
      title: title.trim() || undefined,
      description: description.trim(),
      timestamp: new Date(),
    };
    setHistory((prev) => [newItem, ...prev].slice(0, 10)); // Храним последние 10
    
    // Очищаем поля
    setDescription('');
    setTitle('');
    setIsSending(false);
  };

  const handleQuickPhrase = (phrase: string) => {
    if (description.trim()) {
      setDescription(`${description}\n${phrase}`);
    } else {
      setDescription(phrase);
    }
  };

  const handleUseHistory = (item: SceneHistoryItem) => {
    setDescription(item.description);
    setTitle(item.title || '');
    setShowHistory(false);
  };

  return (
    <Card className="h-full border-2 border-primary bg-card/95 backdrop-blur-sm flex flex-col">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-lg">
            <BookOpen className="w-5 h-5 text-accent" />
            Описание сцены
          </CardTitle>
          {history.length > 0 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowHistory(!showHistory)}
            >
              <History className="w-4 h-4 mr-2" />
              История ({history.length})
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="flex-1 overflow-hidden flex flex-col space-y-4">
        {showHistory && history.length > 0 && (
          <div className="border-2 border-primary rounded-lg p-3 bg-muted/50">
            <div className="flex items-center justify-between mb-2">
              <Label className="text-sm font-semibold">История описаний</Label>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowHistory(false)}
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
            <ScrollArea className="h-40">
              <div className="space-y-2">
                {history.map((item) => (
                  <div
                    key={item.id}
                    className="p-2 bg-card rounded border cursor-pointer hover:bg-muted transition-colors"
                    onClick={() => handleUseHistory(item)}
                  >
                    {item.title && (
                      <div className="font-semibold text-sm mb-1">{item.title}</div>
                    )}
                    <div className="text-xs text-muted-foreground line-clamp-2">
                      {item.description}
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">
                      {item.timestamp.toLocaleTimeString('ru-RU')}
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </div>
        )}

        <div>
          <Label htmlFor="scene-title" className="text-sm font-medium mb-2 block">
            Заголовок (необязательно)
          </Label>
          <Input
            id="scene-title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Например: В таверне"
            className="bg-card border-2 border-primary"
          />
        </div>

        <div className="flex-1 flex flex-col min-h-0">
          <Label htmlFor="scene-description" className="text-sm font-medium mb-2 block">
            Описание сцены
          </Label>
          <Textarea
            id="scene-description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Опишите сцену для игроков..."
            className="flex-1 bg-card border-2 border-primary font-serif resize-none"
            rows={8}
          />
        </div>

        <div>
          <Label className="text-sm font-medium mb-2 block">Быстрые фразы</Label>
          <div className="flex flex-wrap gap-2">
            {QUICK_PHRASES.map((phrase, idx) => (
              <Button
                key={idx}
                variant="outline"
                size="sm"
                onClick={() => handleQuickPhrase(phrase)}
                className="text-xs"
              >
                {phrase}
              </Button>
            ))}
          </div>
        </div>

        <Button
          onClick={handleSend}
          disabled={!description.trim() || isSending}
          className="w-full"
          size="lg"
        >
          <Send className="w-4 h-4 mr-2" />
          {isSending ? 'Отправка...' : 'Отправить описание'}
        </Button>
      </CardContent>
    </Card>
  );
}

