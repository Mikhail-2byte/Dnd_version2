import GameTemplateCard from './GameTemplateCard';
import type { GameTemplate } from '../types/gameTemplate';

interface GameTemplateListProps {
  templates: GameTemplate[];
  onSelectTemplate: (template: GameTemplate) => void;
}

export default function GameTemplateList({ templates, onSelectTemplate }: GameTemplateListProps) {
  if (templates.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Нет доступных шаблонов игр</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {templates.map((template) => (
        <GameTemplateCard
          key={template.id}
          template={template}
          onSelect={onSelectTemplate}
        />
      ))}
    </div>
  );
}

