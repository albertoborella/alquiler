import { writable } from 'svelte/store';
import { browser } from '$app/environment';

type Theme = 'light' | 'dark';

function createThemeStore() {
  const stored = browser ? (localStorage.getItem('theme') as Theme | null) : null;
  const prefersDark = browser ? window.matchMedia('(prefers-color-scheme: dark)').matches : false;
  const initial: Theme = stored ?? (prefersDark ? 'dark' : 'light');
  const { subscribe, set } = writable<Theme>(initial);

  function applyTheme(t: Theme) {
    if (!browser) return;
    document.documentElement.classList.toggle('dark', t === 'dark');
    localStorage.setItem('theme', t);
  }

  if (browser) applyTheme(initial);

  return {
    subscribe,
    toggle: () => {
      let current: Theme = initial;
      const unsub = subscribe((v) => (current = v));
      unsub();
      const next: Theme = current === 'dark' ? 'light' : 'dark';
      set(next);
      applyTheme(next);
    },
  };
}

export const theme = createThemeStore();
