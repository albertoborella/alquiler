import { writable } from 'svelte/store';

interface AppConfig {
  nombre_aplicacion: string;
  nombre_inmobiliaria: string;
  font_size_nombre_app: string;
  font_size_nombre_inmobiliaria: string;
}

const defaultConfig: AppConfig = {
  nombre_aplicacion: 'Alquiler App',
  nombre_inmobiliaria: '',
  font_size_nombre_app: '20',
  font_size_nombre_inmobiliaria: '14',
};

function createConfigStore() {
  const { subscribe, set, update } = writable<AppConfig>(defaultConfig);

  return {
    subscribe,
    async load() {
      try {
        const res = await fetch('http://localhost:8000/api/configuracion');
        if (!res.ok) return;
        const data: Record<string, string | null> = await res.json();
        const newValue: AppConfig = {
          nombre_aplicacion: data.nombre_aplicacion || defaultConfig.nombre_aplicacion,
          nombre_inmobiliaria: data.nombre_inmobiliaria || defaultConfig.nombre_inmobiliaria,
          font_size_nombre_app: data.font_size_nombre_app || defaultConfig.font_size_nombre_app,
          font_size_nombre_inmobiliaria: data.font_size_nombre_inmobiliaria || defaultConfig.font_size_nombre_inmobiliaria,
        };
        set(newValue);
      } catch {
        // Keep defaults on error
      }
    },
  };
}

export const appConfig = createConfigStore();
