import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { useGameStore } from '../store/gameStore';
import { gamesAPI, charactersAPI } from '../services/api';
import { socketService } from '../services/socket';
import { useToast } from '../hooks/use-toast';
import { Header } from '../components/Header';
import PlayerList from '../components/PlayerList';
import CharacterPanel from '../components/CharacterPanel';
import { Card, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '../components/ui/alert';
import { AlertCircle, Play, Loader2, Copy, Check } from 'lucide-react';
import type { Character } from '../types/character';
import type { Participant } from '../types/game';
import { gameTemplates } from '../data/gameTemplates';
import { isTemplateCharacter } from '../utils/uuid';

export default function GameLobby() {
  const { gameId } = useParams<{ gameId: string }>();
  const navigate = useNavigate();
  const { user, token } = useAuthStore();
  const {
    currentGame,
    participants,
    currentUserRole,
    selectedCharacterId,
    isReady,
    setGame,
    setParticipants,
    setCurrentUserRole,
    setSelectedCharacterId,
    setIsReady,
    updateParticipantReady,
    updateParticipantCharacter,
    updateParticipantRole,
    reset,
  } = useGameStore();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [characters, setCharacters] = useState<Character[]>([]);
  const [isSettingReady, setIsSettingReady] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopyInviteCode = () => {
    if (!currentGame?.invite_code) return;
    navigator.clipboard.writeText(currentGame.invite_code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  

  useEffect(() => {
    if (!gameId || !token) {
      console.error('GameLobby: Missing gameId or token', { gameId, token: !!token });
      setError('Отсутствует ID игры или токен авторизации');
      setIsLoading(false);
      return;
    }

    const loadLobby = async () => {
      try {
        setIsLoading(true);
        setError('');
        console.log('GameLobby: Loading game', gameId);
        
        // Загружаем информацию об игре
        const game = await gamesAPI.getInfo(gameId);
        console.log('GameLobby: Game loaded', game);
        setGame(game);

        // Загружаем участников
        const participantsData = await gamesAPI.getParticipants(gameId);
        console.log('GameLobby: Participants loaded', participantsData);
        setParticipants(participantsData as Participant[]);

        // Находим текущего участника и определяем роль
        const currentParticipant = participantsData.find((p) => p.user_id === user?.id);
        if (currentParticipant) {
          // Устанавливаем роль на основе данных участника
          if (currentParticipant.role === 'master') {
            setCurrentUserRole('master');
          } else if (currentParticipant.role === 'spectator') {
            setCurrentUserRole('spectator');
          } else {
            setCurrentUserRole('player');
          }
          
          setIsReady(currentParticipant.is_ready);
          if (currentParticipant.character_id) {
            setSelectedCharacterId(currentParticipant.character_id);
          }
        } else {
          // Если не участник, проверяем, может быть мастер (старая логика для совместимости)
          if (game.master_id === user?.id) {
            setCurrentUserRole('master');
          } else {
            setCurrentUserRole('player');
          }
        }

        // Загружаем персонажей: сначала из шаблона, если игра создана из шаблона
        try {
          const template = gameTemplates.find(t => t.name === game.name);
          if (template?.characters && template.characters.length > 0) {
            // Используем персонажей из шаблона
            setCharacters(template.characters as Character[]);
          } else {
            // Иначе загружаем персонажей пользователя
            const userCharacters = await charactersAPI.getAll();
            setCharacters(userCharacters);
          }
        } catch (err) {
          console.error('Failed to load characters:', err);
        }

        // Подключаемся к WebSocket только если еще не подключены
        console.log('GameLobby: Connecting to WebSocket');
        if (!socketService.isConnected()) {
          socketService.connect(token);
        }
        socketService.joinGame(gameId);

        // Настраиваем обработчики событий только один раз
        // Очищаем старые обработчики перед регистрацией новых
        socketService.off('participant:ready_changed');
        socketService.off('participant:character_changed');
        socketService.off('player:joined');
        socketService.off('player:left');
        socketService.off('master:transferred');
        socketService.off('error');
        
        socketService.onParticipantReadyChanged((data) => {
          console.log('GameLobby: Participant ready changed', data);
          updateParticipantReady(data.user_id, data.is_ready);
          
          // Если это текущий пользователь, обновляем локальный статус
          if (data.user_id === user?.id) {
            setIsReady(data.is_ready);
          }

          if (data.user_id !== user?.id) {
            toast({
              title: data.is_ready ? 'Игрок готов' : 'Игрок не готов',
              description: `${data.username} ${data.is_ready ? 'готов к игре' : 'больше не готов'}`,
            });
          }
        });

        socketService.onParticipantCharacterChanged((data) => {
          console.log('GameLobby: Participant character changed', data);
          updateParticipantCharacter(data.user_id, data.character_id || null);
          
          // Если это текущий пользователь, обновляем локальное состояние
          if (data.user_id === user?.id) {
            setSelectedCharacterId(data.character_id || null);
          }
          
          if (data.user_id !== user?.id) {
            toast({
              title: 'Персонаж выбран',
              description: `${data.username} выбрал персонажа`,
            });
          }
        });

        socketService.onPlayerJoined((data) => {
          toast({
            title: 'Новый игрок',
            description: `${data.username} присоединился к игре`,
          });
          // Обновляем список участников через API только при присоединении нового игрока
          gamesAPI.getParticipants(gameId).then(setParticipants).catch(console.error);
        });

        socketService.onPlayerLeft((data) => {
          toast({
            title: 'Игрок покинул игру',
            description: `Игрок покинул игру`,
          });
          gamesAPI.getParticipants(gameId).then(setParticipants).catch(console.error);
        });

        socketService.onMasterTransferred((data) => {
          console.log('GameLobby: Master transferred', data);
          // Обновляем роли участников
          updateParticipantRole(data.old_master_id, 'player');
          updateParticipantRole(data.new_master_id, 'master');
          
          // Обновляем роль текущего пользователя, если он участвовал в смене
          if (data.old_master_id === user?.id) {
            setCurrentUserRole('player');
            toast({
              title: 'Роль передана',
              description: 'Вы больше не являетесь мастером',
            });
          } else if (data.new_master_id === user?.id) {
            setCurrentUserRole('master');
            toast({
              title: 'Вы стали мастером',
              description: 'Роль мастера передана вам',
            });
          }
          
          // Обновляем список участников
          gamesAPI.getParticipants(gameId).then(setParticipants).catch(console.error);
          
          // Обновляем информацию об игре
          gamesAPI.getInfo(gameId).then(setGame).catch(console.error);
        });

        socketService.onError((data) => {
          console.error('GameLobby: WebSocket error', data);
          setError(data.message);
          toast({
            title: 'Ошибка WebSocket',
            description: data.message,
            variant: 'destructive',
          });
        });

        socketService.onGameStarted((data) => {
          navigate(`/game/${data.game_id}`);
        });

        // Поллинг статуса как надёжный fallback (раз в 2 секунды)
        const pollInterval = setInterval(async () => {
          try {
            const status = await gamesAPI.getStatus(gameId);
            if (status.started) {
              clearInterval(pollInterval);
              navigate(`/game/${gameId}`);
            }
          } catch {
            // игнорируем ошибки поллинга
          }
        }, 2000);

        // Сохраняем ссылку на интервал для очистки
        (window as any).__lobbyPollInterval = pollInterval;

        setIsLoading(false);
      } catch (err: any) {
        console.error('GameLobby: Error loading lobby', err);
        const errorMessage = err.response?.data?.detail || err.message || 'Ошибка загрузки лобби';
        setError(errorMessage);
        setIsLoading(false);
      }
    };

    loadLobby();

    return () => {
      console.log('GameLobby: Cleaning up', { gameId, hasToken: !!token, userId: user?.id });
      // Очищаем обработчики событий при размонтировании
      socketService.off('participant:ready_changed');
      socketService.off('participant:character_changed');
      socketService.off('player:joined');
      socketService.off('player:left');
      socketService.off('master:transferred');
      socketService.off('error');
      socketService.offGameStarted();
      clearInterval((window as any).__lobbyPollInterval);
      // Не отключаемся от WebSocket, т.к. переходим в GameRoom
    };
  }, [gameId, token, user?.id, setGame, setParticipants, setCurrentUserRole, setSelectedCharacterId, setIsReady, updateParticipantReady, updateParticipantCharacter, updateParticipantRole]);

  const handleReadyToggle = async () => {
    if (!gameId) return;
    
    // Наблюдатели не могут быть готовы к игре
    if (currentUserRole === 'spectator') {
      toast({
        title: 'Ограничение',
        description: 'Наблюдатели не могут быть готовы к игре',
        variant: 'destructive',
      });
      return;
    }
    
    if (currentUserRole === 'player' && !selectedCharacterId) {
      toast({
        title: 'Выберите персонажа',
        description: 'Сначала выберите персонажа, чтобы быть готовым к игре',
        variant: 'destructive',
      });
      return;
    }

    setIsSettingReady(true);
    try {
      const newReadyState = !isReady;

      // Если выбран шаблонный персонаж — создаём реального из его данных
      let realCharacterId = selectedCharacterId;
      if (selectedCharacterId && isTemplateCharacter(selectedCharacterId)) {
        const templateChar = characters.find(c => c.id === selectedCharacterId);
        if (templateChar) {
          const created = await charactersAPI.create({
            name: templateChar.name,
            race: templateChar.race,
            class: templateChar.class,
            level: templateChar.level,
            strength: templateChar.strength,
            dexterity: templateChar.dexterity,
            constitution: templateChar.constitution,
            intelligence: templateChar.intelligence,
            wisdom: templateChar.wisdom,
            charisma: templateChar.charisma,
            character_history: templateChar.character_history,
            equipment_and_features: templateChar.equipment_and_features,
          });
          realCharacterId = created.id;
          setSelectedCharacterId(created.id);
        }
      }

      const characterIdForServer = realCharacterId && !isTemplateCharacter(realCharacterId)
        ? realCharacterId
        : null;
      
      // Отправляем через API (устанавливаем персонажа и готовность)
      await gamesAPI.setReady(gameId, newReadyState, characterIdForServer);
      
      // Также отправляем через WebSocket для синхронизации
      socketService.setReady(gameId, newReadyState);
      
      setIsReady(newReadyState);
      updateParticipantReady(user?.id || '', newReadyState);
    } catch (err: any) {
      console.error('Error setting ready status:', err);
      toast({
        title: 'Ошибка',
        description: err.response?.data?.detail || 'Не удалось изменить статус готовности',
        variant: 'destructive',
      });
    } finally {
      setIsSettingReady(false);
    }
  };

  const handleStartGame = () => {
    if (!gameId) return;
    socketService.startGame(gameId);
    navigate(`/game/${gameId}`);
  };

  const handleTransferMaster = async (toUserId: string) => {
    if (!gameId || !user?.id) return;
    
    try {
      await gamesAPI.transferMasterRole(gameId, user.id, toUserId);
      toast({
        title: 'Роль передана',
        description: 'Роль мастера успешно передана',
      });
      // WebSocket событие и обновление состояния произойдет через обработчик onMasterTransferred
    } catch (err: any) {
      console.error('Error transferring master role:', err);
      toast({
        title: 'Ошибка',
        description: err.response?.data?.detail || 'Не удалось передать роль мастера',
        variant: 'destructive',
      });
    }
  };

  const handleSelectCharacter = async (character: Character) => {
    if (!gameId) return;
    
    // Наблюдатели не могут выбирать персонажей
    if (currentUserRole === 'spectator') {
      toast({
        title: 'Ограничение',
        description: 'Наблюдатели не могут выбирать персонажей',
        variant: 'destructive',
      });
      return;
    }
    
    try {
      const characterId = character.id;
      
      // Проверяем, является ли персонаж шаблонным (не является валидным UUID)
      // Шаблонные персонажи имеют ID вида "template-char-1", которые не сохраняются в БД
      const isTemplate = isTemplateCharacter(characterId);
      
      // Для шаблонных персонажей не отправляем character_id на сервер (null)
      // Но сохраняем локально для отображения
      const characterIdForServer = isTemplate ? null : characterId;
      
      // Обновляем локальное состояние сразу для быстрой обратной связи
      setSelectedCharacterId(characterId);
      
      // Отправляем на сервер через API только для реальных персонажей
      if (!isTemplate) {
        await gamesAPI.setCharacter(gameId, characterIdForServer);
        
        // Также отправляем через WebSocket для синхронизации
        socketService.setCharacter(gameId, characterIdForServer);
        
        // Обновляем участника в store только для реальных персонажей
        if (user?.id) {
          updateParticipantCharacter(user.id, characterIdForServer);
        }
      }
      
      toast({
        title: 'Персонаж выбран',
        description: `Вы выбрали ${character.name}`,
      });
    } catch (err: any) {
      console.error('Error setting character:', err);
      toast({
        title: 'Ошибка',
        description: err.response?.data?.detail || 'Не удалось выбрать персонажа',
        variant: 'destructive',
      });
      // Откатываем выбор в случае ошибки
      setSelectedCharacterId(null);
    }
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
                <div className="flex items-center gap-3">
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <p className="text-muted-foreground">Загрузка лобби...</p>
                </div>
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

  // Получаем URL карты для фона
  const mapUrl = currentGame?.map_url || '/assets/images/default-map.jpg';
  const pageBackgroundStyle = {
    backgroundImage: `url(${mapUrl})`,
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    backgroundAttachment: 'fixed',
  };

  const readyCount = participants.filter(p => p.is_ready).length;
  const totalPlayers = participants.filter(p => p.role === 'player').length;
  // Проверяем, готов ли мастер
  const masterParticipant = participants.find(p => p.role === 'master');
  const isMasterReady = masterParticipant?.is_ready || false;

  return (
    <div className="min-h-screen flex flex-col relative overflow-hidden" style={pageBackgroundStyle}>
      {/* Overlay для улучшения читаемости */}
      <div className="absolute inset-0 bg-black/30 backdrop-blur-[2px] pointer-events-none"></div>
      
      <div className="relative z-10 flex flex-col flex-1 overflow-hidden">
        <Header />
      
        <main className="flex-1 flex gap-4 p-4 overflow-hidden">
          {/* Левая панель - Список игроков */}
          <div className="flex-shrink-0">
            <PlayerList
              participants={participants}
              onReadyToggle={handleReadyToggle}
              currentUserReady={isReady}
              showReadyButton={true}
              onTransferMaster={handleTransferMaster}
              gameId={gameId}
              currentUserRole={currentUserRole}
            />
            
            {/* Invite-код */}
            {currentGame?.invite_code && (
              <Card className="mt-4 border-2 border-primary/50 bg-card/95 backdrop-blur-sm">
                <CardContent className="p-4">
                  <p className="text-xs text-muted-foreground mb-2">Код для входа в лобби</p>
                  <div className="flex items-center gap-2">
                    <span className="flex-1 text-center text-2xl font-mono font-bold tracking-widest text-primary bg-muted rounded px-3 py-1 select-all">
                      {currentGame.invite_code}
                    </span>
                    <Button size="icon" variant="outline" onClick={handleCopyInviteCode} title="Скопировать">
                      {copied ? <Check className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4" />}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Кнопка "Начать игру" для мастера */}
            {currentUserRole === 'master' && (
              <Card className="mt-4 border-2 border-border bg-card/95 backdrop-blur-sm">
                <CardContent className="p-4">
                  <div className="space-y-3">
                    <div className="text-sm text-muted-foreground">
                      {totalPlayers > 0 
                        ? `Готово: ${readyCount} из ${totalPlayers} игроков`
                        : 'Мастер может начать игру в любой момент'}
                    </div>
                    <Button
                      onClick={handleStartGame}
                      className="w-full"
                      disabled={!isMasterReady}
                    >
                      <Play className="w-4 h-4 mr-2" />
                      Начать игру
                    </Button>
                    {!isMasterReady && (
                      <p className="text-xs text-muted-foreground text-center">
                        Нажмите "Готов" выше, чтобы начать игру
                      </p>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Основная область - Выбор персонажей */}
          <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
            <Card className="flex-1 border-2 border-border bg-card/95 backdrop-blur-sm overflow-hidden flex flex-col">
              <CardContent className="p-6 flex-1 overflow-y-auto">
                <div className="mb-4">
                  <h2 className="text-2xl font-bold text-foreground mb-2">
                    {currentUserRole === 'master' ? 'Игроки выбирают персонажей' : 'Выберите персонажа'}
                  </h2>
                  <p className="text-muted-foreground">
                    {currentUserRole === 'master' 
                      ? 'Дождитесь, пока все игроки выберут персонажей и будут готовы'
                      : 'Выберите персонажа для игры. После выбора нажмите "Готов"'}
                  </p>
                </div>
                
                <CharacterPanel
                  characters={characters}
                  selectedId={selectedCharacterId || undefined}
                  participants={participants}
                  onSelect={handleSelectCharacter}
                />
              </CardContent>
            </Card>

            {/* Кнопка "Готов" для игроков */}
            {currentUserRole === 'player' && (
              <div className="mt-4 flex justify-end">
                <Button
                  onClick={handleReadyToggle}
                  disabled={!selectedCharacterId || isSettingReady}
                  size="lg"
                  className="min-w-[200px]"
                  variant={isReady ? "default" : "outline"}
                >
                  {isSettingReady ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Загрузка...
                    </>
                  ) : isReady ? (
                    'Готов к игре'
                  ) : (
                    'Готов'
                  )}
                </Button>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
