<script lang="ts">
  import '../app.css';
  import { auth } from '$lib/stores/auth';
  import { theme } from '$lib/stores/theme';
  import { sidebar } from '$lib/stores/sidebar';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import Sidebar from '$lib/components/Sidebar.svelte';
  import { onMount } from 'svelte';
  import { browser } from '$app/environment';
  import { notifications } from '$lib/stores/notifications';
  import type { Notification } from '$lib/stores/notifications';

  // ── Inactivity timer (30 min) ──
  const INACTIVITY_TIMEOUT = 30 * 60 * 1000;
  let inactivityTimer: ReturnType<typeof setTimeout> | null = null;

  function resetInactivityTimer() {
    if (!browser) return;
    if (inactivityTimer) clearTimeout(inactivityTimer);
    if ($auth.token) {
      inactivityTimer = setTimeout(() => {
        auth.logout();
        alert('Se cerró tu sesión por inactividad. Por favor, iniciá sesión nuevamente.');
        goto('/login');
      }, INACTIVITY_TIMEOUT);
    }
  }

  function handleActivity() {
    if ($auth.token) resetInactivityTimer();
  }

  $: if ($auth.token) {
    resetInactivityTimer();
  } else if (browser) {
    if (inactivityTimer) clearTimeout(inactivityTimer);
  }

  // ── Config ──
  let nombreApp = 'Alquiler App';
  let nombreInmobiliaria = '';
  let fontSizeApp = '20';
  let fontSizeInmobiliaria = '14';

  async function loadConfig() {
    if (!browser) return;
    try {
      const res = await fetch('http://localhost:8000/api/configuracion', {
        cache: 'no-store',
      });
      if (!res.ok) {
        console.error('[Config] HTTP error:', res.status);
        return;
      }
      const data = await res.json();
      console.log('[Config] Loaded:', JSON.stringify(data));
      nombreApp = data.nombre_aplicacion || 'Alquiler App';
      nombreInmobiliaria = data.nombre_inmobiliaria || '';
      fontSizeApp = data.font_size_nombre_app || '20';
      fontSizeInmobiliaria = data.font_size_nombre_inmobiliaria || '14';
      console.log('[Config] Applied - nombreApp:', nombreApp, 'fontSize:', fontSizeApp);
    } catch (e) {
      console.error('[Config] fetch error:', e);
    }
  }

  const activityEvents = ['mousedown', 'keydown', 'scroll', 'touchstart'];

  onMount(() => {
    loadConfig();
    activityEvents.forEach(event => document.addEventListener(event, handleActivity, { passive: true }));
    resetInactivityTimer();

    return () => {
      activityEvents.forEach(event => document.removeEventListener(event, handleActivity));
      if (inactivityTimer) clearTimeout(inactivityTimer);
    };
  });

  let mobileMenuOpen = false;

  function toggleMenu() {
    mobileMenuOpen = !mobileMenuOpen;
  }

  function closeMenu() {
    mobileMenuOpen = false;
  }

  function logout() {
    if (inactivityTimer) clearTimeout(inactivityTimer);
    auth.logout();
    goto('/login');
  }

  function getInitials(name: string | null, email: string): string {
    if (name) {
      return name
        .split(' ')
        .map((n) => n[0])
        .join('')
        .toUpperCase()
        .slice(0, 2);
    }
    return email.charAt(0).toUpperCase();
  }

  $: showSidebar = !!$auth.token && $page.url.pathname !== '/login' && $page.url.pathname !== '/register';
  $: isAdmin = $auth.user?.role === 'admin';

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Escape') {
      notifications.clearAll();
    }
  }

  function formatCurrency(amount: number): string {
    return `$ ${amount.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  }
</script>

<svelte:window on:keydown={handleKeydown} />

<div class="min-h-screen flex flex-col">
  <!-- Navbar -->
  <nav class="bg-white dark:bg-gray-900 shadow-sm fixed w-full top-0 z-50 border-b border-gray-100 dark:border-gray-800">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <div class="flex items-center">
          {#if showSidebar}
            <button
              on:click={() => sidebar.toggle()}
              class="p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors cursor-pointer"
              title="Mostrar/ocultar menú"
              aria-label="Mostrar/ocultar menú"
            >
              {#if $sidebar}
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5h18M3 12h18M3 19h12" />
                </svg>
              {:else}
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h10M4 18h16" />
                </svg>
              {/if}
            </button>
          {/if}
          <a href="/" class="flex items-center gap-2" on:click={closeMenu}>
            <svg class="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            <span class="font-poppins font-bold text-primary-600" style="font-size: {fontSizeApp}px">
              {nombreApp}{#if nombreInmobiliaria} <span style="font-size: {fontSizeInmobiliaria}px; font-weight: 500">- {nombreInmobiliaria}</span>{/if}
            </span>
          </a>
        </div>

        <div class="hidden sm:flex sm:items-center sm:gap-4">
          {#if $auth.token}
            <button
              on:click={() => theme.toggle()}
              class="p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors cursor-pointer"
              title={$theme === 'dark' ? 'Modo claro' : 'Modo oscuro'}
              aria-label={$theme === 'dark' ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
            >
              {#if $theme === 'dark'}
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              {:else}
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                </svg>
              {/if}
            </button>

            <div class="flex items-center gap-3 ml-2">
              <div class="w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900/40 text-primary-700 dark:text-primary-300 flex items-center justify-center text-sm font-semibold">
                {getInitials($auth.user?.full_name ?? null, $auth.user?.email ?? '')}
              </div>
              <span class="text-sm text-gray-700 dark:text-gray-300">
                {$auth.user?.full_name || $auth.user?.email}
              </span>
              <button
                on:click={logout}
                class="text-sm text-gray-500 dark:text-gray-400 hover:text-red-600 dark:hover:text-red-400 transition-colors cursor-pointer"
              >
                Salir
              </button>
            </div>
          {:else}
            <a href="/login" class="text-gray-600 dark:text-gray-400 hover:text-primary-600 px-3 py-2 text-sm font-medium transition-colors">
              Iniciar Sesión
            </a>
          {/if}
        </div>

        <div class="flex items-center gap-2 sm:hidden">
          {#if $auth.token}
            <button
              on:click={() => theme.toggle()}
              class="p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors cursor-pointer"
              aria-label="Cambiar tema"
            >
              {#if $theme === 'dark'}
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              {:else}
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                </svg>
              {/if}
            </button>
          {/if}
          <button
            on:click={toggleMenu}
            class="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 p-2 cursor-pointer"
            aria-label="Menú"
          >
            {#if mobileMenuOpen}
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            {:else}
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            {/if}
          </button>
        </div>
      </div>
    </div>

    {#if mobileMenuOpen}
      <div class="sm:hidden border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
        <div class="px-4 py-3 space-y-2">
          {#if $auth.token}
            <div class="flex items-center gap-3 px-3 py-2">
              <div class="w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900/40 text-primary-700 dark:text-primary-300 flex items-center justify-center text-sm font-semibold">
                {getInitials($auth.user?.full_name ?? null, $auth.user?.email ?? '')}
              </div>
              <span class="text-sm text-gray-700 dark:text-gray-300">
                {$auth.user?.full_name || $auth.user?.email}
              </span>
            </div>
            <button
              on:click={() => { closeMenu(); logout(); }}
              class="block w-full text-left px-3 py-2 rounded-md text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 text-sm font-medium cursor-pointer"
            >
              Salir
            </button>
          {:else}
            <a href="/login" class="block px-3 py-2 rounded-md text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 text-sm font-medium" on:click={closeMenu}>
              Iniciar Sesión
            </a>
          {/if}
        </div>
      </div>
    {/if}
  </nav>

  {#if showSidebar}
    <Sidebar />
  {/if}

  <main class="flex-1 pt-16 {showSidebar ? ($sidebar ? 'md:ml-12' : 'md:ml-36') : ''}">
    <div class="p-4 md:p-6">
      <slot />
    </div>
  </main>

  <!-- Notification toasts (admin only) -->
  {#if isAdmin && $notifications.length > 0}
    <div class="fixed top-20 right-4 z-[100] flex flex-col gap-3 max-w-sm w-full pointer-events-none">
      {#if $notifications.length > 1}
        <div class="pointer-events-auto flex justify-end">
          <button
            on:click={() => notifications.clearAll()}
            class="text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-1.5 shadow-sm cursor-pointer"
          >
            Limpiar todo ({$notifications.length})
          </button>
        </div>
      {/if}
      {#each $notifications as notif (notif.id)}
        <div
          class="pointer-events-auto bg-white dark:bg-gray-900 border border-emerald-200 dark:border-emerald-800 rounded-xl shadow-lg p-4 animate-slide-in"
          role="alert"
        >
          <div class="flex items-start gap-3">
            <div class="w-9 h-9 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center shrink-0 mt-0.5">
              <svg class="w-5 h-5 text-emerald-600 dark:text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-emerald-700 dark:text-emerald-300">Cobro realizado</p>
              <div class="mt-1 space-y-0.5">
                <p class="text-sm text-gray-700 dark:text-gray-300">
                  <span class="font-medium">Importe:</span> {formatCurrency(notif.monto)}
                </p>
                <p class="text-sm text-gray-700 dark:text-gray-300">
                  <span class="font-medium">Inquilino:</span> {notif.inquilino_nombre}
                </p>
                <p class="text-sm text-gray-700 dark:text-gray-300">
                  <span class="font-medium">Inmueble:</span> {notif.inmueble_direccion}
                </p>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Registrado por: {notif.usuario_nombre}
                </p>
              </div>
            </div>
            <button
              on:click={() => notifications.dismiss(notif.id)}
              class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 shrink-0 cursor-pointer"
              aria-label="Cerrar"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>
