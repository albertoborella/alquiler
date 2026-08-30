<script lang="ts">
  import { page } from '$app/stores';
  import { sidebar } from '$lib/stores/sidebar';

  interface NavItem {
    label: string;
    href: string;
    icon: string;
  }

  const navItems: NavItem[] = [
    {
      label: 'Inmuebles urbanos',
      href: '/inmuebles',
      icon: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4',
    },
    {
      label: 'Inmuebles rurales',
      href: '/inmuebles/rural',
      icon: 'M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H17a2 2 0 012 2v14m-14-4h14M8 7h3m1 4h3m-6 4h5M5 21h14',
    },
    {
      label: 'Propietarios',
      href: '/propietarios',
      icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z',
    },
    {
      label: 'Inquilinos',
      href: '/inquilinos',
      icon: 'M12 4.354a4 4 0 110 7.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z',
    },
    {
      label: 'Contratos',
      href: '/contratos',
      icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
    },
    {
      label: 'Cobros',
      href: '/cobros',
      icon: 'M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z',
    },
    {
      label: 'Usuarios',
      href: '/users',
      icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z',
    },
  ];

  $: currentPath = $page.url.pathname;

  // `currentPath` must be passed as an argument so Svelte treats it as a template
  // dependency. Calling a function that reads reactive state WITHOUT passing it as
  // an argument does NOT re-evaluate on navigation, leaving the highlight stuck.
  function isActive(path: string, item: NavItem): boolean {
    // /inmuebles must not highlight when on /inmuebles/rural
    if (item.href === '/inmuebles') {
      return path === '/inmuebles';
    }
    return path.startsWith(item.href);
  }
</script>

<!-- Desktop sidebar: fixed, hidden on mobile -->
<aside
  class="hidden md:flex {$sidebar ? 'w-12' : 'w-36'} bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 pt-14 min-h-screen fixed left-0 top-0 z-40 flex-col transition-all duration-200"
>
  <nav class="flex-1 px-1.5 py-3 space-y-0.5">
    {#each navItems as item}
      <a
        href={item.href}
        class="flex items-center {$sidebar ? 'justify-center' : 'gap-2.5 px-2.5'} py-1.5 rounded-lg text-xs font-normal transition-colors
          {isActive(currentPath, item)
            ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300'
            : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100'}"
        title={$sidebar ? item.label : undefined}
      >
        <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="1.5"
            d={item.icon}
          />
        </svg>
        {#if !$sidebar}
          {item.label}
        {/if}
      </a>
    {/each}
  </nav>

  <div class="px-1.5 py-3 border-t border-gray-200 dark:border-gray-800">
    <button
      on:click={() => sidebar.toggle()}
      class="w-full flex items-center {$sidebar ? 'justify-center' : 'gap-2.5'} px-2 py-1.5 rounded-lg text-xs font-normal text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100 transition-colors cursor-pointer"
      title={$sidebar ? 'Expandir menú' : 'Contraer menú'}
      aria-label={$sidebar ? 'Expandir menú' : 'Contraer menú'}
    >
      <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        {#if $sidebar}
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        {:else}
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        {/if}
      </svg>
      {#if !$sidebar}
        Contraer menú
      {/if}
    </button>
    {#if !$sidebar}
      <p class="text-[11px] text-gray-400 px-2 pt-1">Alquiler App v0.1</p>
    {/if}
  </div>
</aside>
