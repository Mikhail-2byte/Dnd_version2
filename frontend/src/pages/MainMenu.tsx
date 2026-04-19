import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { gamesAPI } from '../services/api';
import { useToast } from '../hooks/use-toast';
import { Header } from '../components/Header';
import { Button } from '../components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '../components/ui/alert';
import { Input } from '../components/ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../components/ui/dialog';
import { Switch } from '../components/ui/switch';
import { Label } from '../components/ui/label';
import { AlertCircle, Gamepad2, Users, Settings } from 'lucide-react';

export default function MainMenu() {
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [showJoinModal, setShowJoinModal] = useState(false);
  const [inviteCode, setInviteCode] = useState('');
  const [error, setError] = useState('');
  const [joinAsSpectator, setJoinAsSpectator] = useState(false);

  const handleJoinGame = async (inviteCode: string, asSpectator: boolean = false) => {
    try {
      setError('');
      const game = await gamesAPI.getByInviteCode(inviteCode);
      
      if (asSpectator) {
        await gamesAPI.spectate(game.id);
        toast({
          title: 'Подключено как наблюдатель!',
          description: `Вы присоединились к игре "${game.name}" как наблюдатель`,
        });
      } else {
        await gamesAPI.join(game.id);
        toast({
          title: 'Подключено!',
          description: `Вы присоединились к игре "${game.name}"`,
        });
      }
      
      navigate(`/game/${game.id}/lobby`);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Ошибка подключения к игре';
      setError(errorMessage);
      toast({
        title: 'Ошибка',
        description: errorMessage,
        variant: 'destructive',
      });
    }
  };

  const handleJoinClick = async () => {
    if (!inviteCode.trim()) {
      setError('Введите invite-код');
      return;
    }
    await handleJoinGame(inviteCode, joinAsSpectator);
    setShowJoinModal(false);
    setInviteCode('');
    setJoinAsSpectator(false);
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
      {/* Overlay для затемнения фона и улучшения читаемости */}
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>
      
      <div className="relative z-10 flex flex-col flex-1">
        <Header />
        
        <main className="flex-1 flex items-center justify-center p-8">
          <div className="max-w-md w-full mx-auto">
            {error && (
              <Alert variant="destructive" className="mb-6">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Ошибка</AlertTitle>
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <div className="mb-8 text-center">
              <h2 className="text-3xl font-bold text-foreground mb-2">
                Добро пожаловать, <span className="text-accent gold-glow">{user?.username}</span>!
              </h2>
              <p className="text-muted-foreground">Выберите действие для начала приключения</p>
            </div>

            {/* Кнопки в столбик */}
            <div className="flex flex-col gap-4">
              <Button
                onClick={() => navigate('/create-game')}
                variant="ghost"
                className="w-full text-lg py-6 border-2 border-accent/50 hover:border-accent hover:bg-accent/10 text-foreground font-semibold"
              >
                <Gamepad2 className="w-5 h-5 mr-3" />
                Создать игру
              </Button>

              <Button
                onClick={() => setShowJoinModal(true)}
                variant="ghost"
                className="w-full text-lg py-6 border-2 border-accent/50 hover:border-accent hover:bg-accent/10 text-foreground font-semibold"
              >
                <Users className="w-5 h-5 mr-3" />
                Присоединиться
              </Button>

              <Button
                onClick={() => navigate('/settings')}
                variant="ghost"
                className="w-full text-lg py-6 border-2 border-accent/50 hover:border-accent hover:bg-accent/10 text-foreground font-semibold"
              >
                <Settings className="w-5 h-5 mr-3" />
                Настройки
              </Button>

            </div>

            <Dialog open={showJoinModal} onOpenChange={setShowJoinModal}>
              <DialogContent className="bg-card border-2 border-border">
                <DialogHeader>
                  <DialogTitle>Присоединиться к игре</DialogTitle>
                  <DialogDescription>
                    Введите invite-код для подключения к существующей игре
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 mt-4">
                  {error && (
                    <Alert variant="destructive">
                      <AlertCircle className="h-4 w-4" />
                      <AlertDescription>{error}</AlertDescription>
                    </Alert>
                  )}
                  <Input
                    type="text"
                    placeholder="Введите invite-код"
                    value={inviteCode}
                    onChange={(e) => {
                      setInviteCode(e.target.value.toUpperCase());
                      setError('');
                    }}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        handleJoinClick();
                      }
                    }}
                    className="uppercase font-mono"
                    maxLength={6}
                  />
                  <div className="flex items-center space-x-2">
                    <Switch
                      id="spectator-mode"
                      checked={joinAsSpectator}
                      onCheckedChange={setJoinAsSpectator}
                    />
                    <Label htmlFor="spectator-mode" className="text-sm cursor-pointer">
                      Присоединиться как наблюдатель
                    </Label>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      onClick={() => {
                        setShowJoinModal(false);
                        setInviteCode('');
                        setError('');
                        setJoinAsSpectator(false);
                      }}
                      variant="outline"
                      className="flex-1"
                    >
                      Отмена
                    </Button>
                    <Button
                      onClick={handleJoinClick}
                      className="flex-1"
                      disabled={!inviteCode.trim()}
                    >
                      Присоединиться
                    </Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </main>
      </div>
    </div>
  );
}

