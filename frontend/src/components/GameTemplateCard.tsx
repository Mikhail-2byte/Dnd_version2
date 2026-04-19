import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import type { GameTemplate } from '../types/gameTemplate';
import { MapPin } from 'lucide-react';

interface GameTemplateCardProps {
  template: GameTemplate;
  onSelect: (template: GameTemplate) => void;
}

export default function GameTemplateCard({ template, onSelect }: GameTemplateCardProps) {
  return (
    <Card className="flex flex-col h-full hover:shadow-lg transition-shadow duration-300 cursor-pointer group">
      <div className="relative w-full h-48 overflow-hidden rounded-t-xl">
        <img
          src={template.previewImage}
          alt={template.name}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          onError={(e) => {
            const target = e.target as HTMLImageElement;
            target.src = '/placeholder.jpg';
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
      </div>
      
      <CardHeader>
        <CardTitle className="text-xl">{template.name}</CardTitle>
        <CardDescription className="line-clamp-3">
          {template.description}
        </CardDescription>
      </CardHeader>
      
      <CardContent className="flex-1">
        {template.mapUrl && (
          <div className="flex items-center text-sm text-muted-foreground mb-2">
            <MapPin className="w-4 h-4 mr-1" />
            <span>Карта включена</span>
          </div>
        )}
      </CardContent>
      
      <CardFooter>
        <Button
          onClick={() => onSelect(template)}
          className="w-full"
          variant="default"
        >
          Выбрать этот шаблон
        </Button>
      </CardFooter>
    </Card>
  );
}

