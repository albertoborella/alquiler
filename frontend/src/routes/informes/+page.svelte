<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { auth } from '$lib/stores/auth';

  onMount(() => {
    if (!$auth.token) goto('/login');
  });
</script>

<div class="max-w-7xl mx-auto px-4 md:px-6 lg:px-8 py-6 md:py-8">
  <div class="mb-6 md:mb-8">
    <h1 class="text-xl md:text-2xl font-bold text-gray-900 dark:text-gray-100">Informes</h1>
    <p class="text-gray-500 dark:text-gray-400 mt-1">Reportes y estadísticas del sistema</p>
  </div>

  <div class="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800 p-6 md:p-8">
    <div class="flex flex-col items-center justify-center py-16 text-center">
      <div class="w-16 h-16 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center mb-5">
        <svg class="w-8 h-8 text-primary-500 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      </div>
      <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">Próximamente</h2>
      <p class="text-sm text-gray-500 dark:text-gray-400 max-w-md">
        Estamos trabajando en los informes y reportes del sistema. Vas a poder generar reportes de cobros, inmuebles, propietarios y más.
      </p>
    </div>
  </div>
</div>
