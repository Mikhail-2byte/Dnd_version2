import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Scroll, ChevronDown, ChevronUp } from 'lucide-react';

interface SceneDescriptionProps {
  description: string;
  title?: string | null;
  isVisible: boolean;
}

export default function SceneDescription({
  description,
  title,
  isVisible,
}: SceneDescriptionProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [shouldShow, setShouldShow] = useState(isVisible);

  useEffect(() => {
    if (isVisible) {
      setShouldShow(true);
    }
  }, [isVisible]);

  if (!shouldShow || !description) {
    return null;
  }

  return (
    <Card
      className={`fixed bottom-4 left-1/2 transform -translate-x-1/2 z-50 w-full max-w-4xl mx-4 border-4 border-primary bg-card/98 backdrop-blur-sm shadow-2xl transition-all duration-500 ${
        isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4 pointer-events-none"
      }`}
    >
      <CardHeader className="pb-3 border-b-2 border-primary">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-xl">
            <Scroll className="w-6 h-6 text-accent" />
            {title || 'Описание сцены'}
          </CardTitle>
          <div className="flex gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsCollapsed(!isCollapsed)}
            >
              {isCollapsed ? (
                <ChevronUp className="w-4 h-4" />
              ) : (
                <ChevronDown className="w-4 h-4" />
              )}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShouldShow(false)}
            >
              Закрыть
            </Button>
          </div>
        </div>
      </CardHeader>
      {!isCollapsed && (
        <CardContent className="pt-6">
          <div className="text-lg font-serif text-foreground leading-relaxed whitespace-pre-wrap">
            {description}
          </div>
        </CardContent>
      )}
    </Card>
  );
}

