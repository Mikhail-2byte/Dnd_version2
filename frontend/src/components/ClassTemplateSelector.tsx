import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Sword, Wand2, Dagger, Shield, Bow } from 'lucide-react';
import type { CharacterTemplate } from '../types/character';

interface ClassTemplateSelectorProps {
  templates: Record<string, CharacterTemplate>;
  selectedTemplate: string | null;
  onSelect: (templateKey: string) => void;
}

const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  sword: Sword,
  wand: Wand2,
  dagger: Dagger,
  shield: Shield,
  bow: Bow,
};

export default function ClassTemplateSelector({
  templates,
  selectedTemplate,
  onSelect,
}: ClassTemplateSelectorProps) {
  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-semibold mb-2">Выберите класс персонажа</h3>
        <p className="text-sm text-muted-foreground mb-4">
          Выберите класс, чтобы автоматически заполнить характеристики и снаряжение
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Object.entries(templates).map(([key, template]) => {
          const IconComponent = iconMap[template.icon] || Sword;
          const isSelected = selectedTemplate === key;
          
          return (
            <Card
              key={key}
              className={`cursor-pointer transition-all hover:shadow-lg ${
                isSelected ? 'ring-2 ring-primary border-primary' : ''
              }`}
              onClick={() => onSelect(key)}
            >
              <CardContent className="p-4">
                <div className="flex items-start gap-3">
                  <div className={`p-2 rounded-lg ${
                    isSelected ? 'bg-primary text-primary-foreground' : 'bg-muted'
                  }`}>
                    <IconComponent className="w-6 h-6" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-lg">{template.class}</h4>
                    <p className="text-sm text-muted-foreground mt-1">
                      {template.description}
                    </p>
                    <div className="mt-3 flex flex-wrap gap-1">
                      {template.starting_equipment.slice(0, 3).map((item, idx) => (
                        <span
                          key={idx}
                          className="text-xs px-2 py-1 bg-secondary rounded"
                        >
                          {item}
                        </span>
                      ))}
                      {template.starting_equipment.length > 3 && (
                        <span className="text-xs px-2 py-1 bg-secondary rounded">
                          +{template.starting_equipment.length - 3}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
      
      {selectedTemplate && (
        <div className="mt-4 p-4 bg-primary/10 rounded-lg border border-primary/20">
          <p className="text-sm text-muted-foreground">
            Выбран: <span className="font-semibold text-foreground">
              {templates[selectedTemplate]?.class}
            </span>
          </p>
        </div>
      )}
    </div>
  );
}

