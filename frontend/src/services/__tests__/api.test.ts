import { describe, it, expect, vi, beforeEach } from 'vitest';
import type { TokenResponse, User } from '../../types/user';
import type { GameSession, Token } from '../../types/game';
import type { Character } from '../../types/character';

// Мокируем axios ДО импорта api
vi.mock('axios', () => {
  // Создаем mock instance внутри factory (без использования внешних переменных)
  const instance = {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    interceptors: {
      request: {
        use: vi.fn(),
      },
      response: {
        use: vi.fn(),
      },
    },
  };
  
  return {
    default: {
      create: vi.fn(() => instance),
    },
  };
});

// Импортируем API после мокирования
import { authAPI, gamesAPI, charactersAPI } from '../api';
import axios from 'axios';

// Мокируем window.location
Object.defineProperty(window, 'location', {
  value: {
    href: '',
  },
  writable: true,
});

describe('api', () => {
  let mockInstance: any;

  beforeEach(() => {
    vi.clearAllMocks();
    // Получаем mock instance из axios.create.mock.results
    // axios.create вызывается при импорте api.ts, поэтому instance уже существует
    const createMock = vi.mocked(axios.create);
    if (createMock.mock.results.length > 0) {
      mockInstance = createMock.mock.results[createMock.mock.results.length - 1].value;
    } else {
      // Если по какой-то причине results пуст, создаем новый instance
      mockInstance = axios.create();
    }
  });

  describe('authAPI', () => {
    describe('register', () => {
      it('should register user successfully', async () => {
        const mockResponse: TokenResponse = {
          access_token: 'token-123',
          token_type: 'bearer',
          user: {
            id: 'user-1',
            email: 'test@example.com',
            username: 'testuser',
            created_at: new Date().toISOString(),
          },
        };

        mockInstance.post.mockResolvedValue({ data: mockResponse });

        const result = await authAPI.register('test@example.com', 'testuser', 'password123');

        expect(result).toEqual(mockResponse);
        expect(mockInstance.post).toHaveBeenCalledWith('/api/auth/register', {
          email: 'test@example.com',
          username: 'testuser',
          password: 'password123',
        });
      });

      it('should handle registration error', async () => {
        const error = { response: { status: 400, data: { detail: 'Email already exists' } } };
        mockInstance.post.mockRejectedValue(error);

        await expect(
          authAPI.register('test@example.com', 'testuser', 'password123')
        ).rejects.toEqual(error);
      });
    });

    describe('login', () => {
      it('should login user successfully', async () => {
        const mockResponse: TokenResponse = {
          access_token: 'token-123',
          token_type: 'bearer',
          user: {
            id: 'user-1',
            email: 'test@example.com',
            username: 'testuser',
            created_at: new Date().toISOString(),
          },
        };

        mockInstance.post.mockResolvedValue({ data: mockResponse });

        const result = await authAPI.login('test@example.com', 'password123');

        expect(result).toEqual(mockResponse);
        expect(mockInstance.post).toHaveBeenCalledWith('/api/auth/login', {
          email: 'test@example.com',
          password: 'password123',
        });
      });

      it('should handle login error', async () => {
        const error = { response: { status: 401, data: { detail: 'Invalid credentials' } } };
        mockInstance.post.mockRejectedValue(error);

        await expect(authAPI.login('test@example.com', 'wrongpassword')).rejects.toEqual(error);
      });
    });

    describe('me', () => {
      it('should get current user successfully', async () => {
        const mockUser: User = {
          id: 'user-1',
          email: 'test@example.com',
          username: 'testuser',
          created_at: new Date().toISOString(),
        };

        mockInstance.get.mockResolvedValue({ data: mockUser });

        const result = await authAPI.me();

        expect(result).toEqual(mockUser);
        expect(mockInstance.get).toHaveBeenCalledWith('/api/auth/me');
      });
    });
  });

  describe('gamesAPI', () => {
    describe('create', () => {
      it('should create game successfully', async () => {
        const mockGame: GameSession = {
          id: 'game-1',
          name: 'Test Game',
          invite_code: 'TEST01',
          master_id: 'user-1',
          map_url: null,
          created_at: new Date().toISOString(),
          story: 'Test story',
        };

        mockInstance.post.mockResolvedValue({ data: mockGame });

        const result = await gamesAPI.create('Test Game', 'Test story');

        expect(result).toEqual(mockGame);
        expect(mockInstance.post).toHaveBeenCalledWith('/api/games', {
          name: 'Test Game',
          story: 'Test story',
          map_url: undefined,
        });
      });

      it('should create game with map url', async () => {
        const mockGame: GameSession = {
          id: 'game-1',
          name: 'Test Game',
          invite_code: 'TEST01',
          master_id: 'user-1',
          map_url: '/uploads/maps/map.jpg',
          created_at: new Date().toISOString(),
          story: 'Test story',
        };

        mockInstance.post.mockResolvedValue({ data: mockGame });

        const result = await gamesAPI.create('Test Game', 'Test story', '/uploads/maps/map.jpg');

        expect(result).toEqual(mockGame);
        expect(mockInstance.post).toHaveBeenCalledWith('/api/games', {
          name: 'Test Game',
          story: 'Test story',
          map_url: '/uploads/maps/map.jpg',
        });
      });
    });

    describe('getByInviteCode', () => {
      it('should get game by invite code successfully', async () => {
        const mockGame: GameSession = {
          id: 'game-1',
          name: 'Test Game',
          invite_code: 'TEST01',
          master_id: 'user-1',
          map_url: null,
          created_at: new Date().toISOString(),
          story: 'Test story',
        };

        mockInstance.get.mockResolvedValue({ data: mockGame });

        const result = await gamesAPI.getByInviteCode('TEST01');

        expect(result).toEqual(mockGame);
        expect(mockInstance.get).toHaveBeenCalledWith('/api/games/TEST01');
      });
    });

    describe('join', () => {
      it('should join game successfully', async () => {
        const mockGame: GameSession = {
          id: 'game-1',
          name: 'Test Game',
          invite_code: 'TEST01',
          master_id: 'user-1',
          map_url: null,
          created_at: new Date().toISOString(),
          story: 'Test story',
        };

        mockInstance.post.mockResolvedValue({ data: mockGame });

        const result = await gamesAPI.join('game-1');

        expect(result).toEqual(mockGame);
        expect(mockInstance.post).toHaveBeenCalledWith('/api/games/game-1/join');
      });
    });

    describe('getInfo', () => {
      it('should get game info successfully', async () => {
        const mockGame: GameSession = {
          id: 'game-1',
          name: 'Test Game',
          invite_code: 'TEST01',
          master_id: 'user-1',
          map_url: null,
          created_at: new Date().toISOString(),
          story: 'Test story',
        };

        mockInstance.get.mockResolvedValue({ data: mockGame });

        const result = await gamesAPI.getInfo('game-1');

        expect(result).toEqual(mockGame);
        expect(mockInstance.get).toHaveBeenCalledWith('/api/games/game-1/info');
      });
    });

    describe('getTokens', () => {
      it('should get game tokens successfully', async () => {
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

        mockInstance.get.mockResolvedValue({ data: mockTokens });

        const result = await gamesAPI.getTokens('game-1');

        expect(result).toEqual(mockTokens);
        expect(mockInstance.get).toHaveBeenCalledWith('/api/games/game-1/tokens');
      });
    });
  });

  describe('charactersAPI', () => {
    describe('create', () => {
      it('should create character successfully', async () => {
        const mockCharacter: Character = {
          id: 'char-1',
          user_id: 'user-1',
          name: 'Test Character',
          class: 'Fighter',
          level: 1,
          strength: 16,
          dexterity: 14,
          constitution: 15,
          intelligence: 12,
          wisdom: 13,
          charisma: 10,
          created_at: new Date().toISOString(),
        };

        mockInstance.post.mockResolvedValue({ data: mockCharacter });

        const characterData = {
          name: 'Test Character',
          class: 'Fighter',
          level: 1,
          strength: 16,
          dexterity: 14,
          constitution: 15,
          intelligence: 12,
          wisdom: 13,
          charisma: 10,
        };

        const result = await charactersAPI.create(characterData);

        expect(result).toEqual(mockCharacter);
        expect(mockInstance.post).toHaveBeenCalledWith('/api/characters', characterData);
      });
    });

    describe('getAll', () => {
      it('should get all characters successfully', async () => {
        const mockCharacters: Character[] = [
          {
            id: 'char-1',
            user_id: 'user-1',
            name: 'Character 1',
            class: 'Fighter',
            level: 1,
            strength: 16,
            dexterity: 14,
            constitution: 15,
            intelligence: 12,
            wisdom: 13,
            charisma: 10,
            created_at: new Date().toISOString(),
          },
        ];

        mockInstance.get.mockResolvedValue({ data: { characters: mockCharacters } });

        const result = await charactersAPI.getAll();

        expect(result).toEqual(mockCharacters);
        expect(mockInstance.get).toHaveBeenCalledWith('/api/characters');
      });
    });
  });
});
