<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { auth } from '$lib/stores/auth';
  import { api } from '$lib/api';
  import type { CobroPublic, ContratoDash, InmueblePublic, Propietario } from '$lib/api';

  let allCobros: CobroPublic[] = [];
  let contratos: ContratoDash[] = [];
  let inmuebles: InmueblePublic[] = [];
  let propietarios: Propietario[] = [];
  let loading = true;
  let error = '';

  // ── Filters ──
  let filterPropietario = '';
  let filterInmueble = '';
  let filterFechaInicio = '';
  let filterFechaFin = '';

  // ── Delete modal ──
  let showDeleteConfirm = false;
  let deleteTarget: CobroPublic | null = null;
  let deleting = false;

  $: isAdmin = $auth.user?.role === 'admin';

  // Build lookup maps
  let contratoMap = new Map<string, ContratoDash>();
  let inmuebleMap = new Map<string, InmueblePublic>();
  let propietarioByInmueble = new Map<string, string>(); // inmueble_id -> propietario nombre(s)

  $: enrichedCobros = allCobros.map((c) => {
    const contrato = contratoMap.get(c.contrato_id);
    const inmueble = contrato ? inmuebleMap.get(contrato.inmueble_id) : undefined;
    const propietario = contrato ? propietarioByInmueble.get(contrato.inmueble_id) : undefined;
    return {
      ...c,
      inmuebleDireccion: inmueble?.direccion || '-',
      inmuebleId: contrato?.inmueble_id || '',
      propietarioNombre: propietario || '-',
    };
  }).filter((c) => {
    if (filterPropietario && c.propietarioNombre === '-') return false;
    if (filterPropietario && !c.propietarioNombre.toLowerCase().includes(filterPropietario.toLowerCase())) return false;
    if (filterInmueble && c.inmuebleId !== filterInmueble) return false;
    return true;
  });

  $: filteredInmuebles = filterPropietario
    ? inmuebles.filter((inm) => {
        const propNames = propietarioByInmueble.get(inm.id) || '';
        return propNames.toLowerCase().includes(filterPropietario.toLowerCase());
      })
    : inmuebles;

  onMount(() => {
    if (!$auth.token) {
      goto('/login');
      return;
    }
    loadData();
  });

  async function loadData() {
    if (!$auth.token) return;
    loading = true;
    error = '';
    try {
      const [cobrosData, contratosData, inmueblesData, propietariosData] = await Promise.all([
        api.getCobros($auth.token, {
          fecha_inicio: filterFechaInicio || undefined,
          fecha_fin: filterFechaFin || undefined,
        }),
        api.getContratos($auth.token),
        api.getInmuebles($auth.token),
        api.getPropietarios($auth.token),
      ]);

      allCobros = cobrosData;
      contratos = contratosData;
      inmuebles = inmueblesData;
      propietarios = propietariosData;

      // Build maps
      contratoMap = new Map(contratos.map((c) => [c.id, c]));
      inmuebleMap = new Map(inmuebles.map((i) => [i.id, i]));

      // Build propietario-by-inmueble map by loading copropiedad for each inmueble
      // that has cobros. This is more reliable than the dashboard endpoint.
      const inmuebleIdsConCobros = new Set<string>();
      for (const c of allCobros) {
        const contrato = contratoMap.get(c.contrato_id);
        if (contrato) inmuebleIdsConCobros.add(contrato.inmueble_id);
      }

      const newPropMap = new Map<string, string>();
      const propPromises = Array.from(inmuebleIdsConCobros).map(async (inmId) => {
        try {
          const coprops = await api.getPropietariosByInmueble($auth.token, inmId);
          if (coprops.length > 0) {
            // coprops are CopropiedadPublic[] with {propietario_id, porcentaje_participacion}
            // Match propietario_id against the loaded propietarios list to get names
            const names = coprops.map((cp) => {
              const full = propietarios.find((p) => p.id === cp.propietario_id);
              return full?.nombre || 'Desconocido';
            }).join(', ');
            newPropMap.set(inmId, names);
          }
        } catch {
          // Individual inmueble copropiedad load failed — skip
        }
      });
      await Promise.all(propPromises);
      propietarioByInmueble = newPropMap;
    } catch (err) {
      error = err instanceof Error ? err.message : 'Error al cargar cobros';
    } finally {
      loading = false;
    }
  }

  function handleDateFilter() {
    loadData();
  }

  function clearFilters() {
    filterPropietario = '';
    filterInmueble = '';
    filterFechaInicio = '';
    filterFechaFin = '';
    loadData();
  }

  function formatCurrency(amount: number | null, currency: string | null): string {
    if (amount === null || amount === undefined) return '-';
    const sym = currency === 'USD' ? 'US$' : '$';
    return `${sym} ${amount.toLocaleString('es-AR', { minimumFractionDigits: 0, maximumFractionDigits: 2 })}`;
  }

  function confirmDelete(c: CobroPublic) {
    deleteTarget = c;
    showDeleteConfirm = true;
  }

  async function submitDelete() {
    if (!$auth.token || !deleteTarget) return;
    deleting = true;
    try {
      await api.deleteCobro($auth.token, deleteTarget.id);
      allCobros = allCobros.filter((c) => c.id !== deleteTarget!.id);
      showDeleteConfirm = false;
      deleteTarget = null;
    } catch (err) {
      error = err instanceof Error ? err.message : 'Error al eliminar cobro';
    } finally {
      deleting = false;
    }
  }

  function formatDate(dateStr: string | null): string {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('es-AR', { day: '2-digit', month: '2-digit', year: 'numeric' });
  }
</script>

<div class="max-w-7xl mx-auto px-4 md:px-6 lg:px-8 py-6 md:py-8">
  <div class="mb-6 md:mb-8">
    <h1 class="text-xl md:text-2xl font-bold text-gray-900 dark:text-gray-100">Cobros</h1>
    <p class="text-gray-500 dark:text-gray-400 mt-1">Historial de cobros de todos los alquileres</p>
  </div>

  <div class="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800">
    <!-- Filters bar -->
    <div class="px-4 md:px-6 py-3 border-b border-gray-100 dark:border-gray-800">
      <div class="flex flex-wrap items-end gap-3">
        <!-- Propietario filter -->
        <div>
          <label for="filterProp" class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Propietario</label>
          <input id="filterProp" type="text" bind:value={filterPropietario} placeholder="Buscar..."
            class="px-3 py-1.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent w-40" />
        </div>

        <!-- Inmueble filter -->
        <div>
          <label for="filterInm" class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Inmueble</label>
          <select id="filterInm" bind:value={filterInmueble}
            class="px-3 py-1.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent">
            <option value="">Todos</option>
            {#each filteredInmuebles as inm}
              <option value={inm.id}>{inm.direccion}</option>
            {/each}
          </select>
        </div>

        <!-- Date range -->
        <div>
          <label for="filterFechaInicio" class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Desde</label>
          <input id="filterFechaInicio" type="date" bind:value={filterFechaInicio}
            class="px-3 py-1.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
        </div>
        <div>
          <label for="filterFechaFin" class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Hasta</label>
          <input id="filterFechaFin" type="date" bind:value={filterFechaFin}
            class="px-3 py-1.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
        </div>

        <button on:click={handleDateFilter}
          class="px-3 py-1.5 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors cursor-pointer">
          Filtrar fechas
        </button>

        <button on:click={clearFilters}
          class="px-3 py-1.5 text-sm font-medium text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors cursor-pointer">
          Limpiar
        </button>

        <p class="ml-auto text-sm text-gray-500 dark:text-gray-400">
          {enrichedCobros.length} cobro{enrichedCobros.length !== 1 ? 's' : ''}
        </p>
      </div>
    </div>

    {#if error}
      <div class="px-4 md:px-6 py-3 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 text-sm border-b border-red-100 dark:border-red-900/30">
        {error}
      </div>
    {/if}

    {#if loading}
      <div class="p-6 space-y-3">
        {#each Array(5) as _}
          <div class="flex gap-4 animate-pulse">
            <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/6"></div>
            <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/5"></div>
            <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/4"></div>
            <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/6"></div>
          </div>
        {/each}
      </div>
    {:else if enrichedCobros.length === 0}
      <div class="px-6 py-16 text-center">
        <div class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg px-6 py-5 max-w-md mx-auto mb-6">
          <div class="flex items-center gap-3">
            <svg class="w-5 h-5 text-amber-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <p class="text-sm text-amber-700 dark:text-amber-300 font-medium">No hay cobros registrados</p>
          </div>
        </div>
      </div>
    {:else}
      <div class="overflow-x-auto -mx-4 md:mx-0">
        <table class="w-full min-w-[700px]">
          <thead>
            <tr class="text-left text-[11px] font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider border-b border-gray-100 dark:border-gray-800">
              <th class="px-3 md:px-4 py-1">Fecha</th>
              <th class="px-3 md:px-4 py-1">Monto</th>
              <th class="px-3 md:px-4 py-1 hidden sm:table-cell">Inmueble</th>
              <th class="px-3 md:px-4 py-1 hidden md:table-cell">Propietario</th>
              <th class="px-3 md:px-4 py-1">Observaciones</th>
              {#if isAdmin}
                <th class="px-3 md:px-4 py-1 text-right">Acciones</th>
              {/if}
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50 dark:divide-gray-800">
            {#each enrichedCobros as c (c.id)}
              <tr class="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                <td class="px-3 md:px-4 py-2 text-sm text-gray-900 dark:text-gray-100">{formatDate(c.fecha_cobro)}</td>
                <td class="px-3 md:px-4 py-2 text-sm font-medium text-gray-900 dark:text-gray-100">
                  {formatCurrency(c.monto, c.moneda_original)}
                </td>
                <td class="px-3 md:px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hidden sm:table-cell">{c.inmuebleDireccion}</td>
                <td class="px-3 md:px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hidden md:table-cell">{c.propietarioNombre}</td>
                <td class="px-3 md:px-4 py-2 text-sm text-gray-500 dark:text-gray-400 truncate max-w-[200px]">{c.observaciones || '-'}</td>
                {#if isAdmin}
                  <td class="px-3 md:px-4 py-2 text-right">
                    <button
                      on:click={() => confirmDelete(c)}
                      class="p-1.5 rounded-md text-gray-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors cursor-pointer"
                      title="Eliminar cobro"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </td>
                {/if}
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </div>
</div>

{#if showDeleteConfirm && deleteTarget}
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
    <div class="bg-white dark:bg-gray-900 rounded-xl shadow-xl w-full max-w-md p-6">
      <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100">Eliminar cobro</h3>
      <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
        ¿Seguro que querés eliminar el cobro del
        <strong class="font-medium">{formatDate(deleteTarget.fecha_cobro)}</strong>
        por <strong class="font-medium">{formatCurrency(deleteTarget.monto, deleteTarget.moneda_original)}</strong>?
        Esta acción no se puede deshacer.
      </p>
      {#if error}
        <p class="mt-2 text-sm text-red-600">{error}</p>
      {/if}
      <div class="flex justify-end gap-3 pt-4">
        <button type="button" on:click={() => { showDeleteConfirm = false; deleteTarget = null; }} disabled={deleting}
          class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors cursor-pointer disabled:opacity-50">
          Cancelar
        </button>
        <button type="button" on:click={submitDelete} disabled={deleting}
          class="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 disabled:bg-red-400 rounded-lg transition-colors cursor-pointer disabled:cursor-not-allowed">
          {deleting ? 'Eliminando...' : 'Eliminar'}
        </button>
      </div>
    </div>
  </div>
{/if}
