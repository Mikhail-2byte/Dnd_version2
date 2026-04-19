import { describe, it, expect, beforeEach } from 'vitest';
import { useGameStore } from '../gameStore';
import type { GameSession, Token, Player } from '../../types/game';

describe('gameStore', () => {
  beforeEach(() => {
    useGameStore.getState().reset();
  });

  it('should initialize with empty state', () => {
    const state = useGameStore.getState();
    expect(state.currentGame).toBeNull();
    expect(state.tokens).toEqual([]);
    expect(state.players).toEqual([]);
    expect(state.currentUserRole).toBeNull();
  });

  describe('setGame', () => {
    it('should set current game', () => {
      const mockGame: GameSession = {
        id: 'game-1',
        name: 'Test Game',
        invite_code: 'TEST01',
        master_id: 'user-1',
        map_url: '/uploads/maps/map.jpg',
        created_at: new Date().toISOString(),
        story: 'Test story',
      };

      useGameStore.getState().setGame(mockGame);

      const state = useGameStore.getState();
      expect(state.currentGame).toEqual(mockGame);
    });
  });

  describe('setTokens', () => {
    it('should set tokens', () => {
      const mockTokens: Token[] = [
        {
          id: 'token-1',
          game_id: 'game-1',
          name: 'Token 1',
          x: 10,
          y: 20,
          image_url: null,
          created_at: new Date().toISOString(),
        },
        {
          id: 'token-2',
          game_id: 'game-1',
          name: 'Token 2',
          x: 30,
          y: 40,
          image_url: null,
          created_at: new Date().toISOString(),
        },
      ];

      useGameStore.getState().setTokens(mockTokens);

      const state = useGameStore.getState();
      expect(state.tokens).toEqual(mockTokens);
      expect(state.tokens.length).toBe(2);
    });
  });

  describe('setPlayers', () => {
    it('should set players', () => {
      const mockPlayers: Player[] = [
        {
          id: 'user-1',
          username: 'player1',
          role: 'master',
        },
        {
          id: 'user-2',
          username: 'player2',
          role: 'player',
        },
      ];

      useGameStore.getState().setPlayers(mockPlayers);

      const state = useGameStore.getState();
      expect(state.players).toEqual(mockPlayers);
      expect(state.players.length).toBe(2);
    });
  });

  describe('setCurrentUserRole', () => {
    it('should set current user role to master', () => {
      useGameStore.getState().setCurrentUserRole('master');

      const state = useGameStore.getState();
      expect(state.currentUserRole).toBe('master');
    });

    it('should set current user role to player', () => {
      useGameStore.getState().setCurrentUserRole('player');

      const state = useGameStore.getState();
      expect(state.currentUserRole).toBe('player');
    });

    it('should set current user role to null', () => {
      useGameStore.getState().setCurrentUserRole('master');
      useGameStore.getState().setCurrentUserRole(null);

      const state = useGameStore.getState();
      expect(state.currentUserRole).toBeNull();
    });
  });

  describe('updateTokenPosition', () => {
    it('should update token position', () => {
      const mockTokens: Token[] = [
        {
          id: 'token-1',
          game_id: 'game-1',
          name: 'Token 1',
          x: 10,
          y: 20,
          image_url: null,
          created_at: new Date().toISOString(),
        },
        {
          id: 'token-2',
          game_id: 'game-1',
          name: 'Token 2',
          x: 30,
          y: 40,
          image_url: null,
          created_at: new Date().toISOString(),
        },
      ];

      useGameStore.getState().setTokens(mockTokens);
      useGameStore.getState().updateTokenPosition('token-1', 50, 60);

      const state = useGameStore.getState();
      const updatedToken = state.tokens.find((t) => t.id === 'token-1');
      expect(updatedToken?.x).toBe(50);
      expect(updatedToken?.y).toBe(60);

      // Проверяем что другой токен не изменился
      const otherToken = state.tokens.find((t) => t.id === 'token-2');
      expect(otherToken?.x).toBe(30);
      expect(otherToken?.y).toBe(40);
    });

    it('should not update position if token does not exist', () => {
      const mockTokens: Token[] = [
        {
          id: 'token-1',
          game_id: 'game-1',
          name: 'Token 1',
          x: 10,
          y: 20,
          image_url: null,
          created_at: new Date().toISOString(),
        },
      ];

      useGameStore.getState().setTokens(mockTokens);
      useGameStore.getState().updateTokenPosition('non-existent', 50, 60);

      const state = useGameStore.getState();
      expect(state.tokens.length).toBe(1);
      expect(state.tokens[0].x).toBe(10);
      expect(state.tokens[0].y).toBe(20);
    });
  });

  describe('addToken', () => {
    it('should add token to tokens array', () => {
      const newToken: Token = {
        id: 'token-1',
        game_id: 'game-1',
        name: 'New Token',
        x: 25,
        y: 35,
        image_url: null,
        created_at: new Date().toISOString(),
      };

      useGameStore.getState().addToken(newToken);

      const state = useGameStore.getState();
      expect(state.tokens.length).toBe(1);
      expect(state.tokens[0]).toEqual(newToken);
    });

    it('should add multiple tokens', () => {
      const token1: Token = {
        id: 'token-1',
        game_id: 'game-1',
        name: 'Token 1',
        x: 10,
        y: 20,
        image_url: null,
        created_at: new Date().toISOString(),
      };

      const token2: Token = {
        id: 'token-2',
        game_id: 'game-1',
        name: 'Token 2',
        x: 30,
        y: 40,
        image_url: null,
        created_at: new Date().toISOString(),
      };

      useGameStore.getState().addToken(token1);
      useGameStore.getState().addToken(token2);

      const state = useGameStore.getState();
      expect(state.tokens.length).toBe(2);
      expect(state.tokens).toContainEqual(token1);
      expect(state.tokens).toContainEqual(token2);
    });
  });

  describe('removeToken', () => {
    it('should remove token from tokens array', () => {
      const mockTokens: Token[] = [
        {
          id: 'token-1',
          game_id: 'game-1',
          name: 'Token 1',
          x: 10,
          y: 20,
          image_url: null,
          created_at: new Date().toISOString(),
        },
        {
          id: 'token-2',
          game_id: 'game-1',
          name: 'Token 2',
          x: 30,
          y: 40,
          image_url: null,
          created_at: new Date().toISOString(),
        },
      ];

      useGameStore.getState().setTokens(mockTokens);
      useGameStore.getState().removeToken('token-1');

      const state = useGameStore.getState();
      expect(state.tokens.length).toBe(1);
      expect(state.tokens[0].id).toBe('token-2');
    });

    it('should not remove anything if token does not exist', () => {
      const mockTokens: Token[] = [
        {
          id: 'token-1',
          game_id: 'game-1',
          name: 'Token 1',
          x: 10,
          y: 20,
          image_url: null,
          created_at: new Date().toISOString(),
        },
      ];

      useGameStore.getState().setTokens(mockTokens);
      useGameStore.getState().removeToken('non-existent');

      const state = useGameStore.getState();
      expect(state.tokens.length).toBe(1);
      expect(state.tokens[0].id).toBe('token-1');
    });
  });

  describe('reset', () => {
    it('should reset all state to initial values', () => {
      // Устанавливаем некоторые значения
      useGameStore.getState().setGame({
        id: 'game-1',
        name: 'Test Game',
        invite_code: 'TEST01',
        master_id: 'user-1',
        map_url: '/uploads/maps/map.jpg',
        created_at: new Date().toISOString(),
        story: 'Test story',
      });

      useGameStore.getState().setTokens([
        {
          id: 'token-1',
          game_id: 'game-1',
          name: 'Token 1',
          x: 10,
          y: 20,
          image_url: null,
          created_at: new Date().toISOString(),
        },
      ]);

      useGameStore.getState().setPlayers([
        {
          id: 'user-1',
          username: 'player1',
          role: 'master',
        },
      ]);

      useGameStore.getState().setCurrentUserRole('master');

      // Сбрасываем
      useGameStore.getState().reset();

      const state = useGameStore.getState();
      expect(state.currentGame).toBeNull();
      expect(state.tokens).toEqual([]);
      expect(state.players).toEqual([]);
      expect(state.currentUserRole).toBeNull();
    });
  });
});

