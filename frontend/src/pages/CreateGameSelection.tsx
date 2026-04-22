import { useNavigate } from 'react-router-dom';
import { Header } from '../components/Header';
import GameTemplateList from '../components/GameTemplateList';
import { Button } from '../components/ui/button';
import { gameTemplates } from '../data/gameTemplates';
import type { GameTemplate } from '../types/gameTemplate';
import { gamesAPI } from '../services/api';
import { useToast } from '../hooks/use-toast';
import { useState } from 'react';
import { Plus, ArrowLeft, BookOpen } from 'lucide-react';

export default function CreateGameSelection() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState<string | null>(null);

  const handleSelectTemplate = async (template: GameTemplate) => {
    try {
      setIsLoading(template.id);
      const game = await gamesAPI.create(template.name, template.story, template.mapUrl);
      toast({
        title: 'Игра создана!',
        description: `Игра "${template.name}" успешно создана из шаблона`,
      });
      navigate(`/game/${game.id}/lobby`);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Ошибка создания игры';
      toast({
        title: 'Ошибка',
        description: errorMessage,
        variant: 'destructive',
      });
    } finally {
      setIsLoading(null);
    }
  };

  return (
    <div
      className="min-h-screen flex flex-col relative overflow-hidden"
      style={{
        backgroundImage: 'url(/assets/backgrounds/background2.png)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
      }}
    >
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>

      <div className="relative z-10 flex flex-col flex-1">
        <Header />

        <main className="flex-1 p-8 overflow-y-auto">
          <div className="max-w-7xl mx-auto">
            <div className="mb-6 flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => navigate('/')}
                  className="hover:bg-accent/10"
                >
                  <ArrowLeft className="w-5 h-5" />
                </Button>
                <div>
                  <h1 className="text-3xl font-bold text-foreground mb-2">
                    Выберите шаблон игры
                  </h1>
                  <p className="text-muted-foreground">
                    Выберите готовый шаблон или создайте свою игру с нуля
                  </p>
                </div>
              </div>
              <div className="flex gap-2">
                <Button
                  onClick={() => navigate('/scenarios')}
                  variant="outline"
                  className="gap-2"
                  size="lg"
                >
                  <BookOpen className="w-5 h-5" />
                  Мои сценарии
                </Button>
                <Button
                  onClick={() => navigate('/create-game/new')}
                  className="gap-2"
                  size="lg"
                >
                  <Plus className="w-5 h-5" />
                  Создать новую игру
                </Button>
              </div>
            </div>

            <div className="relative">
              {isLoading && (
                <div className="absolute inset-0 bg-black/20 backdrop-blur-sm rounded-lg z-10 flex items-center justify-center">
                  <div className="text-center">
                    <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                    <p className="text-foreground">Создание игры...</p>
                  </div>
                </div>
              )}
              <GameTemplateList
                templates={gameTemplates}
                onSelectTemplate={handleSelectTemplate}
              />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

