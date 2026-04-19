import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { useGameStore } from '../store/gameStore';
import { gamesAPI, charactersAPI } from '../services/api';
import { socketService, type GameState } from '../services/socket';
import { useToast } from '../hooks/use-toast';
import GameMap from '../components/GameMap';
import MasterScenarioPanel from '../components/MasterScenarioPanel';
import MasterScenePanel from '../components/MasterScenePanel';
import SceneDescription from '../components/SceneDescription';
import CharacterPanel from '../components/CharacterPanel';
import DiceRoller from '../components/DiceRoller';
import CombatPanel from '../components/CombatPanel';
import InventoryPanel from '../components/InventoryPanel';
import SpellbookPanel from '../components/SpellbookPanel';
import BestiaryBrowser from '../components/BestiaryBrowser';
import { Header } from '../components/Header';
import { Card, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../components/ui/tabs';
import { Alert, AlertDescription, AlertTitle } from '../components/ui/alert';
import { AlertCircle } from 'lucide-react';
import type { Character } from '../types/character';
import { gameTemplates } from '../data/gameTemplates';

export default function GameRoom() {
  const { gameId } = useParams<{ gameId: string }>();
  const navigate = useNavigate();
  const { user, token } = useAuthStore();
  const {
    currentGame,
    tokens,
    players,
    currentUserRole,
    setGame,
    setTokens,
    setPlayers,
    setCurrentUserRole,
    reset,
  } = useGameStore();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState<'lobby' | 'characters' | 'dice' | 'combat' | 'inventory' | 'spells' | 'bestiary'>('lobby');
  const [activeCombatId, setActiveCombatId] = useState<string | null>(null);
  const [characters, setCharacters] = useState<Character[]>([]);
  const [selectedCharacterId, setSelectedCharacterId] = useState<string | null>(null);
  const [currentSceneDescription, setCurrentSceneDescription] = useState<{
    description: string;
    title?: string | null;
  } | null>(null);
  const [isSceneVisible, setIsSceneVisible] = useState(false);

  useEffect(() => {
    if (!gameId || !token) {
      console.error('GameRoom: Missing gameId or token', { gameId, token: !!token });
      setError('Отсутствует ID игры или токен авторизации');
      setIsLoading(false);
      return;
    }

    const loadGame = async () => {
      try {
        setIsLoading(true);
        setError('');
        console.log('GameRoom: Loading game', gameId);
        
        const game = await gamesAPI.getInfo(gameId);
        console.log('GameRoom: Game loaded', game);
        setGame(game);

        // Загружаем токены
        const gameTokens = await gamesAPI.getTokens(gameId);
        console.log('GameRoom: Tokens loaded', gameTokens);
        setTokens(gameTokens);

        // Определяем роль сразу после загрузки игры
        if (game.master_id === user?.id) {
          setCurrentUserRole('master');
        } else {
          setCurrentUserRole('player');
        }

        // Загружаем персонажей: сначала из шаблона, если игра создана из шаблона
        try {
          const template = gameTemplates.find(t => t.name === game.name);
          if (template?.characters && template.characters.length > 0) {
            // Используем персонажей из шаблона
            setCharacters(template.characters);
          } else {
            // Иначе загружаем персонажей пользователя
          const userCharacters = await charactersAPI.getAll();
          setCharacters(userCharacters);
          }
        } catch (err) {
          console.error('Failed to load characters:', err);
        }

        // Подключаемся к WebSocket
        console.log('GameRoom: Connecting to WebSocket');
        socketService.connect(token);
        socketService.joinGame(gameId);

        // Настраиваем обработчики событий
        socketService.onGameState((state: GameState) => {
          console.log('GameRoom: Game state received', state);
          setGame(state.game as any);
          setTokens(state.tokens);
          setPlayers(state.players);
          
          // Определяем роль текущего пользователя
          const currentPlayer = state.players.find((p) => p.user_id === user?.id);
          if (currentPlayer) {
            setCurrentUserRole(currentPlayer.role);
          } else if (state.game.id && state.game.master_id === user?.id) {
            setCurrentUserRole('master');
          } else {
            setCurrentUserRole('player');
          }
        });

        socketService.onTokenMoved((data) => {
          useGameStore.getState().updateTokenPosition(data.token_id, data.x, data.y);
        });

        socketService.onTokenCreated((data) => {
          console.log('GameRoom: Token created event received', data);
          const store = useGameStore.getState();
          // Проверяем, есть ли временный токен с таким же именем
          const existingTempToken = store.tokens.find(
            (t) => t.name === data.token.name && t.id.startsWith('temp-')
          );
          if (existingTempToken) {
            // Заменяем временный токен на реальный
            console.log('Replacing temporary token with real one', {
              tempId: existingTempToken.id,
              realId: data.token.id
            });
            store.removeToken(existingTempToken.id);
          }
          store.addToken(data.token);
          console.log('Token added to store, current tokens:', store.tokens.length);
        });

        socketService.onTokenDeleted((data) => {
          console.log('GameRoom: Token deleted event received', data);
          useGameStore.getState().removeToken(data.token_id);
          console.log('Token removed from store, current tokens:', useGameStore.getState().tokens.length);
        });

        socketService.onPlayerJoined((data) => {
          toast({
            title: 'Новый игрок',
            description: `${data.username} присоединился к игре`,
          });
        });

        socketService.onDiceRolled((data) => {
          // Обработка броска кубиков будет в DiceRoller компоненте
          console.log('Dice rolled:', data);
        });

        socketService.onSceneDescription((data) => {
          if (data.game_id === gameId) {
            setCurrentSceneDescription({
              description: data.description,
              title: data.title,
            });
            setIsSceneVisible(true);
          }
        });

        socketService.onError((data) => {
          console.error('GameRoom: WebSocket error', data);
          setError(data.message);
          toast({
            title: 'Ошибка WebSocket',
            description: data.message,
            variant: 'destructive',
          });
        });

        setIsLoading(false);
      } catch (err: any) {
        console.error('GameRoom: Error loading game', err);
        const errorMessage = err.response?.data?.detail || err.message || 'Ошибка загрузки игры';
        setError(errorMessage);
        setIsLoading(false);
      }
    };

    loadGame();

    return () => {
      console.log('GameRoom: Cleaning up', { gameId, hasToken: !!token, userId: user?.id });
      // Отключаемся только при размонтировании компонента или смене игры
      // Не отключаемся при изменении других зависимостей
      socketService.disconnect();
      reset();
    };
  }, [gameId, token, user?.id]);

  const handleLeave = () => {
    socketService.disconnect();
    reset();
    toast({
      title: 'Вы покинули игру',
      description: 'Вы успешно покинули игровую сессию',
    });
    navigate('/');
  };

  // Фон для состояний загрузки/ошибки
  const defaultMapUrl = '/assets/images/default-map.jpg';
  const loadingBackgroundStyle = {
    backgroundImage: `url(${defaultMapUrl})`,
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    backgroundAttachment: 'fixed',
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col relative" style={loadingBackgroundStyle}>
        <div className="absolute inset-0 bg-black/30 backdrop-blur-[2px] pointer-events-none"></div>
        <div className="relative z-10 flex flex-col flex-1">
        <Header />
        <div className="flex-1 flex items-center justify-center">
          <Card className="border-2 border-primary bg-card/95 backdrop-blur-sm">
            <CardContent className="p-6">
              <p className="text-muted-foreground">Загрузка игры...</p>
            </CardContent>
          </Card>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex flex-col relative" style={loadingBackgroundStyle}>
        <div className="absolute inset-0 bg-black/30 backdrop-blur-[2px] pointer-events-none"></div>
        <div className="relative z-10 flex flex-col flex-1">
        <Header />
        <div className="flex-1 flex items-center justify-center p-4">
          <Card className="border-2 border-destructive bg-card/95 backdrop-blur-sm max-w-md w-full">
            <CardContent className="p-6">
              <Alert variant="destructive" className="mb-4">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Ошибка</AlertTitle>
                <AlertDescription>{error}</AlertDescription>
              </Alert>
              <Button onClick={() => navigate('/')} variant="outline" className="w-full">
                Вернуться в главное меню
              </Button>
            </CardContent>
          </Card>
          </div>
        </div>
      </div>
    );
  }

  if (!currentGame) {
    return (
      <div className="min-h-screen flex flex-col relative" style={loadingBackgroundStyle}>
        <div className="absolute inset-0 bg-black/30 backdrop-blur-[2px] pointer-events-none"></div>
        <div className="relative z-10 flex flex-col flex-1">
        <Header />
        <div className="flex-1 flex items-center justify-center p-4">
          <Card className="border-2 border-primary bg-card/95 backdrop-blur-sm max-w-md w-full">
            <CardContent className="p-6">
              <p className="text-muted-foreground mb-4">Игра не загружена</p>
              <Button onClick={() => navigate('/')} variant="outline" className="w-full">
                Вернуться в главное меню
              </Button>
            </CardContent>
          </Card>
          </div>
        </div>
      </div>
    );
  }

  // Получаем информацию о шаблоне для сценария мастера
  const template = gameTemplates.find(t => t.name === currentGame.name);
  
  // Получаем URL карты для фона
  const mapUrl = currentGame?.map_url || '/assets/images/default-map.jpg';
  const pageBackgroundStyle = {
    backgroundImage: `url(${mapUrl})`,
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    backgroundAttachment: 'fixed',
  };

  return (
    <div className="min-h-screen flex flex-col relative overflow-hidden" style={pageBackgroundStyle}>
      {/* Overlay для улучшения читаемости */}
      <div className="absolute inset-0 bg-black/30 backdrop-blur-[2px] pointer-events-none"></div>
      
      <div className="relative z-10 flex flex-col flex-1 overflow-hidden">
        <Header />
      
         <main className="flex-1 flex gap-4 w-full pl-0 items-end">
         {/* Left Sidebar - Сценарий для мастера */}
         {currentUserRole === 'master' && (
           <div className="w-96 flex-shrink-0 h-[calc(100vh-6rem)]">
             <MasterScenarioPanel 
               story={currentGame.story} 
               masterScenario={template?.masterScenario}
             />
           </div>
         )}

        {/* Main Content Area */}
         <div className="flex-1 flex flex-col min-w-0 pr-4 pb-4 h-[calc(100vh-6rem)]">
          <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as any)} className="flex-1 flex flex-col min-h-0">
            <TabsList className="w-fit mb-2 flex-shrink-0 flex-wrap">
              <TabsTrigger value="lobby">Карта</TabsTrigger>
              <TabsTrigger value="characters">Персонажи</TabsTrigger>
              <TabsTrigger value="dice">Кубики</TabsTrigger>
              <TabsTrigger value="combat">Бой</TabsTrigger>
              <TabsTrigger value="inventory" disabled={!selectedCharacterId}>Инвентарь</TabsTrigger>
              <TabsTrigger value="spells" disabled={!selectedCharacterId}>Заклинания</TabsTrigger>
              {currentUserRole === 'master' && <TabsTrigger value="bestiary">Бестиарий</TabsTrigger>}
            </TabsList>
            
            <TabsContent value="lobby" className="relative w-full flex-1 min-h-0 overflow-hidden">
              <GameMap 
                gameId={gameId!} 
                onCharacterSelect={setSelectedCharacterId}
                characters={characters}
              />
              {currentUserRole === 'master' && (
                <div className="absolute top-4 right-4 w-80 z-10 max-h-[calc(100vh-8rem)]">
                  <MasterScenePanel gameId={gameId!} />
                </div>
              )}
              {currentUserRole !== 'master' && currentSceneDescription && (
                <SceneDescription
                  description={currentSceneDescription.description}
                  title={currentSceneDescription.title}
                  isVisible={isSceneVisible}
                />
              )}
            </TabsContent>
            
            <TabsContent value="characters" className="flex-1 mt-0">
              <CharacterPanel
                characters={characters}
                selectedId={selectedCharacterId}
                onSelect={(character) => setSelectedCharacterId(character.id)}
              />
            </TabsContent>
        
            <TabsContent value="dice" className="flex-1 mt-0">
              <div className="flex justify-center items-start h-full">
          <DiceRoller
            gameId={gameId!}
            selectedCharacterId={selectedCharacterId}
            onRoll={(count, faces, rollType, modifier, advantage) => {
              socketService.rollDice(gameId!, count, faces, rollType, modifier, advantage);
            }}
          />
              </div>
            </TabsContent>
            
            <TabsContent value="combat" className="flex-1 mt-0">
              <div className="flex justify-center items-start h-full">
                <CombatPanel
                  gameId={gameId!}
                  isMaster={currentUserRole === 'master'}
                  onCombatChange={setActiveCombatId}
                />
              </div>
            </TabsContent>

            <TabsContent value="inventory" className="flex-1 mt-0">
              {selectedCharacterId ? (
                <InventoryPanel characterId={selectedCharacterId} />
              ) : (
                <p className="text-muted-foreground text-center py-8">Выберите персонажа</p>
              )}
            </TabsContent>

            <TabsContent value="spells" className="flex-1 mt-0">
              {selectedCharacterId ? (
                <SpellbookPanel
                  characterId={selectedCharacterId}
                  characterClass={characters.find(c => c.id === selectedCharacterId)?.class ?? ''}
                />
              ) : (
                <p className="text-muted-foreground text-center py-8">Выберите персонажа</p>
              )}
            </TabsContent>

            {currentUserRole === 'master' && (
              <TabsContent value="bestiary" className="flex-1 mt-0">
                <BestiaryBrowser gameId={gameId!} combatId={activeCombatId} />
              </TabsContent>
            )}
          </Tabs>
        </div>
      </main>
      </div>
    </div>
  );
}

