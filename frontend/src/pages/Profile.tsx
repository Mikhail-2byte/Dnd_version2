import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { Header } from '../components/Header';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Avatar, AvatarFallback, AvatarImage } from '../components/ui/avatar';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../components/ui/tabs';
import { Empty, EmptyHeader, EmptyTitle, EmptyDescription, EmptyMedia } from '../components/ui/empty';
import { authAPI, charactersAPI } from '../services/api';
import { useToast } from '../hooks/use-toast';
import type { UserStats } from '../types/user';
import type { Character } from '../types/character';
import { 
  LogOut, 
  UserCircle, 
  Users, 
  Gamepad2, 
  Crown, 
  BarChart3,
  Swords,
  Shield,
  Loader2
} from 'lucide-react';

export default function Profile() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const [stats, setStats] = useState<UserStats | null>(null);
  const [characters, setCharacters] = useState<Character[]>([]);
  const [isLoadingStats, setIsLoadingStats] = useState(false);
  const [isLoadingCharacters, setIsLoadingCharacters] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  useEffect(() => {
    if (user) {
      loadStats();
      loadCharacters();
    }
  }, [user]);

  const loadStats = async () => {
    setIsLoadingStats(true);
    try {
      const statsData = await authAPI.getStats();
      setStats(statsData);
    } catch (error: any) {
      console.error('Ошибка загрузки статистики:', error);
      toast({
        title: 'Ошибка',
        description: 'Не удалось загрузить статистику',
        variant: 'destructive',
      });
    } finally {
      setIsLoadingStats(false);
    }
  };

  const loadCharacters = async () => {
    setIsLoadingCharacters(true);
    try {
      const charactersData = await charactersAPI.getAll();
      setCharacters(charactersData);
    } catch (error: any) {
      console.error('Ошибка загрузки персонажей:', error);
      toast({
        title: 'Ошибка',
        description: 'Не удалось загрузить персонажей',
        variant: 'destructive',
      });
    } finally {
      setIsLoadingCharacters(false);
    }
  };

  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      logout();
      toast({
        title: 'Выход выполнен',
        description: 'Вы успешно вышли из аккаунта',
      });
      navigate('/welcome');
    } catch (error) {
      console.error('Ошибка выхода:', error);
      toast({
        title: 'Ошибка',
        description: 'Не удалось выйти из аккаунта',
        variant: 'destructive',
      });
    } finally {
      setIsLoggingOut(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const months = [
      'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
      'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'
    ];
    const day = date.getDate();
    const month = months[date.getMonth()];
    const year = date.getFullYear();
    return `${day} ${month} ${year}`;
  };

  const getInitials = (username: string) => {
    return username.substring(0, 2).toUpperCase();
  };

  if (!user) {
    return null;
  }

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
          <Card className="max-w-4xl w-full bg-card/95 backdrop-blur-sm border-2 border-primary/30">
            <CardHeader className="text-center pb-4">
              <CardTitle className="text-3xl font-bold">Профиль</CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="profile" className="w-full">
                <TabsList className="grid w-full grid-cols-3 mb-6">
                  <TabsTrigger value="profile" className="gap-2">
                    <UserCircle className="w-4 h-4" />
                    Профиль
                  </TabsTrigger>
                  <TabsTrigger value="characters" className="gap-2">
                    <Users className="w-4 h-4" />
                    Персонажи
                    {characters.length > 0 && (
                      <Badge variant="secondary" className="ml-1">
                        {characters.length}
                      </Badge>
                    )}
                  </TabsTrigger>
                  <TabsTrigger value="stats" className="gap-2">
                    <BarChart3 className="w-4 h-4" />
                    Статистика
                  </TabsTrigger>
                </TabsList>

                {/* Вкладка Профиль */}
                <TabsContent value="profile" className="space-y-6">
                  {/* Аватар и основная информация */}
                  <div className="flex flex-col items-center gap-4 pb-6 border-b border-border">
                    <Avatar className="w-24 h-24 border-4 border-accent/50">
                      <AvatarImage src="" alt={user.username} />
                      <AvatarFallback className="text-2xl bg-accent/20 text-accent">
                        {getInitials(user.username)}
                      </AvatarFallback>
                    </Avatar>
                    <div className="text-center">
                      <h2 className="text-2xl font-bold text-foreground mb-1">
                        {user.username}
                      </h2>
                      <p className="text-muted-foreground">{user.email}</p>
                    </div>
                  </div>

                  {/* Дополнительная информация */}
                  <div className="space-y-4">
                    <div className="flex justify-between items-center p-4 bg-muted/50 rounded-lg">
                      <span className="text-muted-foreground font-medium">Логин:</span>
                      <span className="text-foreground font-semibold">{user.username}</span>
                    </div>
                    
                    <div className="flex justify-between items-center p-4 bg-muted/50 rounded-lg">
                      <span className="text-muted-foreground font-medium">Email:</span>
                      <span className="text-foreground font-semibold">{user.email}</span>
                    </div>
                    
                    <div className="flex justify-between items-center p-4 bg-muted/50 rounded-lg">
                      <span className="text-muted-foreground font-medium">Дата регистрации:</span>
                      <span className="text-foreground font-semibold">
                        {formatDate(user.created_at)}
                      </span>
                    </div>
                  </div>

                  {/* Кнопка выхода */}
                  <div className="pt-4 border-t border-border">
                    <Button
                      variant="destructive"
                      onClick={handleLogout}
                      disabled={isLoggingOut}
                      className="w-full gap-2"
                    >
                      {isLoggingOut ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin" />
                          Выход...
                        </>
                      ) : (
                        <>
                          <LogOut className="w-4 h-4" />
                          Выйти из аккаунта
                        </>
                      )}
                    </Button>
                  </div>
                </TabsContent>

                {/* Вкладка Персонажи */}
                <TabsContent value="characters" className="space-y-4">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-semibold">Мои персонажи</h3>
                    {characters.length > 0 && (
                      <Badge variant="secondary">
                        Всего: {characters.length}
                      </Badge>
                    )}
                  </div>

                  {isLoadingCharacters ? (
                    <div className="flex items-center justify-center py-12">
                      <Loader2 className="w-8 h-8 animate-spin text-primary" />
                    </div>
                  ) : characters.length === 0 ? (
                    <Empty>
                      <EmptyMedia>
                        <Swords className="w-12 h-12 text-muted-foreground" />
                      </EmptyMedia>
                      <EmptyHeader>
                        <EmptyTitle>Нет персонажей</EmptyTitle>
                        <EmptyDescription>
                          Создайте своего первого персонажа, чтобы начать приключение!
                        </EmptyDescription>
                      </EmptyHeader>
                    </Empty>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {characters.map((character) => (
                        <Card key={character.id} className="bg-muted/30 hover:bg-muted/50 transition-colors">
                          <CardContent className="p-4">
                            <div className="flex items-start justify-between mb-3">
                              <div>
                                <h4 className="font-semibold text-lg">{character.name}</h4>
                                <div className="flex gap-2 mt-1">
                                  <Badge variant="outline">{character.race}</Badge>
                                  <Badge variant="outline">{character.class}</Badge>
                                </div>
                              </div>
                              <Badge variant="secondary" className="text-xs">
                                Ур. {character.level}
                              </Badge>
                            </div>
                            <div className="grid grid-cols-2 gap-2 text-sm text-muted-foreground">
                              <div className="flex items-center gap-1">
                                <Shield className="w-3 h-3" />
                                <span>СИЛ: {character.strength}</span>
                              </div>
                              <div className="flex items-center gap-1">
                                <Shield className="w-3 h-3" />
                                <span>ЛОВ: {character.dexterity}</span>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  )}
                </TabsContent>

                {/* Вкладка Статистика */}
                <TabsContent value="stats" className="space-y-4">
                  <h3 className="text-xl font-semibold mb-4">Статистика игрока</h3>

                  {isLoadingStats ? (
                    <div className="flex items-center justify-center py-12">
                      <Loader2 className="w-8 h-8 animate-spin text-primary" />
                    </div>
                  ) : stats ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {/* Статистика персонажей */}
                      <Card className="bg-muted/30">
                        <CardContent className="p-6">
                          <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center gap-2">
                              <Users className="w-5 h-5 text-accent" />
                              <span className="font-semibold">Персонажи</span>
                            </div>
                            <Badge variant="secondary" className="text-lg px-3 py-1">
                              {stats.characters_count}
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground">
                            Всего созданных персонажей
                          </p>
                        </CardContent>
                      </Card>

                      {/* Статистика игр как мастер */}
                      <Card className="bg-muted/30">
                        <CardContent className="p-6">
                          <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center gap-2">
                              <Crown className="w-5 h-5 text-accent" />
                              <span className="font-semibold">Игр как мастер</span>
                            </div>
                            <Badge variant="secondary" className="text-lg px-3 py-1">
                              {stats.games_as_master_count}
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground">
                            Созданных игровых сессий
                          </p>
                        </CardContent>
                      </Card>

                      {/* Статистика игр как игрок */}
                      <Card className="bg-muted/30">
                        <CardContent className="p-6">
                          <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center gap-2">
                              <Gamepad2 className="w-5 h-5 text-accent" />
                              <span className="font-semibold">Игр как игрок</span>
                            </div>
                            <Badge variant="secondary" className="text-lg px-3 py-1">
                              {stats.games_as_player_count}
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground">
                            Присоединенных игр
                          </p>
                        </CardContent>
                      </Card>

                      {/* Общая статистика игр */}
                      <Card className="bg-muted/30 border-accent/30">
                        <CardContent className="p-6">
                          <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center gap-2">
                              <BarChart3 className="w-5 h-5 text-accent" />
                              <span className="font-semibold">Всего игр</span>
                            </div>
                            <Badge variant="default" className="text-lg px-3 py-1">
                              {stats.total_games_count}
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground">
                            Всего участвовал в играх
                          </p>
                        </CardContent>
                      </Card>
                    </div>
                  ) : (
                    <Empty>
                      <EmptyMedia>
                        <BarChart3 className="w-12 h-12 text-muted-foreground" />
                      </EmptyMedia>
                      <EmptyHeader>
                        <EmptyTitle>Нет данных</EmptyTitle>
                        <EmptyDescription>
                          Не удалось загрузить статистику
                        </EmptyDescription>
                      </EmptyHeader>
                    </Empty>
                  )}
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </main>
      </div>
    </div>
  );
}
