import { writable } from 'svelte/store';
import { browser } from '$app/environment';

type Collapsed = boolean;

function createSidebarStore() {
  const stored = browser ? localStorage.getItem('sidebar-collapsed') : null;
  const initial: Collapsed = stored === null ? false : stored === 'true';
  const { subscribe, set } = writable<Collapsed>(initial);

  function persist(value: Collapsed) {
    if (!browser) return;
    localStorage.setItem('sidebar-collapsed', String(value));
  }

  if (browser) persist(initial);

  return {
    subscribe,
    toggle: () => {
      let current: Collapsed = initial;
      const unsub = subscribe((v) => (current = v));
      unsub();
      const next: Collapsed = !current;
      set(next);
      persist(next);
    },
    set: (value: Collapsed) => {
      set(value);
      persist(value);
    },
  };
}

export const sidebar = createSidebarStore();
