import { writable } from 'svelte/store';
import { browser } from '$app/environment';

interface AuthState {
  token: string | null;
  user: {
    id: string;
    email: string;
    full_name: string | null;
    role: string;
  } | null;
}

function createAuthStore() {
  const stored = browser ? localStorage.getItem('auth') : null;
  const initial: AuthState = stored ? JSON.parse(stored) : { token: null, user: null };
  const { subscribe, set } = writable<AuthState>(initial);

  return {
    subscribe,
    login: (token: string, user: AuthState['user']) => {
      const state = { token, user };
      if (browser) localStorage.setItem('auth', JSON.stringify(state));
      set(state);
    },
    logout: () => {
      if (browser) localStorage.removeItem('auth');
      set({ token: null, user: null });
    },
  };
}

export const auth = createAuthStore();
