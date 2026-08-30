<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { auth } from '$lib/stores/auth';
  import { api } from '$lib/api';
  import type { ContratoDash, InmueblePublic, InquilinoPublic } from '$lib/api';

  let contratos: ContratoDash[] = [];
  let inmuebles: InmueblePublic[] = [];
  let inquilinos: InquilinoPublic[] = [];
  let loading = true;
  let error = '';

  // ── Filters ──
  let filterInmueble = '';
  let filterActivo = '';

  let inmuebleMap = new Map<string, InmueblePublic>();
  let inquilinoMap = new Map<string, InquilinoPublic>();

  $: isAdmin = $auth.user?.role === 'admin';

  // ── Edit modal ──
  let showEditModal = false;
  let editTarget: ContratoDash | null = null;
  let editForm = {
    fecha_inicio: '',
    fecha_fin: '',
    fecha_maxima_pago: '',
    modalidad_pago: '',
    frecuencia: '',
    monto_base: '',
    moneda: '',
    indice: '',
    periodo_indexacion: '',
    tipo_producto: '',
    kilos: '',
    precio_kilo: '',
    fuente_precio_agro: '',
    activo: true,
  };
  let editing = false;
  let editSuccess = '';
  let editError = '';

  // ── Delete modal ──
  let showDeleteConfirm = false;
  let deleteTarget: ContratoDash | null = null;
  let deleting = false;

  $: filteredContratos = contratos.filter((c) => {
    if (filterInmueble && c.inmueble_id !== filterInmueble) return false;
    if (filterActivo === 'activo' && !c.activo) return false;
    if (filterActivo === 'inactivo' && c.activo) return false;
    return true;
  });

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
      const [contratosData, inmueblesData, inquilinosData] = await Promise.all([
        api.getContratos($auth.token),
        api.getInmuebles($auth.token),
        api.getInquilinos($auth.token),
      ]);
      contratos = contratosData;
      inmuebles = inmueblesData;
      inquilinos = inquilinosData;

      inmuebleMap = new Map(inmuebles.map((i) => [i.id, i]));
      inquilinoMap = new Map(inquilinos.map((i) => [i.id, i]));
    } catch (err) {
      error = err instanceof Error ? err.message : 'Error al cargar contratos';
    } finally {
      loading = false;
    }
  }

  function clearFilters() {
    filterInmueble = '';
    filterActivo = '';
  }

  function openEdit(c: ContratoDash) {
    editTarget = c;
    editForm = {
      fecha_inicio: c.fecha_inicio,
      fecha_fin: c.fecha_fin,
      fecha_maxima_pago: String(c.fecha_maxima_pago),
      modalidad_pago: c.modalidad_pago,
      frecuencia: c.frecuencia,
      monto_base: c.monto_base != null ? String(c.monto_base) : '',
      moneda: c.moneda || '',
      indice: c.indice || '',
      periodo_indexacion: c.periodo_indexacion || '',
      tipo_producto: c.tipo_producto || '',
      kilos: c.kilos != null ? String(c.kilos) : '',
      precio_kilo: c.precio_kilo != null ? String(c.precio_kilo) : '',
      fuente_precio_agro: '',
      activo: c.activo,
    };
    editSuccess = '';
    editError = '';
    showEditModal = true;
  }

  async function submitEdit() {
    if (!$auth.token || !editTarget) return;
    editing = true;
    editError = '';
    editSuccess = '';
    try {
      const updated = await api.updateContrato($auth.token, editTarget.id, {
        fecha_inicio: editForm.fecha_inicio || undefined,
        fecha_fin: editForm.fecha_fin || undefined,
        fecha_maxima_pago: editForm.fecha_maxima_pago ? parseInt(editForm.fecha_maxima_pago) : undefined,
        modalidad_pago: editForm.modalidad_pago || undefined,
        frecuencia: editForm.frecuencia || undefined,
        monto_base: editForm.monto_base ? parseFloat(editForm.monto_base) : undefined,
        moneda: editForm.moneda || undefined,
        indice: editForm.indice || undefined,
        periodo_indexacion: editForm.periodo_indexacion || undefined,
        tipo_producto: editForm.tipo_producto || undefined,
        kilos: editForm.kilos ? parseFloat(editForm.kilos) : undefined,
        precio_kilo: editForm.precio_kilo ? parseFloat(editForm.precio_kilo) : undefined,
        activo: editForm.activo,
      });
      // Update local state
      contratos = contratos.map((c) => c.id === editTarget!.id ? { ...c, ...updated } : c);
      editSuccess = 'Contrato actualizado';
      setTimeout(() => { showEditModal = false; }, 1200);
    } catch (err) {
      editError = err instanceof Error ? err.message : 'Error al actualizar';
    } finally {
      editing = false;
    }
  }

  function confirmDelete(c: ContratoDash) {
    deleteTarget = c;
    showDeleteConfirm = true;
  }

  async function submitDelete() {
    if (!$auth.token || !deleteTarget) return;
    deleting = true;
    try {
      await api.deleteContrato($auth.token, deleteTarget.id);
      contratos = contratos.filter((c) => c.id !== deleteTarget!.id);
      showDeleteConfirm = false;
      deleteTarget = null;
    } catch (err) {
      error = err instanceof Error ? err.message : 'Error al eliminar contrato';
    } finally {
      deleting = false;
    }
  }

  function formatDate(dateStr: string | null): string {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('es-AR', { day: '2-digit', month: '2-digit', year: 'numeric' });
  }

  function formatCurrency(amount: number | null, currency: string | null): string {
    if (amount === null || amount === undefined) return '-';
    const sym = currency === 'USD' ? 'US$' : '$';
    return `${sym} ${amount.toLocaleString('es-AR', { minimumFractionDigits: 0, maximumFractionDigits: 2 })}`;
  }

  function modalidadLabel(m: string): string {
    const map: Record<string, string> = {
      pesos_indice: 'Pesos + Índice',
      moneda_extranjera: 'Moneda extranjera',
      producto_agropecuario: 'Producto agropecuario',
    };
    return map[m] || m;
  }

  function frecuenciaLabel(f: string): string {
    const map: Record<string, string> = {
      mensual: 'Mensual',
      trimestral: 'Trimestral',
      anual: 'Anual',
      vencimiento: 'Vencimiento',
    };
    return map[f] || f;
  }
</script>

<div class="max-w-7xl mx-auto px-4 md:px-6 lg:px-8 py-6 md:py-8">
  <div class="mb-6 md:mb-8">
    <h1 class="text-xl md:text-2xl font-bold text-gray-900 dark:text-gray-100">Contratos</h1>
    <p class="text-gray-500 dark:text-gray-400 mt-1">Gestión de contratos de alquiler</p>
  </div>

  <div class="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800">
    <!-- Filters bar -->
    <div class="px-4 md:px-6 py-3 border-b border-gray-100 dark:border-gray-800">
      <div class="flex flex-wrap items-end gap-3">
        <!-- Inmueble filter -->
        <div>
          <label for="filterInm" class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Inmueble</label>
          <select id="filterInm" bind:value={filterInmueble}
            class="px-3 py-1.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent">
            <option value="">Todos</option>
            {#each inmuebles as inm}
              <option value={inm.id}>{inm.direccion}</option>
            {/each}
          </select>
        </div>

        <!-- Activo filter -->
        <div>
          <label for="filterActivo" class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Estado</label>
          <select id="filterActivo" bind:value={filterActivo}
            class="px-3 py-1.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent">
            <option value="">Todos</option>
            <option value="activo">Activo</option>
            <option value="inactivo">Inactivo</option>
          </select>
        </div>

        <button on:click={clearFilters}
          class="px-3 py-1.5 text-sm font-medium text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors cursor-pointer">
          Limpiar
        </button>

        <p class="ml-auto text-sm text-gray-500 dark:text-gray-400">
          {filteredContratos.length} contrato{filteredContratos.length !== 1 ? 's' : ''}
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
            <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/5"></div>
            <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/6"></div>
            <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/4"></div>
            <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/6"></div>
          </div>
        {/each}
      </div>
    {:else if filteredContratos.length === 0}
      <div class="px-6 py-16 text-center">
        <div class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg px-6 py-5 max-w-md mx-auto mb-6">
          <div class="flex items-center gap-3">
            <svg class="w-5 h-5 text-amber-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <p class="text-sm text-amber-700 dark:text-amber-300 font-medium">No hay contratos registrados</p>
          </div>
        </div>
      </div>
    {:else}
      <div class="overflow-x-auto -mx-4 md:mx-0">
        <table class="w-full min-w-[800px]">
          <thead>
            <tr class="text-left text-[11px] font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider border-b border-gray-100 dark:border-gray-800">
              <th class="px-3 md:px-4 py-1">Inmueble</th>
              <th class="px-3 md:px-4 py-1 hidden sm:table-cell">Inquilino</th>
              <th class="px-3 md:px-4 py-1">Inicio</th>
              <th class="px-3 md:px-4 py-1 hidden sm:table-cell">Fin</th>
              <th class="px-3 md:px-4 py-1 hidden md:table-cell">Monto</th>
              <th class="px-3 md:px-4 py-1 hidden md:table-cell">Modalidad</th>
              <th class="px-3 md:px-4 py-1 hidden lg:table-cell">Frecuencia</th>
              <th class="px-3 md:px-4 py-1">Estado</th>
              {#if isAdmin}
                <th class="px-3 md:px-4 py-1 text-right">Acciones</th>
              {/if}
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50 dark:divide-gray-800">
            {#each filteredContratos as c (c.id)}
              <tr class="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                <td class="px-3 md:px-4 py-2 text-sm font-medium text-gray-900 dark:text-gray-100">
                  {inmuebleMap.get(c.inmueble_id)?.direccion || c.inmueble_id.slice(0, 8)}
                </td>
                <td class="px-3 md:px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hidden sm:table-cell">
                  {inquilinoMap.get(c.inquilino_id)?.nombre || c.inquilino_id.slice(0, 8)}
                </td>
                <td class="px-3 md:px-4 py-2 text-sm text-gray-700 dark:text-gray-300">{formatDate(c.fecha_inicio)}</td>
                <td class="px-3 md:px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hidden sm:table-cell">{formatDate(c.fecha_fin)}</td>
                <td class="px-3 md:px-4 py-2 text-sm text-gray-900 dark:text-gray-100 hidden md:table-cell">
                  {formatCurrency(c.monto_base, c.moneda)}
                </td>
                <td class="px-3 md:px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hidden md:table-cell">
                  {modalidadLabel(c.modalidad_pago)}
                </td>
                <td class="px-3 md:px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hidden lg:table-cell">
                  {frecuenciaLabel(c.frecuencia)}
                </td>
                <td class="px-3 md:px-4 py-2">
                  {#if c.activo}
                    <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200">
                      Activo
                    </span>
                  {:else}
                    <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400">
                      Inactivo
                    </span>
                  {/if}
                </td>
                {#if isAdmin}
                  <td class="px-3 md:px-4 py-2 text-right">
                    <div class="flex items-center justify-end gap-1">
                      <button
                        on:click={() => openEdit(c)}
                        class="p-1.5 rounded-md text-gray-400 hover:text-primary-600 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-colors cursor-pointer"
                        title="Editar contrato"
                      >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </button>
                      <button
                        on:click={() => confirmDelete(c)}
                        class="p-1.5 rounded-md text-gray-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors cursor-pointer"
                        title="Eliminar contrato"
                      >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
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

<!-- ═══════════════════════════════════════════════════════════ -->
<!-- EDIT CONTRATO MODAL                                         -->
<!-- ═══════════════════════════════════════════════════════════ -->
{#if showEditModal && editTarget}
  <div class="fixed inset-0 z-50 flex items-center justify-center">
    <div class="absolute inset-0 bg-black/50" on:click={() => { showEditModal = false; }} role="presentation"></div>
    <div class="relative bg-white dark:bg-gray-900 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 w-full max-w-2xl mx-4 p-6 max-h-[90vh] overflow-y-auto">
      <div class="flex items-center gap-3 mb-5">
        <div class="w-10 h-10 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">
          <svg class="w-5 h-5 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
        </div>
        <div>
          <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100">Editar contrato</h3>
          <p class="text-sm text-gray-500 dark:text-gray-400">
            {inmuebleMap.get(editTarget.inmueble_id)?.direccion || ''} — {inquilinoMap.get(editTarget.inquilino_id)?.nombre || ''}
          </p>
        </div>
      </div>

      {#if editError}
        <div class="bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 text-sm rounded-lg px-4 py-3 border border-red-100 dark:border-red-800 mb-4">{editError}</div>
      {/if}
      {#if editSuccess}
        <div class="bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-300 text-sm rounded-lg px-4 py-3 border border-emerald-100 dark:border-emerald-800 mb-4">{editSuccess}</div>
      {/if}

      <form on:submit|preventDefault={submitEdit} class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="ed-fecha-inicio" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Fecha inicio *</label>
            <input id="ed-fecha-inicio" type="date" bind:value={editForm.fecha_inicio} required
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
          </div>
          <div>
            <label for="ed-fecha-fin" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Fecha fin *</label>
            <input id="ed-fecha-fin" type="date" bind:value={editForm.fecha_fin} required
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
          </div>
        </div>

        <div class="grid grid-cols-3 gap-4">
          <div>
            <label for="ed-monto" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Monto base</label>
            <input id="ed-monto" type="number" step="0.01" min="0" bind:value={editForm.monto_base} placeholder="0.00"
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
          </div>
          <div>
            <label for="ed-moneda" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Moneda</label>
            <select id="ed-moneda" bind:value={editForm.moneda}
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent">
              <option value="ARS">ARS</option>
              <option value="USD">USD</option>
            </select>
          </div>
          <div>
            <label for="ed-max-pago" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Días máx. pago</label>
            <input id="ed-max-pago" type="number" min="1" bind:value={editForm.fecha_maxima_pago} placeholder="10"
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="ed-modalidad" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Modalidad</label>
            <select id="ed-modalidad" bind:value={editForm.modalidad_pago}
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent">
              <option value="pesos_indice">Pesos + Índice</option>
              <option value="moneda_extranjera">Moneda extranjera</option>
              <option value="producto_agropecuario">Producto agropecuario</option>
            </select>
          </div>
          <div>
            <label for="ed-frecuencia" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Frecuencia</label>
            <select id="ed-frecuencia" bind:value={editForm.frecuencia}
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent">
              <option value="mensual">Mensual</option>
              <option value="trimestral">Trimestral</option>
              <option value="anual">Anual</option>
              <option value="vencimiento">Vencimiento</option>
            </select>
          </div>
        </div>

        {#if editForm.modalidad_pago === 'pesos_indice'}
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label for="ed-indice" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Índice</label>
              <input id="ed-indice" type="text" bind:value={editForm.indice} placeholder="Ej: IPC"
                class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
            </div>
            <div>
              <label for="ed-periodo" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Período indexación</label>
              <input id="ed-periodo" type="text" bind:value={editForm.periodo_indexacion} placeholder="Ej: trimestral"
                class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
            </div>
          </div>
        {/if}

        {#if editForm.modalidad_pago === 'producto_agropecuario'}
          <div class="grid grid-cols-3 gap-4">
            <div>
              <label for="ed-tipo-prod" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Tipo producto</label>
              <input id="ed-tipo-prod" type="text" bind:value={editForm.tipo_producto}
                class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
            </div>
            <div>
              <label for="ed-kilos" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Kilos</label>
              <input id="ed-kilos" type="number" step="0.01" min="0" bind:value={editForm.kilos}
                class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
            </div>
            <div>
              <label for="ed-precio-kilo" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Precio/kilo</label>
              <input id="ed-precio-kilo" type="number" step="0.01" min="0" bind:value={editForm.precio_kilo}
                class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
            </div>
          </div>
        {/if}

        <div class="flex items-center gap-3">
          <label class="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300 cursor-pointer">
            <input type="checkbox" bind:checked={editForm.activo}
              class="w-4 h-4 rounded border-gray-300 dark:border-gray-600 text-primary-600 focus:ring-primary-500" />
            Contrato activo
          </label>
        </div>

        <div class="flex justify-end gap-3 pt-2">
          <button type="button" on:click={() => { showEditModal = false; }} disabled={editing}
            class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors cursor-pointer disabled:opacity-50">
            Cancelar
          </button>
          <button type="submit" disabled={editing || !editForm.fecha_inicio || !editForm.fecha_fin}
            class="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 disabled:bg-primary-400 rounded-lg transition-colors cursor-pointer disabled:cursor-not-allowed">
            {editing ? 'Guardando...' : 'Guardar cambios'}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

{#if showDeleteConfirm && deleteTarget}
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
    <div class="bg-white dark:bg-gray-900 rounded-xl shadow-xl w-full max-w-md p-6">
      <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100">Eliminar contrato</h3>
      <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
        ¿Seguro que querés eliminar el contrato con inmueble
        <strong class="font-medium">{deleteTarget.inmueble_direccion}</strong>?
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
