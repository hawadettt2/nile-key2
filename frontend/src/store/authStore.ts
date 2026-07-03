import { create } from 'zustand';
import { login as apiLogin, register as apiRegister, getMe, updateMe, refreshToken as apiRefreshToken } from '@/services/api';

interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  role: string;
  phone?: string;
  company?: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (username: string, password: string) => Promise<void>;
  register: (data: Record<string, string>) => Promise<void>;
  logout: () => void;
  loadUser: () => Promise<void>;
  clearError: () => void;
  updateProfile: (data: { full_name?: string; email?: string; phone?: string; company?: string }) => Promise<void>;
  refreshTokens: () => Promise<boolean>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  login: async (username: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiLogin(username, password);
      const { access_token, refresh_token } = response.data;
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      const meRes = await getMe();
      set({ user: meRes.data, isAuthenticated: true, isLoading: false });
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      set({ error: error.response?.data?.detail || 'Login failed', isLoading: false });
    }
  },

  register: async (data: Record<string, string>) => {
    set({ isLoading: true, error: null });
    try {
      await apiRegister(data);
      set({ isLoading: false });
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      set({ error: error.response?.data?.detail || 'Registration failed', isLoading: false });
    }
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    set({ user: null, isAuthenticated: false, error: null });
    window.location.href = '/login';
  },

  loadUser: async () => {
    const token = localStorage.getItem('access_token');
    if (!token) { set({ isAuthenticated: false, isLoading: false }); return; }
    set({ isLoading: true });
    try {
      const response = await getMe();
      set({ user: response.data, isAuthenticated: true, isLoading: false });
    } catch {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },

  refreshTokens: async () => {
    const storedRefreshToken = localStorage.getItem('refresh_token');
    if (!storedRefreshToken) return false;
    try {
      const response = await apiRefreshToken({ refresh_token: storedRefreshToken });
      const { access_token, refresh_token } = response.data;
      localStorage.setItem('access_token', access_token);
      if (refresh_token) localStorage.setItem('refresh_token', refresh_token);
      return true;
    } catch {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      set({ user: null, isAuthenticated: false });
      return false;
    }
  },

  updateProfile: async (data) => {
    set({ isLoading: true, error: null });
    try {
      await updateMe(data);
      const meRes = await getMe();
      set({ user: meRes.data, isLoading: false });
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      set({ error: error.response?.data?.detail || 'Update failed', isLoading: false });
    }
  },

  clearError: () => set({ error: null }),
}));
