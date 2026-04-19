import type { Player, Participant } from '../types/game';
import { Card, CardContent } from './ui/card';
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Circle, Check, X, Crown } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAuthStore } from '../store/authStore';
import { createPlayerColorMap, getPlayerColor } from '../utils/playerColors';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from './ui/alert-dialog';
import { useState } from 'react';

interface PlayerListProps {
  players?: Player[];
  participants?: Participant[];
  onReadyToggle?: (isReady: boolean) => void;
  currentUserReady?: boolean;
  showReadyButton?: boolean;
  onTransferMaster?: (toUserId: string) => void;
  gameId?: string;
  currentUserRole?: 'master' | 'player' | 'spectator' | null;
}

export default function PlayerList({ 
  players = [], 
  participants = [],
  onReadyToggle,
  currentUserReady = false,
  showReadyButton = false,
  onTransferMaster,
  gameId,
  currentUserRole
}: PlayerListProps) {
  const { user } = useAuthStore();
  const [transferDialogOpen, setTransferDialogOpen] = useState(false);
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null);
  
  // Используем participants, если есть, иначе players
  const displayList = participants.length > 0 
    ? participants.map(p => ({
        user_id: p.user_id,
        username: p.username,
        role: p.role as 'master' | 'player' | 'spectator',
        is_ready: p.is_ready,
        character_id: p.character_id
      }))
    : players;
  
  const readyCount = displayList.filter(p => p.is_ready === true).length;
  const onlineCount = displayList.length;
  
  // Создаем карту цветов для игроков
  const playerColorMap = participants.length > 0 
    ? createPlayerColorMap(participants)
    : createPlayerColorMap(players.map(p => ({ user_id: p.user_id, role: p.role })));
  
  const isCurrentUser = (player: typeof displayList[0]) => player.user_id === user?.id;
  
  // Получить цвет игрока
  const getPlayerColorClasses = (player: typeof displayList[0]) => {
    if (player.role === 'master') return null;
    const color = playerColorMap.get(player.user_id);
    return color;
  };

  return (
    <Card className="w-72 p-4 border-2 border-border bg-card/95 backdrop-blur-sm">
      <div className="space-y-4">
        <div className="border-b border-border pb-3">
          <h2 className="text-lg font-bold text-foreground">Игроки в лобби</h2>
          <p className="text-sm text-muted-foreground">
            {readyCount > 0 
              ? `${readyCount} из ${onlineCount} готовы` 
              : onlineCount > 0
                ? `${onlineCount} ${onlineCount === 1 ? 'игрок' : 'игроков'} онлайн`
                : 'Нет игроков'}
          </p>
        </div>

        <div className="space-y-2">
          {displayList.length === 0 ? (
            <p className="text-muted-foreground text-sm text-center py-4">Нет игроков</p>
          ) : (
            displayList.map((player) => {
              const isReady = player.is_ready === true;
              const isCurrent = isCurrentUser(player);
              const playerColor = getPlayerColorClasses(player);
              
              return (
                <div
                  key={player.user_id}
                  className="flex items-center gap-3 p-2 rounded-md hover:bg-muted/50 transition-colors"
                >
                  <Avatar className={`w-10 h-10 border-2 ${playerColor ? playerColor.border : 'border-border'}`}>
                    <AvatarImage src={`/assets/images/placeholder-user.jpg`} alt={player.username} />
                    <AvatarFallback className={playerColor ? playerColor.bg : ''}>
                      {player.username[0].toUpperCase()}
                    </AvatarFallback>
                  </Avatar>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="font-medium text-sm text-foreground truncate">{player.username}</p>
                      {player.role === 'master' && (
                        <Badge variant="default" className="text-xs px-1.5 py-0">
                          М
                        </Badge>
                      )}
                      {player.role === 'spectator' && (
                        <Badge variant="secondary" className="text-xs px-1.5 py-0">
                          Н
                        </Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-1.5 mt-0.5">
                      <Circle
                        className={cn(
                          'w-2 h-2 fill-current transition-colors',
                          isReady
                            ? 'text-green-600 dark:text-green-500'
                            : 'text-yellow-600 dark:text-yellow-500'
                        )}
                      />
                      <span className="text-xs text-muted-foreground">
                        {isReady ? 'Готов' : 'Не готов'}
                      </span>
                    </div>
                  </div>

                  {isReady && !isCurrent && (
                    <Badge variant="secondary" className="text-xs bg-green-500/20 text-green-700 dark:text-green-400 border-green-500/30 flex-shrink-0">
                      <Check className="w-3 h-3" />
                    </Badge>
                  )}

                  {isCurrent && showReadyButton && onReadyToggle && (
                    <Button
                      size="sm"
                      variant={currentUserReady ? "default" : "outline"}
                      onClick={() => onReadyToggle(!currentUserReady)}
                      className="flex-shrink-0 h-7 px-2 text-xs"
                    >
                      {currentUserReady ? (
                        <>
                          <Check className="w-3 h-3 mr-1" />
                          Готов
                        </>
                      ) : (
                        <>
                          <X className="w-3 h-3 mr-1" />
                          Не готов
                        </>
                      )}
                    </Button>
                  )}

                  {currentUserRole === 'master' && 
                   !isCurrent && 
                   player.role === 'player' && 
                   onTransferMaster && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        setSelectedUserId(player.user_id);
                        setTransferDialogOpen(true);
                      }}
                      className="flex-shrink-0 h-7 px-2 text-xs"
                      title="Передать роль мастера"
                    >
                      <Crown className="w-3 h-3" />
                    </Button>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Диалог подтверждения передачи роли мастера */}
      <AlertDialog open={transferDialogOpen} onOpenChange={setTransferDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Передать роль мастера?</AlertDialogTitle>
            <AlertDialogDescription>
              Вы уверены, что хотите передать роль мастера игроку{' '}
              <strong>
                {displayList.find(p => p.user_id === selectedUserId)?.username}
              </strong>
              ? Вы станете обычным игроком и потеряете права мастера.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Отмена</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => {
                if (selectedUserId && onTransferMaster) {
                  onTransferMaster(selectedUserId);
                  setTransferDialogOpen(false);
                  setSelectedUserId(null);
                }
              }}
            >
              Передать роль
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </Card>
  );
}

