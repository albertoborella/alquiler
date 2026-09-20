<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { auth } from '$lib/stores/auth';
  import { api } from '$lib/api';
  import type {
    InformePropietarios, InformePivot, InformeResponse,
    PropietarioPivotColumn
  } from '$lib/api';

  let informe: InformeResponse | null = null;
  let loading = true;
  let error = '';

  // Filtros
  let fechaInicio = '';
  let fechaFin = '';
  let propietarioId = '';
  let inmuebleId = '';
  let propietarios: Array<{ id: string; nombre: string }> = [];
  let inmuebles: Array<{ id: string; direccion: string; categoria: string }> = [];

  // Expandir/colapsar propietarios (modo general)
  let expanded: Record<string, boolean> = {};

  $: esPivot = informe?.mode === 'pivot';

  onMount(async () => {
    if (!$auth.token) {
      goto('/login');
      return;
    }
    try {
      const [props, inmList] = await Promise.all([
        api.getPropietarios($auth.token),
        api.getInmuebles($auth.token),
      ]);
      propietarios = props.map(p => ({ id: p.id, nombre: p.nombre }));
      inmuebles = inmList.map(i => ({ id: i.id, direccion: i.direccion, categoria: i.categoria }));
    } catch {
      // Ignorar
    }
    await cargarInforme();
  });

  async function cargarInforme() {
    if (!$auth.token) return;
    loading = true;
    error = '';
    try {
      informe = await api.getInformePropietarios($auth.token, {
        fecha_inicio: fechaInicio || undefined,
        fecha_fin: fechaFin || undefined,
        propietario_id: (!inmuebleId && propietarioId) ? propietarioId : undefined,
        inmueble_id: inmuebleId || undefined,
      });
      if (informe?.mode === 'general') {
        expanded = {};
        for (const p of informe.propietarios) {
          expanded[p.propietario_id] = true;
        }
      }
    } catch (e) {
      error = e instanceof Error ? e.message : 'Error al cargar informe';
    } finally {
      loading = false;
    }
  }

  function toggleExpand(id: string) {
    expanded[id] = !expanded[id];
  }

  function formatMoney(amount: number): string {
    return `$ ${amount.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  }

  function formatDate(dateStr: string): string {
    const [y, m, d] = dateStr.split('-');
    return `${y.slice(2)}/${m}/${d}`;
  }

  function formatMes(mesKey: string): string {
    const [y, m] = mesKey.split('-');
    const meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
    return `${meses[parseInt(m) - 1]} ${y}`;
  }

  // Cast helpers for template (Svelte 4 compatible)
  $: pivotData = informe?.mode === 'pivot' ? (informe as InformePivot) : null;
  $: generalData = informe?.mode === 'general' ? (informe as InformePropietarios) : null;

  $: pivotMeses = (informe?.mode === 'pivot' && informe) ? (informe as any).meses || [] : [];
  $: pivotPropietarios = (informe?.mode === 'pivot' && informe) ? (informe as any).propietarios || [] : [];
  $: pivotTotales = (informe?.mode === 'pivot' && informe) ? (informe as any).totales || { prop_montos: {}, total_bruto: 0, total_admin: 0, total_neto: 0 } : { prop_montos: {}, total_bruto: 0, total_admin: 0, total_neto: 0 };
  $: generalPropietarios = (informe?.mode === 'general' && informe) ? (informe as any).propietarios || [] : [];
</script>

<div class="max-w-7xl mx-auto px-4 md:px-6 lg:px-8 py-6 md:py-8">
  <div class="mb-6 md:mb-8">
    <h1 class="text-xl md:text-2xl font-bold text-gray-900 dark:text-gray-100">Informes de Propietarios</h1>
    <p class="text-gray-500 dark:text-gray-400 mt-1">
      {esPivot ? 'Vista mensual por inmueble' : 'Cobros descontando costo de administración'}
    </p>
  </div>

  <!-- Filtros -->
  <div class="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800 p-4 md:p-6 mb-6">
    <form on:submit|preventDefault={cargarInforme} class="flex flex-wrap items-end gap-4">
      <div>
        <label for="filter-fecha-inicio" class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Fecha inicio</label>
        <input id="filter-fecha-inicio" type="date" bind:value={fechaInicio}
          class="px-3 py-1.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500" />
      </div>
      <div>
        <label for="filter-fecha-fin" class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Fecha fin</label>
        <input id="filter-fecha-fin" type="date" bind:value={fechaFin}
          class="px-3 py-1.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500" />
      </div>
      <div>
        <label for="filter-inmueble" class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Inmueble</label>
        <select id="filter-inmueble" bind:value={inmuebleId}
          class="px-3 py-1.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500">
          <option value="">Todos</option>
          {#each inmuebles as inm}
            <option value={inm.id}>{inm.direccion} ({inm.categoria})</option>
          {/each}
        </select>
      </div>
      {#if !inmuebleId}
        <div>
          <label for="filter-propietario" class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Propietario</label>
          <select id="filter-propietario" bind:value={propietarioId}
            class="px-3 py-1.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500">
            <option value="">Todos</option>
            {#each propietarios as p}
              <option value={p.id}>{p.nombre}</option>
            {/each}
          </select>
        </div>
      {/if}
      <button type="submit" disabled={loading}
        class="px-4 py-1.5 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 disabled:bg-primary-400 rounded-lg transition-colors cursor-pointer disabled:cursor-not-allowed">
        {loading ? 'Cargando...' : 'Filtrar'}
      </button>
    </form>
  </div>

  {#if error}
    <div class="bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 text-sm rounded-lg px-4 py-3 border border-red-100 dark:border-red-800 mb-6">
      {error}
    </div>
  {/if}

  {#if loading && !informe}
    <div class="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800 p-6">
      <div class="animate-pulse space-y-4">
        <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/3"></div>
        <div class="h-20 bg-gray-200 dark:bg-gray-700 rounded"></div>
        <div class="h-20 bg-gray-200 dark:bg-gray-700 rounded"></div>
      </div>
    </div>
  {:else if informe}
    <!-- Info de porcentajes -->
    <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg px-4 py-3 mb-6">
      <p class="text-sm text-blue-700 dark:text-blue-300">
        <span class="font-semibold">Costo de administración:</span>
        Urbanos {informe.costo_admin_urbano}% · Rurales {informe.costo_admin_rural}%
        {#if esPivot}
          <span class="ml-2 text-blue-500">| Vista mensual por inmueble</span>
        {/if}
      </p>
    </div>

    {#if esPivot}
      <!-- VISTA PIVOT (por inmueble) -->

      {#if pivotMeses.length === 0}
        <div class="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800 p-12 text-center">
          <p class="text-gray-500 dark:text-gray-400">No hay cobros registrados para los filtros seleccionados.</p>
        </div>
      {:else}
        <div class="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800 overflow-hidden">
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="bg-gray-50 dark:bg-gray-800/50">
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 sticky left-0 bg-gray-50 dark:bg-gray-800/50 z-10">Mes</th>
                  {#each pivotPropietarios as prop}
                    <th colspan="3" class="px-2 py-3 text-center text-xs font-medium border-l border-gray-200 dark:border-gray-700
                      {prop.porcentaje === 100 ? 'text-blue-600 dark:text-blue-400' : 'text-primary-600 dark:text-primary-400'}">
                      <div>{prop.nombre}</div>
                      <div class="text-[10px] font-normal opacity-70">{prop.porcentaje}%</div>
                    </th>
                  {/each}
                  <th colspan="3" class="px-2 py-3 text-center text-xs font-medium border-l-2 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300">
                    Total período
                  </th>
                </tr>
                <tr class="bg-gray-50 dark:bg-gray-800/50 border-t border-gray-200 dark:border-gray-700">
                  <th class="px-4 py-1.5 sticky left-0 bg-gray-50 dark:bg-gray-800/50 z-10"></th>
                  {#each pivotPropietarios as _}
                    <th class="px-2 py-1.5 text-[10px] text-right text-gray-400 border-l border-gray-200 dark:border-gray-700">Bruto</th>
                    <th class="px-2 py-1.5 text-[10px] text-right text-gray-400">Admin</th>
                    <th class="px-2 py-1.5 text-[10px] text-right text-gray-400">Neto</th>
                  {/each}
                  <th class="px-2 py-1.5 text-[10px] text-right text-gray-400 border-l-2 border-gray-300 dark:border-gray-600">Bruto</th>
                  <th class="px-2 py-1.5 text-[10px] text-right text-gray-400">Admin</th>
                  <th class="px-2 py-1.5 text-[10px] text-right text-gray-400">Neto</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100 dark:divide-gray-800">
                {#each pivotMeses as fila (fila.mes_key)}
                  <tr class="hover:bg-gray-50 dark:hover:bg-gray-800/30">
                    <td class="px-4 py-2.5 font-medium text-gray-700 dark:text-gray-300 sticky left-0 bg-white dark:bg-gray-900 z-10">
                      {formatMes(fila.mes_key)}
                    </td>
                    {#each pivotPropietarios as prop}
                      <td class="px-2 py-2.5 text-right text-gray-700 dark:text-gray-300 border-l border-gray-100 dark:border-gray-800">
                        {formatMoney((fila.prop_montos[prop.propietario_id] || { bruto: 0, admin: 0, neto: 0 }).bruto)}
                      </td>
                      <td class="px-2 py-2.5 text-right text-red-500 dark:text-red-400 text-xs">
                        {(fila.prop_montos[prop.propietario_id] || { bruto: 0, admin: 0, neto: 0 }).admin > 0 ? `- ${formatMoney((fila.prop_montos[prop.propietario_id] || { bruto: 0, admin: 0, neto: 0 }).admin)}` : '—'}
                      </td>
                      <td class="px-2 py-2.5 text-right font-semibold text-gray-900 dark:text-gray-100">
                        {formatMoney((fila.prop_montos[prop.propietario_id] || { bruto: 0, admin: 0, neto: 0 }).neto)}
                      </td>
                    {/each}
                    <td class="px-2 py-2.5 text-right text-gray-700 dark:text-gray-300 border-l-2 border-gray-200 dark:border-gray-700">
                      {formatMoney(fila.total_bruto)}
                    </td>
                    <td class="px-2 py-2.5 text-right text-red-600 dark:text-red-400 text-xs">
                      - {formatMoney(fila.total_admin)}
                    </td>
                    <td class="px-2 py-2.5 text-right font-bold text-gray-900 dark:text-gray-100">
                      {formatMoney(fila.total_neto)}
                    </td>
                  </tr>
                {/each}
              </tbody>
              <tfoot>
                <tr class="bg-gray-100 dark:bg-gray-800/70 font-bold border-t-2 border-gray-300 dark:border-gray-600">
                  <td class="px-4 py-3 sticky left-0 bg-gray-100 dark:bg-gray-800/70 z-10 text-gray-700 dark:text-gray-300">TOTALES</td>
                  {#each pivotPropietarios as prop}
                    <td class="px-2 py-3 text-right text-gray-700 dark:text-gray-300 border-l border-gray-200 dark:border-gray-700">
                      {formatMoney((pivotTotales.prop_montos[prop.propietario_id] || { bruto: 0, admin: 0, neto: 0 }).bruto)}
                    </td>
                    <td class="px-2 py-3 text-right text-red-600 dark:text-red-400 text-xs">
                      - {formatMoney((pivotTotales.prop_montos[prop.propietario_id] || { bruto: 0, admin: 0, neto: 0 }).admin)}
                    </td>
                    <td class="px-2 py-3 text-right text-emerald-600 dark:text-emerald-400">
                      {formatMoney((pivotTotales.prop_montos[prop.propietario_id] || { bruto: 0, admin: 0, neto: 0 }).neto)}
                    </td>
                  {/each}
                  <td class="px-2 py-3 text-right text-gray-700 dark:text-gray-300 border-l-2 border-gray-300 dark:border-gray-600">
                    {formatMoney(pivotTotales.total_bruto)}
                  </td>
                  <td class="px-2 py-3 text-right text-red-600 dark:text-red-400 text-xs">
                    - {formatMoney(pivotTotales.total_admin)}
                  </td>
                  <td class="px-2 py-3 text-right text-emerald-600 dark:text-emerald-400">
                    {formatMoney(pivotTotales.total_neto)}
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      {/if}

    {:else}
      <!-- VISTA GENERAL (por propietario) -->

      {#if generalPropietarios.length === 0}
        <div class="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800 p-12 text-center">
          <p class="text-gray-500 dark:text-gray-400">No hay cobros registrados para los filtros seleccionados.</p>
        </div>
      {:else}
        <!-- Resumen general -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div class="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800 p-4">
            <p class="text-xs text-gray-500 dark:text-gray-400 mb-1">Total bruto</p>
            <p class="text-lg font-bold text-gray-900 dark:text-gray-100">
              {formatMoney(generalPropietarios.reduce((sum, p) => sum + p.total_bruto, 0))}
            </p>
          </div>
          <div class="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800 p-4">
            <p class="text-xs text-gray-500 dark:text-gray-400 mb-1">Total admin descontado</p>
            <p class="text-lg font-bold text-red-600 dark:text-red-400">
              - {formatMoney(generalPropietarios.reduce((sum, p) => sum + p.total_admin, 0))}
            </p>
          </div>
          <div class="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800 p-4">
            <p class="text-xs text-gray-500 dark:text-gray-400 mb-1">Total neto propietarios</p>
            <p class="text-lg font-bold text-emerald-600 dark:text-emerald-400">
              {formatMoney(generalPropietarios.reduce((sum, p) => sum + p.total_neto, 0))}
            </p>
          </div>
        </div>

        <!-- Por propietario -->
        <div class="space-y-4">
          {#each generalPropietarios as prop (prop.propietario_id)}
            <div class="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800 overflow-hidden">
              <button
                type="button"
                on:click={() => toggleExpand(prop.propietario_id)}
                class="w-full flex items-center justify-between px-4 md:px-6 py-4 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors cursor-pointer"
              >
                <div class="flex items-center gap-3 text-left">
                  <div class="w-9 h-9 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center flex-shrink-0">
                    <span class="text-sm font-bold text-primary-600 dark:text-primary-400">
                      {prop.propietario_nombre.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <div>
                    <p class="text-sm font-semibold text-gray-900 dark:text-gray-100">{prop.propietario_nombre}</p>
                    {#if prop.propietario_cuit}
                      <p class="text-xs text-gray-500 dark:text-gray-400">CUIT: {prop.propietario_cuit}</p>
                    {/if}
                  </div>
                </div>
                <div class="flex items-center gap-4 md:gap-6">
                  <div class="text-right hidden sm:block">
                    <p class="text-xs text-gray-500 dark:text-gray-400">Neto</p>
                    <p class="text-sm font-bold text-emerald-600 dark:text-emerald-400">{formatMoney(prop.total_neto)}</p>
                  </div>
                  <svg class="w-5 h-5 text-gray-400 transition-transform {expanded[prop.propietario_id] ? 'rotate-180' : ''}"
                    fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </button>

              {#if expanded[prop.propietario_id]}
                <div class="border-t border-gray-100 dark:border-gray-800">
                  <div class="overflow-x-auto">
                    <table class="w-full text-sm">
                      <thead>
                        <tr class="bg-gray-50 dark:bg-gray-800/50">
                          <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400">Fecha</th>
                          <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400">Inmueble</th>
                          <th class="px-4 py-2 text-center text-xs font-medium text-gray-500 dark:text-gray-400">Part.</th>
                          <th class="px-4 py-2 text-right text-xs font-medium text-gray-500 dark:text-gray-400">Bruto</th>
                          <th class="px-4 py-2 text-right text-xs font-medium text-gray-500 dark:text-gray-400">Admin</th>
                          <th class="px-4 py-2 text-right text-xs font-medium text-gray-500 dark:text-gray-400">Neto</th>
                        </tr>
                      </thead>
                      <tbody class="divide-y divide-gray-100 dark:divide-gray-800">
                        {#each prop.cobros as cobro (cobro.id)}
                          <tr class="hover:bg-gray-50 dark:hover:bg-gray-800/30">
                            <td class="px-4 py-2.5 text-gray-700 dark:text-gray-300">{formatDate(cobro.fecha_cobro)}</td>
                            <td class="px-4 py-2.5">
                              <span class="text-gray-700 dark:text-gray-300">{cobro.inmueble_direccion}</span>
                              <span class="ml-1.5 inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium
                                {cobro.inmueble_tipo === 'rural'
                                  ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                                  : 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'}">
                                {cobro.inmueble_tipo}
                              </span>
                            </td>
                            <td class="px-4 py-2.5 text-center text-xs text-gray-500 dark:text-gray-400">{cobro.porcentaje_participacion}%</td>
                            <td class="px-4 py-2.5 text-right text-gray-700 dark:text-gray-300">{formatMoney(cobro.monto_bruto)}</td>
                            <td class="px-4 py-2.5 text-right text-red-600 dark:text-red-400">
                              - {formatMoney(cobro.costo_admin)}
                              <span class="text-[10px] text-gray-400 ml-0.5">({cobro.porcentaje_admin}%)</span>
                            </td>
                            <td class="px-4 py-2.5 text-right font-semibold text-gray-900 dark:text-gray-100">{formatMoney(cobro.monto_neto)}</td>
                          </tr>
                        {/each}
                      </tbody>
                      <tfoot>
                        <tr class="bg-gray-50 dark:bg-gray-800/50 font-semibold">
                          <td colspan="3" class="px-4 py-2.5 text-xs text-gray-500 dark:text-gray-400">TOTALES</td>
                          <td class="px-4 py-2.5 text-right text-gray-700 dark:text-gray-300">{formatMoney(prop.total_bruto)}</td>
                          <td class="px-4 py-2.5 text-right text-red-600 dark:text-red-400">- {formatMoney(prop.total_admin)}</td>
                          <td class="px-4 py-2.5 text-right text-emerald-600 dark:text-emerald-400">{formatMoney(prop.total_neto)}</td>
                        </tr>
                      </tfoot>
                    </table>
                  </div>
                </div>
              {/if}
            </div>
          {/each}
        </div>
      {/if}
    {/if}
  {/if}
</div>
