import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Swords } from 'lucide-react';

export default function Welcome() {
  const navigate = useNavigate();

  const handleStartGame = () => {
    navigate('/auth');
  };

  return (
    <div 
      className="min-h-screen flex items-center justify-center relative overflow-hidden"
      style={{
        backgroundImage: 'url(/assets/backgrounds/background2.png)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
      }}
    >
      {/* Overlay для затемнения фона и улучшения читаемости */}
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>
      
      {/* Контент */}
      <div className="relative z-10 text-center px-4 max-w-2xl mx-auto">
        <div className="mb-8">
          <div className="flex items-center justify-center gap-3 mb-6">
            <div className="w-16 h-16 rounded-lg wood-frame flex items-center justify-center bg-accent/20">
              <Swords className="w-10 h-10 text-accent" />
            </div>
            <h1 className="text-5xl md:text-6xl font-bold text-foreground tracking-tight">
              D&D <span className="text-accent gold-glow">Tavern</span>
            </h1>
          </div>
          <p className="text-xl md:text-2xl text-muted-foreground mb-2">
            Добро пожаловать в мир приключений!
          </p>
          <p className="text-lg text-muted-foreground/80">
            Создавайте персонажей, собирайте друзей и отправляйтесь в незабываемые путешествия
          </p>
        </div>

        <Button
          onClick={handleStartGame}
          size="lg"
          className="text-lg px-8 py-6 bg-accent hover:bg-accent/90 text-accent-foreground font-semibold shadow-lg hover:shadow-xl transition-all"
        >
          Начать игру
        </Button>
      </div>
    </div>
  );
}

