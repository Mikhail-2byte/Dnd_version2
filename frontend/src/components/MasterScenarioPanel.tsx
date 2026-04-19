import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { ScrollArea } from './ui/scroll-area';
import { BookOpen } from 'lucide-react';

interface MasterScenarioPanelProps {
  story?: string | null;
  masterScenario?: string[];
}

export default function MasterScenarioPanel({ story, masterScenario }: MasterScenarioPanelProps) {
  const content = masterScenario && masterScenario.length > 0 
    ? masterScenario 
    : story 
      ? [story] 
      : ['Сценарий не загружен'];

  return (
    <Card className="h-full border-2 border-border bg-card/95 backdrop-blur-sm flex flex-col">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <BookOpen className="w-5 h-5 text-accent" />
          Сценарий для мастера
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 overflow-hidden p-0">
        <ScrollArea className="h-full px-6 pb-6">
          <div className="space-y-4 text-sm text-foreground leading-relaxed">
            {masterScenario && masterScenario.length > 0 ? (
              <div className="space-y-4">
                {masterScenario.map((scene, index) => (
                  <div key={index} className="space-y-2">
                    <div className="whitespace-pre-wrap">
                      {scene.split(/\*\*(.*?)\*\*/).map((part, i) => 
                        i % 2 === 1 ? (
                          <strong key={i} className="font-bold text-accent">{part}</strong>
                        ) : (
                          <span key={i}>{part}</span>
                        )
                      )}
                    </div>
                    {index < masterScenario.length - 1 && (
                      <div className="border-t border-border pt-2 mt-2" />
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="whitespace-pre-wrap leading-relaxed">
                {story || 'Сценарий не загружен'}
              </div>
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}

