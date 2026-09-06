<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { auth } from '$lib/stores/auth';

  const API_URL = 'http://localhost:8000/api';

  let nombreApp = '';
  let nombreInmobiliaria = '';
  let fontSizeApp = '20';
  let fontSizeInmobiliaria = '14';
  let loading = true;
  let saving = false;
  let success = '';
  let error = '';

  onMount(async () => {
    if (!$auth.token || $auth.user?.role !== 'admin') {
      goto('/login');
      return;
    }
    try {
      const res = await fetch(`${API_URL}/configuracion`, { cache: 'no-store' });
      if (res.ok) {
        const data = await res.json();
        nombreApp = data.nombre_aplicacion || '';
        nombreInmobiliaria = data.nombre_inmobiliaria || '';
        fontSizeApp = data.font_size_nombre_app || '20';
        fontSizeInmobiliaria = data.font_size_nombre_inmobiliaria || '14';
      }
    } catch (e) {
      console.error('Error loading config:', e);
    } finally {
      loading = false;
    }
  });

  async function save() {
    if (!$auth.token) {
      console.error('[ConfigPage] No auth token');
      return;
    }
    saving = true;
    success = '';
    error = '';
    try {
      const payload = {
        items: {
          nombre_aplicacion: nombreApp || null,
          nombre_inmobiliaria: nombreInmobiliaria || null,
          font_size_nombre_app: String(fontSizeApp || '20'),
          font_size_nombre_inmobiliaria: String(fontSizeInmobiliaria || '14'),
        },
      };
      console.log('[ConfigPage] Saving:', JSON.stringify(payload));
      const res = await fetch(`${API_URL}/configuracion`, {
        method: 'PUT',
        cache: 'no-store',
        headers: {
          'Content-Type': 'application/json',
          'X-Access-Token': $auth.token,
        },
        body: JSON.stringify(payload),
      });
      console.log('[ConfigPage] Response status:', res.status);
      if (!res.ok) {
        const errBody = await res.json().catch(() => null);
        console.error('[ConfigPage] Error body:', errBody);
        const msg = errBody?.detail || `Error ${res.status}`;
        throw new Error(typeof msg === 'string' ? msg : JSON.stringify(msg));
      }
      const result = await res.json();
      console.log('[ConfigPage] Saved:', JSON.stringify(result));
      success = 'Configuración guardada correctamente';
      setTimeout(() => window.location.reload(), 600);
    } catch (e) {
      console.error('[ConfigPage] Caught:', e);
      error = e instanceof Error ? e.message : String(e);
    } finally {
      saving = false;
    }
  }
</script>

<div class="max-w-2xl mx-auto">
  <div class="mb-6">
    <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">Configuración</h1>
    <p class="text-gray-500 dark:text-gray-400 mt-1">Ajustes generales del sistema</p>
  </div>

  {#if loading}
    <div class="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800 p-6">
      <div class="animate-pulse space-y-4">
        <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/3"></div>
        <div class="h-10 bg-gray-200 dark:bg-gray-700 rounded w-full"></div>
      </div>
    </div>
  {:else}
    <form on:submit|preventDefault={save} class="space-y-6">
      {#if success}
        <div class="bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-300 text-sm rounded-lg px-4 py-3 border border-emerald-100 dark:border-emerald-800">
          {success}
        </div>
      {/if}

      {#if error}
        <div class="bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 text-sm rounded-lg px-4 py-3 border border-red-100 dark:border-red-800">
          {error}
        </div>
      {/if}

      <!-- Nombre de la aplicación -->
      <div class="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800">
        <div class="px-6 py-4 border-b border-gray-100 dark:border-gray-800">
          <h2 class="text-sm font-semibold text-gray-900 dark:text-gray-100">Nombre de la aplicación</h2>
        </div>
        <div class="p-6">
          <label for="nombre-app" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Nombre de la aplicación
          </label>
          <input
            id="nombre-app"
            type="text"
            bind:value={nombreApp}
            placeholder="Alquiler App"
            class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Nombre que se muestra en la barra de navegación.
          </p>
        </div>
      </div>

      <!-- Nombre de la inmobiliaria -->
      <div class="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800">
        <div class="px-6 py-4 border-b border-gray-100 dark:border-gray-800">
          <h2 class="text-sm font-semibold text-gray-900 dark:text-gray-100">Nombre de la inmobiliaria</h2>
        </div>
        <div class="p-6">
          <label for="nombre-inmobiliaria" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Nombre de la inmobiliaria
          </label>
          <input
            id="nombre-inmobiliaria"
            type="text"
            bind:value={nombreInmobiliaria}
            placeholder="Ej: Inmobiliaria López & Asociados"
            class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Se muestra junto al nombre de la aplicación.
          </p>
        </div>
      </div>

      <!-- Tipografía -->
      <div class="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800">
        <div class="px-6 py-4 border-b border-gray-100 dark:border-gray-800">
          <h2 class="text-sm font-semibold text-gray-900 dark:text-gray-100">Tipografía</h2>
        </div>
        <div class="p-6">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label for="font-size-app" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Tamaño fuente nombre app (px)
              </label>
              <input
                id="font-size-app"
                type="number"
                min="12"
                max="32"
                bind:value={fontSizeApp}
                class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
            <div>
              <label for="font-size-inmobiliaria" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Tamaño fuente inmobiliaria (px)
              </label>
              <input
                id="font-size-inmobiliaria"
                type="number"
                min="10"
                max="24"
                bind:value={fontSizeInmobiliaria}
                class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </div>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-3">
            Poppins es la tipografía del sistema. Se aplica en la barra de navegación.
          </p>
        </div>
      </div>

      <div class="flex justify-end">
        <button
          type="submit"
          disabled={saving}
          class="px-4 py-2 bg-primary-600 hover:bg-primary-700 disabled:bg-primary-400 text-white text-sm font-medium rounded-lg transition-colors cursor-pointer disabled:cursor-not-allowed"
        >
          {saving ? 'Guardando...' : 'Guardar'}
        </button>
      </div>
    </form>
  {/if}
</div>
