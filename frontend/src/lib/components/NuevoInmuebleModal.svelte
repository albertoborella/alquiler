<script lang="ts">
  import { auth } from '$lib/stores/auth';
  import { api } from '$lib/api';
  import type { Propietario } from '$lib/api';

  export let open = false;
  export let defaultCategoria: 'urbano' | 'rural' = 'urbano';
  export let onClose: () => void = () => {};
  export let onCreated: () => void = () => {};

  interface PropietarioRow {
    clave: number;
    modo: 'existente' | 'nuevo';
    propietario_id: string;
    porcentaje: string;
    // new fields
    nombre: string;
    dni_cuit: string;
    telefono: string;
    email: string;
    direccion: string;
  }

  let form = {
    direccion: '',
    categoria: 'urbano' as 'urbano' | 'rural',
    superficie: '',
    habitaciones: '',
    banos: '',
    dormitorios: '',
    comodidades: '',
    descripcion: '',
  };

  let propietarios: Propietario[] = [];
  let propietariosLoading = false;
  let rows: PropietarioRow[] = [];
  let nextKey = 1;

  let submitting = false;
  let success = '';
  let error = '';

  // The category is fixed by the view that opened the modal (no select in the UI).
  // Keep form.categoria in lockstep with defaultCategoria at all times so the
  // urban/rural field set is always correct, regardless of modal open timing.
  $: if (defaultCategoria) form.categoria = defaultCategoria;

  $: totalPorcentaje = rows.reduce((acc, r) => acc + (parseFloat(r.porcentaje) || 0), 0);
  $: showTotalWarning = rows.length > 1 && totalPorcentaje !== 100;

  // Reset only on the rising edge of `open` (when the modal is opened), so the
  // internal re-renders triggered by binding form/rows never wipe what the user types.
  let previousOpen = false;
  $: if (open && !previousOpen) {
    resetForm();
    if (propietarios.length === 0) loadPropietarios();
  }
  $: previousOpen = open;

  function resetForm() {
    form = {
      direccion: '',
      categoria: defaultCategoria,
      superficie: '',
      habitaciones: '',
      banos: '',
      dormitorios: '',
      comodidades: '',
      descripcion: '',
    };
    success = '';
    error = '';
    rows = [newRow('existente', '100')];
  }

  function newRow(modo: 'existente' | 'nuevo', porcentaje = ''): PropietarioRow {
    const r: PropietarioRow = {
      clave: nextKey,
      modo,
      propietario_id: '',
      porcentaje: porcentaje === '' ? '' : String(porcentaje),
      nombre: '',
      dni_cuit: '',
      telefono: '',
      email: '',
      direccion: '',
    };
    nextKey += 1;
    return r;
  }

  async function loadPropietarios() {
    if (!$auth.token) return;
    propietariosLoading = true;
    try {
      propietarios = await api.getPropietarios($auth.token);
    } catch (err) {
      error = err instanceof Error ? err.message : 'Error al cargar propietarios';
    } finally {
      propietariosLoading = false;
    }
  }

  function addPropietario() {
    rows = [...rows, newRow('existente')];
  }

  function removePropietario(clave: number) {
    if (rows.length === 1) return;
    rows = rows.filter((r) => r.clave !== clave);
  }

  function setModo(clave: number, modo: 'existente' | 'nuevo') {
    rows = rows.map((r) => (r.clave === clave ? { ...r, modo, propietario_id: '', nombre: '', dni_cuit: '' } : r));
  }

  function setPropietario(clave: number, id: string) {
    rows = rows.map((r) => (r.clave === clave ? { ...r, propietario_id: id } : r));
  }

  function onSelectPropietario(e: Event, clave: number) {
    setPropietario(clave, (e.currentTarget as HTMLSelectElement).value);
  }

  function setField(clave: number, field: keyof PropietarioRow, value: string) {
    rows = rows.map((r) => (r.clave === clave ? { ...r, [field]: value } : r));
  }

  function cancel() {
    onClose();
  }

  async function submit() {
    if (!$auth.token) return;
    submitting = true;
    error = '';
    success = '';
    try {
      const validRows = rows.filter(
        (r) => (r.modo === 'existente' ? r.propietario_id : r.nombre && r.dni_cuit)
      );
      if (validRows.length === 0) {
        error = 'Debés agregar al menos un propietario';
        submitting = false;
        return;
      }

      const propietariosPayload = validRows.map((r) => {
        const base: any = {
          propietario_id: r.modo === 'existente' ? r.propietario_id : undefined,
          porcentaje_participacion: parseFloat(r.porcentaje) || 0,
        };
        if (r.modo === 'nuevo') {
          base.nombre = r.nombre;
          base.dni_cuit = r.dni_cuit;
          if (r.telefono) base.telefono = r.telefono;
          if (r.email) base.email = r.email;
          if (r.direccion) base.direccion = r.direccion;
        }
        return base;
      });

      await api.createInmueble($auth.token, {
        direccion: form.direccion,
        categoria: form.categoria,
        superficie: form.superficie ? parseFloat(form.superficie) : undefined,
        habitaciones: form.categoria === 'urbano' && form.habitaciones ? parseInt(form.habitaciones) : undefined,
        banos: form.categoria === 'urbano' && form.banos ? parseInt(form.banos) : undefined,
        dormitorios: form.categoria === 'urbano' && form.dormitorios ? parseInt(form.dormitorios) : undefined,
        comodidades: form.categoria === 'urbano' && form.comodidades ? form.comodidades : undefined,
        descripcion: form.descripcion || undefined,
        propietarios: propietariosPayload,
      });

      success = 'Inmueble creado exitosamente';
      setTimeout(() => {
        onClose();
        onCreated();
      }, 1500);
    } catch (err) {
      error = err instanceof Error ? err.message : 'Error al crear inmueble';
    } finally {
      submitting = false;
    }
  }
</script>

{#if open}
  <div class="fixed inset-0 z-50 flex items-center justify-center">
    <div class="absolute inset-0 bg-black/50" on:click={cancel} role="presentation"></div>
    <div class="relative bg-white dark:bg-gray-900 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 w-full max-w-2xl mx-4 p-6 max-h-[90vh] overflow-y-auto">
      <div class="flex items-center gap-3 mb-5">
        <div class="w-10 h-10 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">
          <svg class="w-5 h-5 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
          </svg>
        </div>
        <div>
          <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100">Nuevo inmueble</h3>
          <p class="text-sm text-gray-500 dark:text-gray-400">Se crea como disponible</p>
        </div>
      </div>

      {#if success}
        <div class="bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-300 text-sm rounded-lg px-4 py-3 border border-emerald-100 dark:border-emerald-800 mb-4">
          {success}
        </div>
      {/if}

      {#if error}
        <div class="bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 text-sm rounded-lg px-4 py-3 border border-red-100 dark:border-red-800 mb-4">
          {error}
        </div>
      {/if}

      <form on:submit|preventDefault={submit} class="space-y-4">
        <!-- Categoria (fija segun la tabla desde la que se crea; no se edita) -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <p class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Categoría</p>
            <div class="px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 capitalize">
              {form.categoria === 'urbano' ? 'Urbano' : 'Rural'}
            </div>
          </div>
          <div>
            <label for="nuevo-inm-superficie" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Superficie ({form.categoria === 'urbano' ? 'm²' : 'ha'})
            </label>
            <input id="nuevo-inm-superficie" type="number" step="0.01" min="0" bind:value={form.superficie} placeholder="0.00"
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
          </div>
        </div>

        <!-- Direccion -->
        <div>
          <label for="nuevo-inm-direccion" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Dirección *</label>
          <input id="nuevo-inm-direccion" type="text" bind:value={form.direccion} required placeholder="Ej: Av. Corrientes 1234"
            class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
        </div>

        <!-- Campos urbanos -->
        {#if form.categoria === 'urbano'}
          <div class="grid grid-cols-3 gap-4">
            <div>
              <label for="nuevo-inm-hab" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Habitaciones</label>
              <input id="nuevo-inm-hab" type="number" min="0" bind:value={form.habitaciones} placeholder="0"
                class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
            </div>
            <div>
              <label for="nuevo-inm-banos" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Baños</label>
              <input id="nuevo-inm-banos" type="number" min="0" bind:value={form.banos} placeholder="0"
                class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
            </div>
            <div>
              <label for="nuevo-inm-dorm" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Dormitorios</label>
              <input id="nuevo-inm-dorm" type="number" min="0" bind:value={form.dormitorios} placeholder="0"
                class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
            </div>
          </div>

          <div>
            <label for="nuevo-inm-comodidades" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Comodidades</label>
            <input id="nuevo-inm-comodidades" type="text" bind:value={form.comodidades} placeholder="Ej: pileta, parrilla, garage"
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
          </div>
        {/if}

        <!-- Descripcion -->
        <div>
          <label for="nuevo-inm-descripcion" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Descripción</label>
          <textarea id="nuevo-inm-descripcion" bind:value={form.descripcion} rows="2" placeholder="Notas adicionales..."
            class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"></textarea>
        </div>

        <!-- Propietarios -->
        <div class="border-t border-gray-200 dark:border-gray-700 pt-4">
          <div class="flex items-center justify-between mb-3">
            <p class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Propietarios</p>
            <button type="button" on:click={addPropietario}
              class="inline-flex items-center gap-1 text-xs font-medium text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 transition-colors cursor-pointer">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              Agregar propietario
            </button>
          </div>

          {#if propietariosLoading}
            <p class="text-xs text-gray-500 dark:text-gray-400">Cargando propietarios...</p>
          {/if}

          <div class="space-y-3">
            {#each rows as row (row.clave)}
              <div class="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg space-y-2">
                <div class="flex items-center justify-between gap-2">
                  <div class="flex items-center gap-1">
                    <button type="button"
                      on:click={() => setModo(row.clave, 'existente')}
                      class="text-xs px-2 py-1 rounded-md transition-colors cursor-pointer {row.modo === 'existente' ? 'bg-primary-100 dark:bg-primary-900/40 text-primary-700 dark:text-primary-300' : 'text-gray-500 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'}">
                      Existente
                    </button>
                    <button type="button"
                      on:click={() => setModo(row.clave, 'nuevo')}
                      class="text-xs px-2 py-1 rounded-md transition-colors cursor-pointer {row.modo === 'nuevo' ? 'bg-primary-100 dark:bg-primary-900/40 text-primary-700 dark:text-primary-300' : 'text-gray-500 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'}">
                      Crear nuevo
                    </button>
                  </div>
                  <div class="flex items-center gap-2">
                  <div class="flex items-center gap-1">
                    <label for="porc-{row.clave}" class="text-xs text-gray-500 dark:text-gray-400">%</label>
                    <input id="porc-{row.clave}" type="number" step="0.01" min="0" max="100" bind:value={row.porcentaje} placeholder="100"
                        class="w-20 px-2 py-1 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
                    </div>
                    {#if rows.length > 1}
                      <button type="button" on:click={() => removePropietario(row.clave)}
                        class="p-1.5 rounded-md text-gray-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors cursor-pointer"
                        title="Quitar propietario">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    {/if}
                  </div>
                </div>

                {#if row.modo === 'existente'}
                  <select
                    value={row.propietario_id}
                    on:change={(e) => onSelectPropietario(e, row.clave)}
                    required
                    class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent">
                    <option value="">Seleccionar propietario...</option>
                    {#each propietarios as p}
                      <option value={p.id}>{p.nombre} ({p.dni_cuit})</option>
                    {/each}
                  </select>
                {:else}
                  <div class="grid grid-cols-2 gap-2">
                    <input type="text" placeholder="Nombre *" bind:value={row.nombre}
                      class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
                    <input type="text" placeholder="DNI/CUIT *" bind:value={row.dni_cuit}
                      class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
                    <input type="text" placeholder="Teléfono" bind:value={row.telefono}
                      class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
                    <input type="text" placeholder="Email" bind:value={row.email}
                      class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
                    <input type="text" placeholder="Dirección" bind:value={row.direccion}
                      class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
                  </div>
                {/if}
              </div>
            {/each}
          </div>

          {#if showTotalWarning}
            <p class="text-xs text-amber-600 dark:text-amber-400 mt-2">
              La suma de participaciones es {totalPorcentaje}% (debería ser 100%).
            </p>
          {/if}
        </div>

        <div class="flex justify-end gap-3 pt-2">
          <button type="button" on:click={cancel} disabled={submitting}
            class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors cursor-pointer disabled:opacity-50">
            Cancelar
          </button>
          <button type="submit" disabled={submitting || !form.direccion}
            class="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 disabled:bg-primary-400 rounded-lg transition-colors cursor-pointer disabled:cursor-not-allowed">
            {submitting ? 'Creando...' : 'Crear inmueble'}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}
