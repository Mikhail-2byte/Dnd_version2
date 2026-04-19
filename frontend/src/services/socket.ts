import { io, Socket } from 'socket.io-client';
import type { Token, Player } from '../types/game';
import type { CombatSession, CombatParticipant } from '../types/combat';

const WS_URL = import.meta.env.VITE_WS_URL || window.location.origin;

export interface GameState {
  game: {
    id: string;
    name: string;
    invite_code: string;
    map_url: string | null;
  };
  tokens: Token[];
  players: Player[];
}

export class SocketService {
  private socket: Socket | null = null;
  private currentGameId: string | null = null;

  getSocket(): Socket | null {
    return this.socket;
  }

  isConnected(): boolean {
    return this.socket !== null && this.socket.connected;
  }

  connect(token: string): Socket {
    // Если socket уже существует и подключен, возвращаем его
    if (this.socket && this.socket.connected) {
      console.log('Socket already connected, reusing existing connection');
      return this.socket;
    }

    // Если socket существует, но не подключен, отключаем его
    if (this.socket) {
      console.log('Disconnecting existing socket before creating new one', {
        socketId: this.socket.id,
        connected: this.socket.connected,
        disconnected: this.socket.disconnected
      });
      this.socket.disconnect();
      this.socket = null;
    }

    console.log('Creating new socket connection to', WS_URL);
    this.socket = io(WS_URL, {
      auth: { token },
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5,
      reconnectionDelayMax: 5000,
    });

    console.log('Socket instance created:', {
      socketExists: !!this.socket,
      socketId: this.socket.id,
      connected: this.socket.connected
    });

    // Обработчик подключения
    this.socket.on('connect', () => {
      console.log('WebSocket connected, socket ID:', this.socket?.id);
      // Восстанавливаем подключение к игре, если было
      if (this.currentGameId) {
        this.joinGame(this.currentGameId);
      }
    });

    // Обработчик переподключения
    this.socket.on('reconnect', (attemptNumber) => {
      console.log(`WebSocket reconnected after ${attemptNumber} attempts`);
      // Восстанавливаем подключение к игре
      if (this.currentGameId) {
        this.joinGame(this.currentGameId);
      }
    });

    // Обработчик отключения
    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason);
      // НЕ устанавливаем this.socket = null, чтобы можно было переподключиться
    });

    return this.socket;
  }

  disconnect(): void {
    console.log('socketService.disconnect called', { socketExists: !!this.socket });
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.currentGameId = null;
      console.log('Socket disconnected and cleared');
    }
  }

  joinGame(gameId: string): void {
    if (this.socket) {
      this.currentGameId = gameId;
      this.socket.emit('game:join', { game_id: gameId });
    }
  }

  moveToken(gameId: string, tokenId: string, x: number, y: number): void {
    if (this.socket) {
      this.socket.emit('token:move', {
        game_id: gameId,
        token_id: tokenId,
        x,
        y,
      });
    }
  }

  createToken(gameId: string, name: string, x: number, y: number, imageUrl?: string): void {
    console.log('socketService.createToken called:', { 
      gameId, 
      name, 
      x, 
      y, 
      imageUrl, 
      socketExists: !!this.socket,
      socketConnected: this.socket?.connected,
      socketId: this.socket?.id,
      socketDisconnected: this.socket?.disconnected
    });
    
    if (!this.socket) {
      console.error('Socket not initialized, cannot create token');
      console.error('SocketService state:', {
        socketExists: !!this.socket,
        currentGameId: this.currentGameId,
        socketServiceInstance: this
      });
      // Попробуем переподключиться, если есть токен
      console.warn('Attempting to reconnect...');
      return;
    }

    // Если socket еще не подключен, ждем подключения
    if (!this.socket.connected) {
      console.warn('Socket not connected yet, waiting for connection...', {
        socketId: this.socket.id,
        disconnected: this.socket.disconnected
      });
      
      // Проверяем, не отключен ли socket полностью
      if (this.socket.disconnected) {
        console.error('Socket is disconnected, cannot create token');
        return;
      }

      this.socket.once('connect', () => {
        console.log('Socket connected, creating token now');
        this.socket!.emit('token:create', {
          game_id: gameId,
          name,
          x,
          y,
          image_url: imageUrl,
        });
        console.log('Token create event emitted (after wait)');
      });
      return;
    }
    
    // Socket подключен, создаем токен сразу
    this.socket.emit('token:create', {
      game_id: gameId,
      name,
      x,
      y,
      image_url: imageUrl,
    });
    console.log('Token create event emitted successfully');
  }

  deleteToken(gameId: string, tokenId: string): void {
    if (this.socket) {
      this.socket.emit('token:delete', {
        game_id: gameId,
        token_id: tokenId,
      });
    }
  }

  onGameState(callback: (state: GameState) => void): void {
    if (this.socket) {
      this.socket.on('game:state', callback);
    }
  }

  onTokenMoved(callback: (data: { token_id: string; x: number; y: number; moved_by: string }) => void): void {
    if (this.socket) {
      this.socket.on('token:moved', callback);
    }
  }

  onTokenCreated(callback: (data: { token: Token }) => void): void {
    if (this.socket) {
      this.socket.on('token:created', callback);
    }
  }

  onTokenDeleted(callback: (data: { token_id: string }) => void): void {
    if (this.socket) {
      this.socket.on('token:deleted', callback);
    }
  }

  onPlayerJoined(callback: (data: { user_id: string; username: string }) => void): void {
    if (this.socket) {
      this.socket.on('player:joined', callback);
    }
  }

  onPlayerLeft(callback: (data: { user_id: string }) => void): void {
    if (this.socket) {
      this.socket.on('player:left', callback);
    }
  }

  rollDice(gameId: string, count: number, faces: number, rollType?: string, modifier?: number, advantage?: boolean): void {
    if (this.socket) {
      this.socket.emit('dice:roll', {
        game_id: gameId,
        count,
        faces,
        ...(rollType && { roll_type: rollType }),
        ...(modifier !== undefined && { modifier }),
        ...(advantage !== undefined && { advantage }),
      });
    }
  }

  onDiceRolled(callback: (data: {
    game_id: string;
    user_id: string;
    username: string;
    count: number;
    faces: number;
    rolls: Array<{ die_id: string; value: number }>;
    total: number;
  }) => void): void {
    if (this.socket) {
      this.socket.on('dice:rolled', callback);
    }
  }

  startGame(gameId: string): void {
    if (this.socket) {
      this.socket.emit('game_start', { game_id: gameId });
    }
  }

  onGameStarted(callback: (data: { game_id: string }) => void): void {
    if (this.socket) {
      this.socket.on('game:started', callback);
    }
  }

  offGameStarted(): void {
    if (this.socket) {
      this.socket.off('game:started');
    }
  }

  setReady(gameId: string, isReady: boolean): void {
    if (this.socket) {
      this.socket.emit('participant:ready', {
        game_id: gameId,
        is_ready: isReady,
      });
    }
  }

  onParticipantReadyChanged(callback: (data: {
    user_id: string;
    username: string;
    is_ready: boolean;
  }) => void): void {
    if (this.socket) {
      this.socket.on('participant:ready_changed', callback);
    }
  }

  setCharacter(gameId: string, characterId: string | null): void {
    if (this.socket) {
      this.socket.emit('participant:character', {
        game_id: gameId,
        character_id: characterId,
      });
    }
  }

  onParticipantCharacterChanged(callback: (data: {
    user_id: string;
    username: string;
    character_id: string | null;
  }) => void): void {
    if (this.socket) {
      this.socket.on('participant:character_changed', callback);
    }
  }

  onMasterTransferred(callback: (data: {
    game_id: string;
    old_master_id: string;
    new_master_id: string;
  }) => void): void {
    if (this.socket) {
      this.socket.on('master:transferred', callback);
    }
  }

  onError(callback: (data: { message: string }) => void): void {
    if (this.socket) {
      this.socket.on('error', callback);
    }
  }

  sendSceneDescription(gameId: string, description: string, title?: string): void {
    if (this.socket) {
      this.socket.emit('scene:description', {
        game_id: gameId,
        description,
        ...(title && { title }),
      });
    }
  }

  onSceneDescription(callback: (data: {
    game_id: string;
    user_id: string;
    description: string;
    title?: string | null;
  }) => void): void {
    if (this.socket) {
      this.socket.on('scene:description_received', callback);
    }
  }

  offSceneDescription(): void {
    if (this.socket) {
      this.socket.off('scene:description_received');
    }
  }

  onCombatStarted(callback: (data: CombatSession) => void): void {
    if (this.socket) {
      this.socket.on('combat:started', callback);
    }
  }

  onInitiativeRolled(callback: (data: CombatParticipant) => void): void {
    if (this.socket) {
      this.socket.on('combat:initiative_rolled', callback);
    }
  }

  onCombatEnded(callback: () => void): void {
    if (this.socket) {
      this.socket.on('combat:ended', callback);
    }
  }

  onCombatAttack(callback: (data: {
    attacker_id: string;
    target_id: string;
    hit: boolean;
    attack_roll: number;
    modifier: number;
    total_attack: number;
    target_ac: number;
    damage: number | null;
  }) => void): void {
    if (this.socket) {
      this.socket.on('combat:attack', callback);
    }
  }

  onCombatDamage(callback: (data: {
    participant_id: string;
    damage: number;
    current_hp: number;
    max_hp: number;
    was_defeated: boolean;
  }) => void): void {
    if (this.socket) {
      this.socket.on('combat:damage', callback);
    }
  }

  onCombatHeal(callback: (data: {
    participant_id: string;
    healing: number;
    current_hp: number;
    max_hp: number;
  }) => void): void {
    if (this.socket) {
      this.socket.on('combat:heal', callback);
    }
  }

  onParticipantDefeated(callback: (data: {
    participant_id: string;
  }) => void): void {
    if (this.socket) {
      this.socket.on('combat:participant_defeated', callback);
    }
  }

  off(event: string): void {
    if (this.socket) {
      this.socket.off(event);
    }
  }
}

export const socketService = new SocketService();

