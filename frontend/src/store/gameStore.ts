import { create } from 'zustand';
import type { GameSession, Token, Player, Participant, LogEvent, ChatMessage } from '../types/game';

interface GameState {
  currentGame: GameSession | null;
  tokens: Token[];
  hiddenTokens: Token[];
  players: Player[];
  participants: Participant[];
  currentUserRole: 'master' | 'player' | 'spectator' | null;
  selectedCharacterId: string | null;
  isReady: boolean;
  logEvents: LogEvent[];
  chatMessages: ChatMessage[];
  setGame: (game: GameSession) => void;
  setTokens: (tokens: Token[]) => void;
  setHiddenTokens: (tokens: Token[]) => void;
  addHiddenToken: (token: Token) => void;
  revealHiddenToken: (tokenId: string) => void;
  setPlayers: (players: Player[]) => void;
  setParticipants: (participants: Participant[]) => void;
  setCurrentUserRole: (role: 'master' | 'player' | 'spectator' | null) => void;
  setSelectedCharacterId: (characterId: string | null) => void;
  setIsReady: (isReady: boolean) => void;
  updateTokenPosition: (tokenId: string, x: number, y: number) => void;
  addToken: (token: Token) => void;
  removeToken: (tokenId: string) => void;
  updateParticipantReady: (userId: string, isReady: boolean) => void;
  updateParticipantCharacter: (userId: string, characterId: string | null) => void;
  updateParticipantRole: (userId: string, role: 'master' | 'player') => void;
  addLogEvent: (event: LogEvent) => void;
  addChatMessage: (msg: ChatMessage) => void;
  clearLog: () => void;
  reset: () => void;
}

export const useGameStore = create<GameState>((set) => ({
  currentGame: null,
  tokens: [],
  hiddenTokens: [],
  players: [],
  participants: [],
  currentUserRole: null,
  selectedCharacterId: null,
  isReady: false,
  logEvents: [],
  chatMessages: [],

  setGame: (game) => set({ currentGame: game }),

  setTokens: (tokens) => set({ tokens }),

  setHiddenTokens: (tokens) => set({ hiddenTokens: tokens }),

  addHiddenToken: (token) =>
    set((state) => ({ hiddenTokens: [...state.hiddenTokens, token] })),

  revealHiddenToken: (tokenId) =>
    set((state) => {
      const token = state.hiddenTokens.find((t) => t.id === tokenId);
      if (!token) return state;
      return {
        hiddenTokens: state.hiddenTokens.filter((t) => t.id !== tokenId),
        tokens: [...state.tokens, { ...token, is_hidden: false }],
      };
    }),

  setPlayers: (players) => set({ players }),

  setParticipants: (participants) => set({ participants }),

  setCurrentUserRole: (role) => set({ currentUserRole: role }),

  setSelectedCharacterId: (characterId) => set({ selectedCharacterId: characterId }),

  setIsReady: (isReady) => set({ isReady }),

  updateTokenPosition: (tokenId, x, y) =>
    set((state) => ({
      tokens: state.tokens.map((token) =>
        token.id === tokenId ? { ...token, x, y } : token
      ),
    })),

  addToken: (token) =>
    set((state) => ({
      tokens: [...state.tokens, token],
    })),

  removeToken: (tokenId) =>
    set((state) => ({
      tokens: state.tokens.filter((token) => token.id !== tokenId),
    })),

  updateParticipantReady: (userId, isReady) =>
    set((state) => ({
      participants: state.participants.map((p) =>
        p.user_id === userId ? { ...p, is_ready: isReady } : p
      ),
      players: state.players.map((p) =>
        p.user_id === userId ? { ...p, is_ready: isReady } : p
      ),
    })),

  updateParticipantCharacter: (userId, characterId) =>
    set((state) => ({
      participants: state.participants.map((p) =>
        p.user_id === userId ? { ...p, character_id: characterId || undefined } : p
      ),
      players: state.players.map((p) =>
        p.user_id === userId ? { ...p, character_id: characterId || undefined } : p
      ),
    })),

  updateParticipantRole: (userId, role) =>
    set((state) => ({
      participants: state.participants.map((p) =>
        p.user_id === userId ? { ...p, role } : p
      ),
      players: state.players.map((p) =>
        p.user_id === userId ? { ...p, role } : p
      ),
    })),

  addLogEvent: (event) =>
    set((state) => ({ logEvents: [...state.logEvents, event] })),

  addChatMessage: (msg) =>
    set((state) => ({ chatMessages: [...state.chatMessages, msg] })),

  clearLog: () => set({ logEvents: [], chatMessages: [] }),

  reset: () =>
    set({
      currentGame: null,
      tokens: [],
      hiddenTokens: [],
      players: [],
      participants: [],
      currentUserRole: null,
      selectedCharacterId: null,
      isReady: false,
      logEvents: [],
      chatMessages: [],
    }),
}));

