<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { auth } from '$lib/stores/auth';
  import { api } from '$lib/api';
  import type { InmuebleDashboard, DashboardFilters } from '$lib/api';

  let inmuebles: InmuebleDashboard[] = [];
  let loading = true;
  let error = '';

  // Filters
  let filterPropietario = '';
  let filterInmueble = '';
  let filterEstado = '';
  let filterMorosos: '' | 'true' | 'false' = '';

  onMount(() => {
    if (!$auth.token) {
      goto('/login');
      return;
    }
    loadInmuebles();
  });

  async function loadInmuebles() {
    if (!$auth.token) return;
    loading = true;
    error = '';
    try {
      const f: DashboardFilters = {};
      if (filterEstado) f.estado = filterEstado;
      if (filterPropietario) f.propietario = filterPropietario;
      if (filterInmueble) f.inmueble = filterInmueble;
      if (filterMorosos === 'true') f.morosos = true;
      if (filterMorosos === 'false') f.morosos = false;
      inmuebles = await api.getDashboardInmuebles($auth.token, f);
    } catch (err) {
      error = err instanceof Error ? err.message : 'Error al cargar inmuebles';
    } finally {
      loading = false;
    }
  }

  function applyFilters() {
    loadInmuebles();
  }

  function clearFilters() {
    filterPropietario = '';
    filterInmueble = '';
    filterEstado = '';
    filterMorosos = '';
    loadInmuebles();
  }

  function formatCurrency(amount: number | null, currency: string | null): string {
    if (amount === null) return '-';
    const sym = currency === 'USD' ? 'US$' : '$';
    return `${sym} ${amount.toLocaleString('es-AR', { minimumFractionDigits: 0, maximumFractionDigits: 2 })}`;
  }

  function formatDate(dateStr: string | null): string {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('es-AR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  }

  function estadoBadgeClass(estado: string): string {
    return estado === 'alquilado'
      ? 'bg-primary-100 dark:bg-primary-900/40 text-primary-800 dark:text-primary-200'
      : 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200';
  }

  function estadoLabel(estado: string): string {
    return estado === 'alquilado' ? 'Alquilado' : 'Disponible';
  }

  function morosoBadgeClass(moroso: boolean): string {
    return moroso
      ? 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200'
      : 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200';
  }

  // Stats
  $: totalAlquilados = inmuebles.filter((i) => i.estado === 'alquilado').length;
  $: totalDisponibles = inmuebles.filter((i) => i.estado === 'disponible').length;
  $: totalMorosos = inmuebles.filter((i) => i.moroso).length;
</script>

<div class="space-y-6">
  <!-- Stats cards -->
  <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
    <div class="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800 p-4">
      <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Alquilados</p>
      <p class="text-2xl font-bold text-primary-600 mt-1">{totalAlquilados}</p>
    </div>
    <div class="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800 p-4">
      <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Disponibles</p>
      <p class="text-2xl font-bold text-green-600 mt-1">{totalDisponibles}</p>
    </div>
    <div class="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800 p-4">
      <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Morosos</p>
      <p class="text-2xl font-bold text-red-600 mt-1">{totalMorosos}</p>
    </div>
  </div>

  <!-- Filters -->
  <div class="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800 px-6 py-4">
    <div class="flex flex-wrap items-end gap-4">
      <div class="flex flex-col">
        <label for="filterInmueble" class="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Inmueble</label>
        <input
          id="filterInmueble"
          type="text"
          bind:value={filterInmueble}
          placeholder="Dirección..."
          class="px-3 py-1.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent w-48"
        />
      </div>
      <div class="flex flex-col">
        <label for="filterPropietario" class="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Propietario</label>
        <input
          id="filterPropietario"
          type="text"
          bind:value={filterPropietario}
          placeholder="Nombre..."
          class="px-3 py-1.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent w-48"
        />
      </div>
      <div class="flex flex-col">
        <label for="filterEstado" class="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Estado</label>
        <select
          id="filterEstado"
          bind:value={filterEstado}
          class="px-3 py-1.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        >
          <option value="">Todos</option>
          <option value="alquilado">Alquilado</option>
          <option value="disponible">Disponible</option>
        </select>
      </div>
      <div class="flex flex-col">
        <label for="filterMorosos" class="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Morosos</label>
        <select
          id="filterMorosos"
          bind:value={filterMorosos}
          class="px-3 py-1.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        >
          <option value="">Todos</option>
          <option value="true">Solo morosos</option>
          <option value="false">No morosos</option>
        </select>
      </div>
      <button
        on:click={applyFilters}
        class="px-4 py-1.5 rounded-lg bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium transition-colors cursor-pointer"
      >
        Filtrar
      </button>
      <button
        on:click={clearFilters}
        class="px-4 py-1.5 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 text-sm font-medium transition-colors cursor-pointer"
      >
        Limpiar
      </button>
    </div>
  </div>

  <!-- Table -->
  <div class="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800">
    {#if error}
      <div class="px-6 py-3 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 text-sm border-b border-red-100 dark:border-red-900/30">
        {error}
      </div>
    {/if}

    {#if loading}
      <div class="p-6 space-y-3">
        {#each Array(5) as _}
          <div class="flex gap-4 animate-pulse">
            <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/5"></div>
            <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/6"></div>
            <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/6"></div>
            <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/8"></div>
            <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/8"></div>
          </div>
        {/each}
      </div>
    {:else if inmuebles.length === 0}
      <!-- Empty state with alert -->
      <div class="px-6 py-16 text-center">
        <div class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg px-6 py-5 max-w-md mx-auto mb-6">
          <div class="flex items-center gap-3">
            <svg class="w-5 h-5 text-amber-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <p class="text-sm text-amber-700 dark:text-amber-300 font-medium">No hay inmuebles cargados</p>
          </div>
          <p class="text-xs text-amber-600 dark:text-amber-400 mt-2">
            Cargá los primeros inmuebles para verlos en el dashboard.
          </p>
        </div>
        <svg class="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
        </svg>
        <p class="text-gray-500 dark:text-gray-400 text-sm">No se encontraron inmuebles</p>
      </div>
    {:else}
      <div class="overflow-x-auto -mx-4 md:mx-0">
        <table class="w-full min-w-[640px]">
          <thead>
            <tr class="text-left text-[11px] font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider border-b border-gray-100 dark:border-gray-800">
              <th class="px-3 md:px-4 py-1">Dirección</th>
              <th class="px-3 md:px-4 py-1 hidden sm:table-cell">Propietario(s)</th>
              <th class="px-3 md:px-4 py-1">Estado</th>
              <th class="px-3 md:px-4 py-1 hidden lg:table-cell">Inquilino</th>
              <th class="px-3 md:px-4 py-1 hidden sm:table-cell">Monto</th>
              <th class="px-3 md:px-4 py-1 hidden md:table-cell">Vencimiento</th>
              <th class="px-3 md:px-4 py-1">Moroso</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50 dark:divide-gray-800">
            {#each inmuebles as inm (inm.id)}
              <tr class="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                <td class="px-3 md:px-4 py-1">
                  <div class="text-xs font-medium text-gray-900 dark:text-gray-100">{inm.direccion}</div>
                  <div class="text-[11px] text-gray-400 dark:text-gray-500 mt-0.5 sm:hidden">
                    {inm.categoria}{inm.superficie ? ` · ${inm.superficie} m²` : ''}
                  </div>
                </td>
                <td class="px-3 md:px-4 py-1 text-xs text-gray-600 dark:text-gray-400 hidden sm:table-cell">
                  {#if inm.propietarios.length > 0}
                    {#each inm.propietarios as prop, i}{prop.nombre}{i < inm.propietarios.length - 1 ? ', ' : ''}{/each}
                  {:else}
                    <span class="text-gray-400">-</span>
                  {/if}
                </td>
                <td class="px-3 md:px-4 py-1">
                  <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium {estadoBadgeClass(inm.estado)}">
                    {estadoLabel(inm.estado)}
                  </span>
                </td>
                <td class="px-3 md:px-4 py-1 text-xs text-gray-600 dark:text-gray-400 hidden lg:table-cell">
                  {#if inm.inquilino}
                    {inm.inquilino.nombre}
                  {:else}
                    <span class="text-gray-400">-</span>
                  {/if}
                </td>
                <td class="px-3 md:px-4 py-1 text-xs text-gray-600 dark:text-gray-400 hidden sm:table-cell">
                  {#if inm.contrato}
                    {formatCurrency(inm.contrato.monto_base, inm.contrato.moneda)}
                  {:else}
                    <span class="text-gray-400">-</span>
                  {/if}
                </td>
                <td class="px-3 md:px-4 py-1 text-xs text-gray-500 dark:text-gray-400 hidden md:table-cell">
                  {#if inm.contrato}
                    {formatDate(inm.contrato.fecha_fin)}
                  {:else}
                    <span class="text-gray-400">-</span>
                  {/if}
                </td>
                <td class="px-3 md:px-4 py-1">
                  <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium {morosoBadgeClass(inm.moroso)}">
                    {inm.moroso ? 'Sí' : 'No'}
                  </span>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </div>
</div>
