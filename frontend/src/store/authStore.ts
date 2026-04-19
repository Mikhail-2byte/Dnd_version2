import { create } from 'zustand';
import type { User } from '../types/user';
import { authAPI } from '../services/api';

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  hasCheckedAuth: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => {
  const token = localStorage.getItem('token');
  return {
    user: null,
    token,
    isLoading: false, // Не начинаем с загрузки, checkAuth установит его
    hasCheckedAuth: false,

    login: async (email: string, password: string) => {
      set({ isLoading: true });
      try {
        const response = await authAPI.login(email, password);
        localStorage.setItem('token', response.access_token);
        set({ user: response.user, token: response.access_token, isLoading: false, hasCheckedAuth: true });
      } catch (error) {
        set({ isLoading: false, hasCheckedAuth: true });
        throw error;
      }
    },

    register: async (email: string, username: string, password: string) => {
      set({ isLoading: true });
      try {
        const response = await authAPI.register(email, username, password);
        localStorage.setItem('token', response.access_token);
        set({ user: response.user, token: response.access_token, isLoading: false, hasCheckedAuth: true });
      } catch (error) {
        set({ isLoading: false, hasCheckedAuth: true });
        throw error;
      }
    },

    logout: () => {
      localStorage.removeItem('token');
      set({ user: null, token: null, hasCheckedAuth: true });
    },

    checkAuth: async () => {
      // Предотвращаем параллельные вызовы
      const state = get();
      if (state.isLoading) {
        return; // Уже идет проверка
      }

      if (state.hasCheckedAuth) {
        return; // Уже проверяли
      }

      const token = localStorage.getItem('token');
      if (!token) {
        set({ user: null, token: null, isLoading: false, hasCheckedAuth: true });
        return;
      }

      set({ isLoading: true });
      try {
        const user = await authAPI.me();
        set({ user, token, isLoading: false, hasCheckedAuth: true });
      } catch (error) {
        localStorage.removeItem('token');
        set({ user: null, token: null, isLoading: false, hasCheckedAuth: true });
      }
    },
  };
});
