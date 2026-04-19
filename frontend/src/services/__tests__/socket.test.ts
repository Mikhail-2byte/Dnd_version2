import { describe, it, expect, beforeEach, vi } from 'vitest';
import { SocketService } from '../socket';
import type { Socket } from 'socket.io-client';

// Мокируем socket.io-client
const mockSocket = {
  id: 'socket-123',
  connected: true,
  disconnected: false,
  emit: vi.fn(),
  on: vi.fn(),
  off: vi.fn(),
  once: vi.fn(),
  disconnect: vi.fn(),
} as unknown as Socket;

vi.mock('socket.io-client', () => ({
  io: vi.fn(() => mockSocket),
}));

describe('SocketService', () => {
  let socketService: SocketService;

  beforeEach(() => {
    socketService = new SocketService();
    vi.clearAllMocks();
  });

  describe('getSocket', () => {
    it('should return null when socket is not initialized', () => {
      expect(socketService.getSocket()).toBeNull();
    });

    it('should return socket when connected', () => {
      socketService.connect('test-token');
      expect(socketService.getSocket()).not.toBeNull();
    });
  });

  describe('isConnected', () => {
    it('should return false when socket is not initialized', () => {
      expect(socketService.isConnected()).toBe(false);
    });

    it('should return true when socket is connected', () => {
      socketService.connect('test-token');
      expect(socketService.isConnected()).toBe(true);
    });
  });

  describe('connect', () => {
    it('should create new socket connection', async () => {
      const { io } = await import('socket.io-client');
      socketService.connect('test-token');

      expect(io).toHaveBeenCalledWith('http://localhost:8000', {
        auth: { token: 'test-token' },
        transports: ['websocket', 'polling'],
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionAttempts: 5,
        reconnectionDelayMax: 5000,
      });
    });

    it('should return existing socket if already connected', () => {
      socketService.connect('test-token');
      const firstSocket = socketService.getSocket();

      // Мокируем что socket уже подключен
      Object.defineProperty(mockSocket, 'connected', { value: true, writable: true });

      const secondSocket = socketService.connect('test-token');
      expect(secondSocket).toBe(firstSocket);
    });

    it('should disconnect existing socket before creating new one', () => {
      socketService.connect('test-token');
      Object.defineProperty(mockSocket, 'connected', { value: false, writable: true });

      socketService.connect('new-token');
      expect(mockSocket.disconnect).toHaveBeenCalled();
    });
  });

  describe('disconnect', () => {
    it('should do nothing if socket is not initialized', () => {
      socketService.disconnect();
      expect(socketService.getSocket()).toBeNull();
    });

    it('should disconnect socket and clear it', () => {
      socketService.connect('test-token');
      expect(socketService.getSocket()).not.toBeNull();

      socketService.disconnect();
      expect(mockSocket.disconnect).toHaveBeenCalled();
      expect(socketService.getSocket()).toBeNull();
    });
  });

  describe('joinGame', () => {
    it('should emit game:join event', () => {
      socketService.connect('test-token');
      socketService.joinGame('game-1');

      expect(mockSocket.emit).toHaveBeenCalledWith('game:join', { game_id: 'game-1' });
    });

    it('should do nothing if socket is not initialized', () => {
      socketService.joinGame('game-1');
      expect(mockSocket.emit).not.toHaveBeenCalled();
    });
  });

  describe('moveToken', () => {
    it('should emit token:move event', () => {
      socketService.connect('test-token');
      socketService.moveToken('game-1', 'token-1', 50, 60);

      expect(mockSocket.emit).toHaveBeenCalledWith('token:move', {
        game_id: 'game-1',
        token_id: 'token-1',
        x: 50,
        y: 60,
      });
    });

    it('should do nothing if socket is not initialized', () => {
      socketService.moveToken('game-1', 'token-1', 50, 60);
      expect(mockSocket.emit).not.toHaveBeenCalled();
    });
  });

  describe('deleteToken', () => {
    it('should emit token:delete event', () => {
      socketService.connect('test-token');
      socketService.deleteToken('game-1', 'token-1');

      expect(mockSocket.emit).toHaveBeenCalledWith('token:delete', {
        game_id: 'game-1',
        token_id: 'token-1',
      });
    });

    it('should do nothing if socket is not initialized', () => {
      socketService.deleteToken('game-1', 'token-1');
      expect(mockSocket.emit).not.toHaveBeenCalled();
    });
  });

  describe('rollDice', () => {
    it('should emit dice:roll event', () => {
      socketService.connect('test-token');
      socketService.rollDice('game-1', 2, 20);

      expect(mockSocket.emit).toHaveBeenCalledWith('dice:roll', {
        game_id: 'game-1',
        count: 2,
        faces: 20,
      });
    });

    it('should do nothing if socket is not initialized', () => {
      socketService.rollDice('game-1', 2, 20);
      expect(mockSocket.emit).not.toHaveBeenCalled();
    });
  });

  describe('event listeners', () => {
    it('should register onGameState listener', () => {
      socketService.connect('test-token');
      const callback = vi.fn();
      socketService.onGameState(callback);

      expect(mockSocket.on).toHaveBeenCalledWith('game:state', callback);
    });

    it('should register onTokenMoved listener', () => {
      socketService.connect('test-token');
      const callback = vi.fn();
      socketService.onTokenMoved(callback);

      expect(mockSocket.on).toHaveBeenCalledWith('token:moved', callback);
    });

    it('should register onTokenCreated listener', () => {
      socketService.connect('test-token');
      const callback = vi.fn();
      socketService.onTokenCreated(callback);

      expect(mockSocket.on).toHaveBeenCalledWith('token:created', callback);
    });

    it('should register onTokenDeleted listener', () => {
      socketService.connect('test-token');
      const callback = vi.fn();
      socketService.onTokenDeleted(callback);

      expect(mockSocket.on).toHaveBeenCalledWith('token:deleted', callback);
    });

    it('should register onPlayerJoined listener', () => {
      socketService.connect('test-token');
      const callback = vi.fn();
      socketService.onPlayerJoined(callback);

      expect(mockSocket.on).toHaveBeenCalledWith('player:joined', callback);
    });

    it('should register onPlayerLeft listener', () => {
      socketService.connect('test-token');
      const callback = vi.fn();
      socketService.onPlayerLeft(callback);

      expect(mockSocket.on).toHaveBeenCalledWith('player:left', callback);
    });

    it('should register onDiceRolled listener', () => {
      socketService.connect('test-token');
      const callback = vi.fn();
      socketService.onDiceRolled(callback);

      expect(mockSocket.on).toHaveBeenCalledWith('dice:rolled', callback);
    });

    it('should register onError listener', () => {
      socketService.connect('test-token');
      const callback = vi.fn();
      socketService.onError(callback);

      expect(mockSocket.on).toHaveBeenCalledWith('error', callback);
    });

    it('should not register listener if socket is not initialized', () => {
      const callback = vi.fn();
      socketService.onGameState(callback);

      expect(mockSocket.on).not.toHaveBeenCalled();
    });
  });

  describe('off', () => {
    it('should unregister event listener', () => {
      socketService.connect('test-token');
      socketService.off('game:state');

      expect(mockSocket.off).toHaveBeenCalledWith('game:state');
    });

    it('should do nothing if socket is not initialized', () => {
      socketService.off('game:state');
      expect(mockSocket.off).not.toHaveBeenCalled();
    });
  });
});

