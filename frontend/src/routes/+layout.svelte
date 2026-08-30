<script lang="ts">
  import '../app.css';
  import { auth } from '$lib/stores/auth';
  import { theme } from '$lib/stores/theme';
  import { sidebar } from '$lib/stores/sidebar';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import Sidebar from '$lib/components/Sidebar.svelte';

  let mobileMenuOpen = false;

  function toggleMenu() {
    mobileMenuOpen = !mobileMenuOpen;
  }

  function closeMenu() {
    mobileMenuOpen = false;
  }

  function logout() {
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
</script>

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
            <span class="text-xl font-bold text-primary-600">Alquiler App</span>
          </a>
        </div>

        <div class="hidden sm:flex sm:items-center sm:gap-4">
          {#if $auth.token}
            <!-- Dark mode toggle -->
            <button
              on:click={() => theme.toggle()}
              class="p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors cursor-pointer"
              title={$theme === 'dark' ? 'Modo claro' : 'Modo oscuro'}
              aria-label={$theme === 'dark' ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
            >
              {#if $theme === 'dark'}
                <!-- Sun icon -->
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              {:else}
                <!-- Moon icon -->
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
            <a href="/register" class="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
              Registrarse
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
            <a href="/register" class="block px-3 py-2 rounded-md bg-primary-600 text-white text-sm font-medium text-center" on:click={closeMenu}>
              Registrarse
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
</div>
