import { useNavigate } from 'react-router-dom';
import { Header } from '../components/Header';
import CreateGameForm from '../components/CreateGameForm';
import { gamesAPI } from '../services/api';
import { useToast } from '../hooks/use-toast';
import { useState } from 'react';
import { ArrowLeft } from 'lucide-react';
import { Button } from '../components/ui/button';

export default function CreateGameNew() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (data: { name: string; story?: string; mapFile?: File }) => {
    setIsLoading(true);
    try {
      // Если есть файл карты, используем placeholder или можно загрузить на сервер позже
      // Для простого рабочего варианта используем placeholder
      let mapUrl: string | undefined;
      if (data.mapFile) {
        // В простом варианте можно использовать дефолтную карту или загрузить позже
        // Для полноценной реализации нужен endpoint загрузки файлов
        mapUrl = '/assets/images/default-map.jpg';
      }

      const game = await gamesAPI.create(data.name, data.story, mapUrl);
      toast({
        title: 'Игра создана!',
        description: `Игра "${data.name}" успешно создана`,
      });
      navigate(`/game/${game.id}/lobby`);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Ошибка создания игры';
      toast({
        title: 'Ошибка',
        description: errorMessage,
        variant: 'destructive',
      });
      throw err;
    } finally {
      setIsLoading(false);
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
          <div className="max-w-3xl mx-auto">
            <div className="mb-6 flex items-center gap-4">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => navigate('/create-game')}
                className="hover:bg-accent/10"
              >
                <ArrowLeft className="w-5 h-5" />
              </Button>
              <div>
                <h1 className="text-3xl font-bold text-foreground mb-2">
                  Создать новую игру
                </h1>
                <p className="text-muted-foreground">
                  Заполните информацию о вашей игре
                </p>
              </div>
            </div>

            <div className="bg-card/90 backdrop-blur-sm rounded-xl border-2 border-border p-6 shadow-lg">
              <CreateGameForm
                onSubmit={handleSubmit}
                onCancel={() => navigate('/create-game')}
                isLoading={isLoading}
              />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

