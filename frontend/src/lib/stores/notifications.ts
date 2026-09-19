import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import { auth } from './auth';

export interface Notification {
  id: number;
  type: string;
  usuario_nombre: string;
  usuario_email: string;
  monto: number;
  inquilino_nombre: string;
  inmueble_direccion: string;
  timestamp: Date;
}

function createNotificationStore() {
  const { subscribe, update } = writable<Notification[]>([]);
  let nextId = 0;
  let eventSource: EventSource | null = null;

  function connect(token: string) {
    if (!browser || eventSource) return;

    eventSource = new EventSource(`http://localhost:8000/api/notifications/stream?token=${token}`);

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'connected') return;

        if (data.type === 'cobro_realizado') {
          update((notifications) => {
            const newNotification: Notification = {
              id: nextId++,
              ...data,
              timestamp: new Date(),
            };
            return [newNotification, ...notifications].slice(0, 20);
          });
        }
      } catch {
        // Ignore parse errors
      }
    };

    eventSource.onerror = () => {
      // Reconnect after 5 seconds
      disconnect();
      setTimeout(() => {
        if (browser && localStorage.getItem('auth')) {
          const stored = localStorage.getItem('auth');
          if (stored) {
            const authData = JSON.parse(stored);
            if (authData.token) connect(authData.token);
          }
        }
      }, 5000);
    };
  }

  function disconnect() {
    if (eventSource) {
      eventSource.close();
      eventSource = null;
    }
  }

  function dismiss(id: number) {
    update((notifications) => notifications.filter((n) => n.id !== id));
  }

  function clearAll() {
    update(() => []);
  }

  return {
    subscribe,
    connect,
    disconnect,
    dismiss,
    clearAll,
  };
}

export const notifications = createNotificationStore();

// Auto-connect when auth changes
if (browser) {
  auth.subscribe((state) => {
    if (state.token) {
      notifications.connect(state.token);
    } else {
      notifications.disconnect();
      notifications.clearAll();
    }
  });
}
