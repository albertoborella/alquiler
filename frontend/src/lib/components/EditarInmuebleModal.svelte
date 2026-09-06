<script lang="ts">
  import { onMount } from 'svelte';
  import { auth } from '$lib/stores/auth';
  import { api } from '$lib/api';
  import type { InmuebleDashboard, Persona } from '$lib/api';

  export let open = false;
  export let inmueble: InmuebleDashboard | null = null;
  export let onClose: () => void = () => {};
  export let onUpdated: () => void = () => {};

  interface PropietarioRow {
    clave: number;
    modo: 'existente' | 'nuevo';
    propietario_id: string;
    porcentaje: string;
    nombre: string;
    cuit: string;
    telefono: string;
    email: string;
    direccion: string;
  }

  let form = {
    direccion: '',
    superficie: '',
    habitaciones: '',
    banos: '',
    dormitorios: '',
    comodidades: '',
    descripcion: '',
  };

  let propietarios: Persona[] = [];
  let propietariosLoading = false;
  let rows: PropietarioRow[] = [];
  let nextKey = 1;

  let submitting = false;
  let success = '';
  let error = '';

  $: isUrban = inmueble?.categoria === 'urbano';
  $: totalPorcentaje = rows.reduce((acc, r) => acc + (parseFloat(r.porcentaje) || 0), 0);
  $: showTotalWarning = rows.length > 1 && totalPorcentaje !== 100;

  // Load all propietarios for the select (eagerly + on open).
  onMount(() => {
    if ($auth.token && propietarios.length === 0) loadPropietarios();
  });

  let previousOpen = false;

  // Populate form when modal opens AND inmueble is available.
  // Svelte renders {#if open && inmueble} BEFORE props settle, so inmueble
  // may still be null on the first render after `open` flips true.  We handle
  // this by reacting to BOTH `open` and `inmueble` independently.
  let populatedFor: string | null = null;
  $: if (open && inmueble && populatedFor !== inmueble.id) {
    populatedFor = inmueble.id;
    populateForm();
    loadPropietarios();
  }
  // Reset the guard when the modal closes so the next inmueble repopulates.
  $: if (!open) {
    populatedFor = null;
  }
  $: previousOpen = open;

  function populateForm() {
    if (!inmueble) return;
    form = {
      direccion: inmueble.direccion || '',
      superficie: inmueble.superficie != null ? String(inmueble.superficie) : '',
      habitaciones: inmueble.habitaciones != null ? String(inmueble.habitaciones) : '',
      banos: inmueble.banos != null ? String(inmueble.banos) : '',
      dormitorios: inmueble.dormitorios != null ? String(inmueble.dormitorios) : '',
      comodidades: inmueble.comodidades || '',
      descripcion: inmueble.descripcion || '',
    };
    success = '';
    error = '';

    // Build rows from existing propietarios on this inmueble.
    rows = (inmueble.propietarios || []).map((p) => {
      const r: PropietarioRow = {
        clave: nextKey++,
        modo: 'existente',
        propietario_id: p.id,
        porcentaje: String(p.porcentaje_participacion ?? 100),
        nombre: p.nombre,
        cuit: p.dni_cuit,
        telefono: '',
        email: '',
        direccion: '',
      };
      return r;
    });
    if (rows.length === 0) {
      rows = [newRow('existente', '100')];
    }
  }

  function newRow(modo: 'existente' | 'nuevo', porcentaje = ''): PropietarioRow {
    const r: PropietarioRow = {
      clave: nextKey++,
      modo,
      propietario_id: '',
      porcentaje: porcentaje === '' ? '' : String(porcentaje),
      nombre: '',
      cuit: '',
      telefono: '',
      email: '',
      direccion: '',
    };
    return r;
  }

  async function loadPropietarios() {
    if (!$auth.token) return;
    propietariosLoading = true;
    try {
      propietarios = await api.getPropietarios($auth.token);
    } catch (err) {
      // Non-fatal: the user can still use "Crear nuevo" mode.
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
    rows = rows.map((r) =>
      r.clave === clave ? { ...r, modo, propietario_id: '', nombre: '', cuit: '' } : r
    );
  }

  function setField(clave: number, field: keyof PropietarioRow, value: string) {
    rows = rows.map((r) => (r.clave === clave ? { ...r, [field]: value } : r));
  }

  function cancel() {
    onClose();
  }

  async function submit() {
    if (!$auth.token || !inmueble) {
      console.error('[EditarInmueble] submit abortado: token o inmueble null', { token: !!$auth.token, inmueble });
      return;
    }
    submitting = true;
    error = '';
    success = '';

    try {
      // 1. Validate rows
      const validRows = rows.filter(
        (r) => (r.modo === 'existente' ? r.propietario_id : r.nombre && r.cuit)
      );
      console.log('[EditarInmueble] validRows:', validRows.length, validRows);
      if (validRows.length === 0) {
        error = 'Debés agregar al menos un propietario';
        submitting = false;
        return;
      }

      // 2. Update inmueble fields
      const inmueblePayload = {
        direccion: form.direccion || undefined,
        superficie: form.superficie ? parseFloat(form.superficie) : undefined,
        habitaciones: isUrban && form.habitaciones ? parseInt(form.habitaciones) : undefined,
        banos: isUrban && form.banos ? parseInt(form.banos) : undefined,
        dormitorios: isUrban && form.dormitorios ? parseInt(form.dormitorios) : undefined,
        comodidades: isUrban ? (form.comodidades || undefined) : undefined,
        descripcion: form.descripcion || undefined,
      };
      console.log('[EditarInmueble] updateInmueble payload:', inmueblePayload);
      const updateResult = await api.updateInmueble($auth.token, inmueble.id, inmueblePayload);
      console.log('[EditarInmueble] updateInmueble OK:', updateResult);

      // 3. Create any new propietarios and collect their IDs.
      const resolvedRows: Array<{ propietario_id: string; porcentaje_participacion: number }> = [];
      for (const r of validRows) {
        if (r.modo === 'existente') {
          resolvedRows.push({
            propietario_id: r.propietario_id,
            porcentaje_participacion: parseFloat(r.porcentaje) || 0,
          });
        } else {
          // Create the propietario first, then use its ID.
          console.log('[EditarInmueble] creando propietario nuevo:', r.nombre, r.dni_cuit);
          const created = await api.createPersona($auth.token, {
            nombre: r.nombre,
            cuit: r.cuit,
            rol: 'propietario',
            telefono: r.telefono || undefined,
            email: r.email || undefined,
            direccion: r.direccion || undefined,
          });
          console.log('[EditarInmueble] propietario creado:', created);
          resolvedRows.push({
            propietario_id: created.id,
            porcentaje_participacion: parseFloat(r.porcentaje) || 0,
          });
        }
      }

      // 4. Replace all copropiedad for this inmueble.
      console.log('[EditarInmueble] updateCopropietarios payload:', resolvedRows);
      await api.updateCopropietarios($auth.token, inmueble.id, resolvedRows);
      console.log('[EditarInmueble] updateCopropietarios OK');

      success = 'Inmueble actualizado exitosamente';
      setTimeout(() => {
        onClose();
        onUpdated();
      }, 1200);
    } catch (err) {
      console.error('[EditarInmueble] ERROR en submit:', err);
      error = err instanceof Error ? err.message : 'Error al actualizar inmueble';
    } finally {
      submitting = false;
    }
  }
</script>

{#if open && inmueble}
  <div class="fixed inset-0 z-50 flex items-center justify-center">
    <div class="absolute inset-0 bg-black/50" on:click={cancel} role="presentation"></div>
    <div class="relative bg-white dark:bg-gray-900 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 w-full max-w-2xl mx-4 p-6 max-h-[90vh] overflow-y-auto">
      <div class="flex items-center gap-3 mb-5">
        <div class="w-10 h-10 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">
          <svg class="w-5 h-5 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
        </div>
        <div>
          <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100">Editar inmueble</h3>
          <p class="text-sm text-gray-500 dark:text-gray-400">{inmueble.direccion}</p>
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
        <!-- Categoria (fija) -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <p class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Categoría</p>
            <div class="px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 capitalize">
              {inmueble.categoria === 'urbano' ? 'Urbano' : 'Rural'}
            </div>
          </div>
          <div>
            <label for="edit-inm-superficie" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Superficie ({isUrban ? 'm²' : 'ha'})
            </label>
            <input id="edit-inm-superficie" type="number" step="0.01" min="0" bind:value={form.superficie} placeholder="0.00"
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
          </div>
        </div>

        <!-- Direccion -->
        <div>
          <label for="edit-inm-direccion" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Dirección *</label>
          <input id="edit-inm-direccion" type="text" bind:value={form.direccion} required placeholder="Ej: Av. Corrientes 1234"
            class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
        </div>

        <!-- Campos urbanos -->
        {#if isUrban}
          <div class="grid grid-cols-3 gap-4">
            <div>
              <label for="edit-inm-hab" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Habitaciones</label>
              <input id="edit-inm-hab" type="number" min="0" bind:value={form.habitaciones} placeholder="0"
                class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
            </div>
            <div>
              <label for="edit-inm-banos" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Baños</label>
              <input id="edit-inm-banos" type="number" min="0" bind:value={form.banos} placeholder="0"
                class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
            </div>
            <div>
              <label for="edit-inm-dorm" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Dormitorios</label>
              <input id="edit-inm-dorm" type="number" min="0" bind:value={form.dormitorios} placeholder="0"
                class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
            </div>
          </div>

          <div>
            <label for="edit-inm-comodidades" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Comodidades</label>
            <input id="edit-inm-comodidades" type="text" bind:value={form.comodidades} placeholder="Ej: pileta, parrilla, garage"
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
          </div>
        {/if}

        <!-- Descripcion -->
        <div>
          <label for="edit-inm-descripcion" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Descripción</label>
          <textarea id="edit-inm-descripcion" bind:value={form.descripcion} rows="2" placeholder="Notas adicionales..."
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
                      <label for="edit-porc-{row.clave}" class="text-xs text-gray-500 dark:text-gray-400">%</label>
                      <input id="edit-porc-{row.clave}" type="number" step="0.01" min="0" max="100" bind:value={row.porcentaje} placeholder="100"
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
                    bind:value={row.propietario_id}
                    required
                    class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent">
                    <option value="">Seleccionar propietario...</option>
                    {#each propietarios as p}
                      <option value={p.id}>{p.nombre} ({p.cuit})</option>
                    {/each}
                  </select>
                {:else}
                  <div class="grid grid-cols-2 gap-2">
                    <input type="text" placeholder="Nombre *" bind:value={row.nombre}
                      class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
                    <input type="text" placeholder="CUIT *" bind:value={row.cuit}
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
            {submitting ? 'Guardando...' : 'Guardar cambios'}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}
