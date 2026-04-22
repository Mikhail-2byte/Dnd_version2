import { useRef, useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { ScrollArea } from './ui/scroll-area';
import { Tabs, TabsList, TabsTrigger, TabsContent } from './ui/tabs';
import { Send, Scroll, MessageSquare } from 'lucide-react';
import type { LogEvent, ChatMessage } from '../types/game';

const EVENT_ICONS: Record<LogEvent['type'], string> = {
  attack:    '⚔️',
  damage:    '💥',
  heal:      '💚',
  death:     '💀',
  condition: '🔮',
  scene:     '📜',
  roll:      '🎲',
  system:    'ℹ️',
};

interface GameLogProps {
  events: LogEvent[];
  messages: ChatMessage[];
  onSendMessage: (text: string, isOOC: boolean) => void;
}

export default function GameLog({ events, messages, onSendMessage }: GameLogProps) {
  const [input, setInput] = useState('');
  const [isOOC, setIsOOC] = useState(false);
  const logEndRef = useRef<HTMLDivElement>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [events]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    const text = input.trim();
    if (!text) return;
    onSendMessage(text, isOOC);
    setInput('');
  };

  const formatTime = (iso: string) => {
    try {
      return new Date(iso).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
    } catch {
      return '';
    }
  };

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-2">
        <CardTitle className="text-base flex items-center gap-2">
          <Scroll className="h-4 w-4" />
          Лог игры
        </CardTitle>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col overflow-hidden p-3">
        <Tabs defaultValue="log" className="flex-1 flex flex-col min-h-0">
          <TabsList className="mb-2 w-fit">
            <TabsTrigger value="log" className="flex items-center gap-1">
              <Scroll className="h-3 w-3" />
              События
            </TabsTrigger>
            <TabsTrigger value="chat" className="flex items-center gap-1">
              <MessageSquare className="h-3 w-3" />
              Чат
            </TabsTrigger>
          </TabsList>

          {/* Log tab */}
          <TabsContent value="log" className="flex-1 overflow-hidden mt-0">
            <ScrollArea className="h-full">
              <div className="space-y-1 pr-2">
                {events.length === 0 ? (
                  <p className="text-xs text-muted-foreground text-center py-6">
                    События появятся здесь во время игры
                  </p>
                ) : (
                  events.map((ev) => (
                    <div
                      key={ev.id}
                      className={`flex gap-2 text-xs rounded px-2 py-1 ${
                        ev.isCritical
                          ? 'bg-yellow-500/15 border border-yellow-500/40'
                          : 'hover:bg-muted/30'
                      }`}
                    >
                      <span className="shrink-0 w-5 text-center">{EVENT_ICONS[ev.type]}</span>
                      <span className={`flex-1 ${ev.isCritical ? 'text-yellow-400 font-medium' : 'text-foreground/90'}`}>
                        {ev.message}
                      </span>
                      <span className="shrink-0 text-muted-foreground tabular-nums">
                        {formatTime(ev.timestamp)}
                      </span>
                    </div>
                  ))
                )}
                <div ref={logEndRef} />
              </div>
            </ScrollArea>
          </TabsContent>

          {/* Chat tab */}
          <TabsContent value="chat" className="flex-1 flex flex-col overflow-hidden mt-0 min-h-0">
            <ScrollArea className="flex-1">
              <div className="space-y-1.5 pr-2">
                {messages.length === 0 ? (
                  <p className="text-xs text-muted-foreground text-center py-6">
                    Напишите что-нибудь...
                  </p>
                ) : (
                  messages.map((msg) => (
                    <div key={msg.id} className="text-xs">
                      <span className="text-muted-foreground tabular-nums mr-1">
                        {formatTime(msg.timestamp)}
                      </span>
                      <span className={`font-medium mr-1 ${msg.isOOC ? 'text-muted-foreground' : 'text-primary'}`}>
                        {msg.isOOC ? '[OOC]' : ''} {msg.userName}:
                      </span>
                      <span className={msg.isOOC ? 'text-muted-foreground italic' : 'text-foreground'}>
                        {msg.message}
                      </span>
                    </div>
                  ))
                )}
                <div ref={chatEndRef} />
              </div>
            </ScrollArea>

            {/* Chat input */}
            <div className="flex gap-2 mt-2 pt-2 border-t border-border">
              <Button
                size="sm"
                variant={isOOC ? 'secondary' : 'outline'}
                className="text-xs px-2 shrink-0"
                onClick={() => setIsOOC(v => !v)}
                title="Переключить IC/OOC"
              >
                {isOOC ? 'OOC' : 'IC'}
              </Button>
              <Input
                className="flex-1 h-8 text-xs"
                placeholder={isOOC ? 'Вне персонажа...' : 'В роли персонажа...'}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter') handleSend(); }}
                maxLength={1000}
              />
              <Button size="sm" variant="default" className="h-8 px-2" onClick={handleSend} disabled={!input.trim()}>
                <Send className="h-3.5 w-3.5" />
              </Button>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
