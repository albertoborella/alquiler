<script lang="ts">
  import { auth } from '$lib/stores/auth';
  import { api } from '$lib/api';
  import type { InmuebleDashboard } from '$lib/api';

  export let open = false;
  export let inmueble: InmuebleDashboard | null = null;
  export let onClose: () => void = () => {};
  export let onUpdated: () => void = () => {};

  let form = {
    direccion: '',
    superficie: '',
    habitaciones: '',
    banos: '',
    dormitorios: '',
    comodidades: '',
    descripcion: '',
  };

  let submitting = false;
  let success = '';
  let error = '';

  let previousOpen = false;
  $: if (open && !previousOpen && inmueble) {
    populateForm();
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
  }

  function cancel() {
    onClose();
  }

  $: isUrban = inmueble?.categoria === 'urbano';

  async function submit() {
    if (!$auth.token || !inmueble) return;
    submitting = true;
    error = '';
    success = '';
    try {
      await api.updateInmueble($auth.token, inmueble.id, {
        direccion: form.direccion || undefined,
        superficie: form.superficie ? parseFloat(form.superficie) : undefined,
        habitaciones: isUrban && form.habitaciones ? parseInt(form.habitaciones) : undefined,
        banos: isUrban && form.banos ? parseInt(form.banos) : undefined,
        dormitorios: isUrban && form.dormitorios ? parseInt(form.dormitorios) : undefined,
        comodidades: isUrban ? (form.comodidades || undefined) : undefined,
        descripcion: form.descripcion || undefined,
      });

      success = 'Inmueble actualizado exitosamente';
      setTimeout(() => {
        onClose();
        onUpdated();
      }, 1200);
    } catch (err) {
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
