<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { auth } from '$lib/stores/auth';
  import { api } from '$lib/api';
  import type { Persona } from '$lib/api';

  let personas: Persona[] = [];
  let loading = true;
  let error = '';

  // ── Filter ──
  let filterRol = '';
  $: filteredPersonas = filterRol
    ? personas.filter((p) => p.rol === filterRol)
    : personas;

  // ── Create/Edit modal ──
  let showModal = false;
  let editTarget: Persona | null = null;
  let form = {
    nombre: '',
    cuit: '',
    iva: '',
    telefono: '',
    email: '',
    direccion: '',
    rol: 'propietario',
  };
  let submitting = false;
  let success = '';
  let formError = '';

  // ── Delete modal ──
  let showDeleteConfirm = false;
  let deleteTarget: Persona | null = null;
  let deleting = false;

  $: isAdmin = $auth.user?.role === 'admin';

  onMount(() => {
    if (!$auth.token) {
      goto('/login');
      return;
    }
    loadPersonas();
  });

  async function loadPersonas() {
    if (!$auth.token) return;
    loading = true;
    error = '';
    try {
      personas = await api.getPersonas($auth.token);
    } catch (err) {
      error = err instanceof Error ? err.message : 'Error al cargar personas';
    } finally {
      loading = false;
    }
  }

  // ── Create / Edit ──
  function openCreate() {
    editTarget = null;
    form = { nombre: '', cuit: '', iva: '', telefono: '', email: '', direccion: '', rol: 'propietario' };
    success = '';
    formError = '';
    showModal = true;
  }

  function openEdit(p: Persona) {
    editTarget = p;
    form = {
      nombre: p.nombre,
      cuit: p.cuit ?? '',
      iva: p.iva ?? '',
      telefono: p.telefono ?? '',
      email: p.email ?? '',
      direccion: p.direccion ?? '',
      rol: p.rol ?? 'propietario',
    };
    success = '';
    formError = '';
    showModal = true;
  }

  function cancelModal() {
    showModal = false;
    editTarget = null;
  }

  async function executeSubmit() {
    if (!$auth.token) return;
    submitting = true;
    formError = '';
    success = '';
    try {
      if (editTarget) {
        await api.updatePersona($auth.token, editTarget.id, {
          nombre: form.nombre,
          cuit: form.cuit,
          iva: form.iva || undefined,
          telefono: form.telefono || undefined,
          email: form.email || undefined,
          direccion: form.direccion || undefined,
          rol: form.rol,
        });
        success = 'Persona actualizada';
      } else {
        await api.createPersona($auth.token, {
          nombre: form.nombre,
          cuit: form.cuit,
          iva: form.iva || undefined,
          telefono: form.telefono || undefined,
          email: form.email || undefined,
          direccion: form.direccion || undefined,
          rol: form.rol,
        });
        success = 'Persona creada';
      }
      await loadPersonas();
      setTimeout(() => {
        showModal = false;
        editTarget = null;
      }, 1200);
    } catch (err) {
      formError = err instanceof Error ? err.message : 'Error al guardar persona';
    } finally {
      submitting = false;
    }
  }

  // ── Delete ──
  function confirmDelete(p: Persona) {
    deleteTarget = p;
    showDeleteConfirm = true;
  }

  function cancelDelete() {
    deleteTarget = null;
    showDeleteConfirm = false;
  }

  async function executeDelete() {
    if (!deleteTarget || !$auth.token) return;
    deleting = true;
    try {
      await api.deletePersona($auth.token, deleteTarget.id);
      personas = personas.filter((p) => p.id !== deleteTarget!.id);
      showDeleteConfirm = false;
      deleteTarget = null;
    } catch (err) {
      error = err instanceof Error ? err.message : 'Error al eliminar persona';
      showDeleteConfirm = false;
    } finally {
      deleting = false;
    }
  }

  function rolBadge(rol: string): string {
    switch (rol) {
      case 'propietario':
        return 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200';
      case 'inquilino':
        return 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200';
      case 'ambos':
        return 'bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-200';
      default:
        return 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400';
    }
  }

  function rolLabel(rol: string): string {
    switch (rol) {
      case 'propietario': return 'Propietario';
      case 'inquilino': return 'Inquilino';
      case 'ambos': return 'Ambos';
      default: return rol;
    }
  }

  function formatDate(d: string | null): string {
    if (!d) return '-';
    const [y, m, dd] = d.split('T')[0].split('-');
    return `${y.slice(2)}/${m}/${dd}`;
  }
</script>

<div class="max-w-7xl mx-auto px-4 md:px-6 lg:px-8 py-6 md:py-8">
  <div class="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800">
    <!-- Header bar -->
    <div class="px-4 md:px-6 py-3 border-b border-gray-100 dark:border-gray-800">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 class="text-xl font-bold text-gray-900 dark:text-gray-100">Personas</h1>
          <p class="text-gray-500 dark:text-gray-400 mt-0.5 text-sm">Gestión de propietarios e inquilinos</p>
        </div>
        {#if isAdmin}
          <button
            on:click={openCreate}
            class="inline-flex items-center gap-2 px-3.5 py-1.5 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 active:bg-primary-800 rounded-lg shadow-sm transition-colors cursor-pointer"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Nueva persona
          </button>
        {/if}
      </div>
    </div>

    <!-- Filters -->
    <div class="px-4 md:px-6 py-2 border-b border-gray-100 dark:border-gray-800">
      <div class="flex flex-wrap items-center gap-2">
        <button
          on:click={() => { filterRol = ''; }}
          class="px-3 py-1 text-xs font-medium rounded-full transition-colors cursor-pointer {filterRol === '' ? 'bg-primary-100 dark:bg-primary-900/40 text-primary-700 dark:text-primary-300' : 'text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'}">
          Todos
        </button>
        <button
          on:click={() => { filterRol = 'propietario'; }}
          class="px-3 py-1 text-xs font-medium rounded-full transition-colors cursor-pointer {filterRol === 'propietario' ? 'bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300' : 'text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'}">
          Propietarios
        </button>
        <button
          on:click={() => { filterRol = 'inquilino'; }}
          class="px-3 py-1 text-xs font-medium rounded-full transition-colors cursor-pointer {filterRol === 'inquilino' ? 'bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300' : 'text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'}">
          Inquilinos
        </button>
        <button
          on:click={() => { filterRol = 'ambos'; }}
          class="px-3 py-1 text-xs font-medium rounded-full transition-colors cursor-pointer {filterRol === 'ambos' ? 'bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300' : 'text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'}">
          Ambos
        </button>
        <span class="ml-auto text-sm text-gray-500 dark:text-gray-400">
          {filteredPersonas.length} persona{filteredPersonas.length !== 1 ? 's' : ''}
        </span>
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
            <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/4"></div>
            <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/6"></div>
            <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/6"></div>
            <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/8"></div>
          </div>
        {/each}
      </div>
    {:else if filteredPersonas.length === 0}
      <div class="px-6 py-16 text-center">
        <div class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg px-6 py-5 max-w-md mx-auto mb-6">
          <div class="flex items-center gap-3">
            <svg class="w-5 h-5 text-amber-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <p class="text-sm text-amber-700 dark:text-amber-300 font-medium">
              {filterRol ? 'No hay personas con ese rol' : 'No hay personas cargadas'}
            </p>
          </div>
          <p class="text-xs text-amber-600 dark:text-amber-400 mt-2">
            Cargue las primeras personas para poder generar contratos.
          </p>
        </div>
        <svg class="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        <p class="text-gray-500 dark:text-gray-400 text-sm">No se encontraron personas</p>
      </div>
    {:else}
      <div class="overflow-x-auto -mx-4 md:mx-0">
        <table class="w-full min-w-[700px]">
          <thead>
            <tr class="text-left text-[11px] font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider border-b border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-800/50">
              <th class="px-3 md:px-4 py-1">Nombre</th>
              <th class="px-3 md:px-4 py-1">CUIT</th>
              <th class="px-3 md:px-4 py-1 hidden sm:table-cell">IVA</th>
              <th class="px-3 md:px-4 py-1 hidden sm:table-cell">Telefono</th>
              <th class="px-3 md:px-4 py-1 hidden md:table-cell">Email</th>
              <th class="px-3 md:px-4 py-1 hidden lg:table-cell">Direccion</th>
              <th class="px-3 md:px-4 py-1">Rol</th>
              <th class="px-3 md:px-4 py-1 hidden lg:table-cell">Creado</th>
              {#if isAdmin}
                <th class="px-3 md:px-4 py-1 text-right">Acciones</th>
              {/if}
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100 dark:divide-gray-800">
            {#each filteredPersonas as p (p.id)}
              <tr class="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                <td class="px-3 md:px-4 py-1 text-xs text-gray-900 dark:text-gray-100">{p.nombre}</td>
                <td class="px-3 md:px-4 py-1 text-xs text-gray-700 dark:text-gray-300 font-mono">{p.cuit}</td>
                <td class="px-3 md:px-4 py-1 text-xs text-gray-600 dark:text-gray-400 hidden sm:table-cell">{p.iva ?? '-'}</td>
                <td class="px-3 md:px-4 py-1 text-xs text-gray-600 dark:text-gray-400 hidden sm:table-cell">{p.telefono ?? '-'}</td>
                <td class="px-3 md:px-4 py-1 text-xs text-gray-600 dark:text-gray-400 hidden md:table-cell">{p.email ?? '-'}</td>
                <td class="px-3 md:px-4 py-1 text-xs text-gray-600 dark:text-gray-400 hidden lg:table-cell">{p.direccion ?? '-'}</td>
                <td class="px-3 md:px-4 py-2">
                  <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium {rolBadge(p.rol)}">
                    {rolLabel(p.rol)}
                  </span>
                </td>
                <td class="px-3 md:px-4 py-1 text-xs text-gray-500 dark:text-gray-400 hidden lg:table-cell">{formatDate(p.created_at)}</td>
                {#if isAdmin}
                  <td class="px-3 md:px-4 py-1 text-right">
                    <div class="flex items-center justify-end gap-0.5">
                      <button
                        on:click={() => openEdit(p)}
                        class="p-1.5 rounded-md text-gray-400 hover:text-violet-600 hover:bg-violet-50 dark:hover:bg-violet-900/20 transition-colors cursor-pointer"
                        title="Editar persona"
                      >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </button>
                      <button
                        on:click={() => confirmDelete(p)}
                        class="p-1.5 rounded-md text-gray-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors cursor-pointer"
                        title="Eliminar persona"
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
<!-- CREATE/EDIT MODAL                                         -->
<!-- ═══════════════════════════════════════════════════════════ -->
{#if showModal}
  <div class="fixed inset-0 z-50 flex items-center justify-center">
    <div class="absolute inset-0 bg-black/50" on:click={cancelModal} role="presentation"></div>
    <div class="relative bg-white dark:bg-gray-900 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 w-full max-w-lg mx-4 p-6">
      <div class="flex items-center gap-3 mb-5">
        <div class="w-10 h-10 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">
          <svg class="w-5 h-5 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </div>
        <div>
          <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100">{editTarget ? 'Editar persona' : 'Nueva persona'}</h3>
        </div>
      </div>

      {#if success}
        <div class="bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-300 text-sm rounded-lg px-4 py-3 border border-emerald-100 dark:border-emerald-800 mb-4">
          {success}
        </div>
      {/if}

      {#if formError}
        <div class="bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 text-sm rounded-lg px-4 py-3 border border-red-100 dark:border-red-800 mb-4">
          {formError}
        </div>
      {/if}

      <form on:submit|preventDefault={executeSubmit} class="space-y-4">
        <!-- Rol (prominent) -->
        <div>
          <label for="per-rol" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Rol *</label>
          <select id="per-rol" bind:value={form.rol} required
            class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent">
            <option value="propietario">Propietario</option>
            <option value="inquilino">Inquilino</option>
            <option value="ambos">Ambos</option>
          </select>
        </div>

        <div>
          <label for="per-nombre" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Nombre *</label>
          <input id="per-nombre" type="text" bind:value={form.nombre} required placeholder="Nombre completo"
            class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="per-cuit" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">CUIT *</label>
            <input id="per-cuit" type="text" bind:value={form.cuit} required placeholder="CUIT"
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
          </div>
          <div>
            <label for="per-iva" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">IVA</label>
            <select id="per-iva" bind:value={form.iva}
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent">
              <option value="">Seleccionar...</option>
              <option value="Monotributo">Monotributo</option>
              <option value="Resp. inscripto">Resp. inscripto</option>
              <option value="Exento">Exento</option>
            </select>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="per-telefono" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Telefono</label>
            <input id="per-telefono" type="text" bind:value={form.telefono} placeholder="Telefono"
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
          </div>
          <div>
            <label for="per-email" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Email</label>
            <input id="per-email" type="email" bind:value={form.email} placeholder="email@ejemplo.com"
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
          </div>
        </div>

        <div>
          <label for="per-direccion" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Direccion</label>
          <input id="per-direccion" type="text" bind:value={form.direccion} placeholder="Direccion personal"
            class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
        </div>

        <div class="flex justify-end gap-3 pt-2">
          <button type="button" on:click={cancelModal} disabled={submitting}
            class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors cursor-pointer disabled:opacity-50">
            Cancelar
          </button>
          <button type="submit" disabled={submitting || !form.nombre || !form.cuit}
            class="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 disabled:bg-primary-400 rounded-lg transition-colors cursor-pointer disabled:cursor-not-allowed">
            {submitting ? 'Guardando...' : editTarget ? 'Actualizar' : 'Crear persona'}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

<!-- ═══════════════════════════════════════════════════════════ -->
<!-- DELETE CONFIRMATION MODAL                                 -->
<!-- ═══════════════════════════════════════════════════════════ -->
{#if showDeleteConfirm && deleteTarget}
  <div class="fixed inset-0 z-50 flex items-center justify-center">
    <div class="absolute inset-0 bg-black/50" on:click={cancelDelete} role="presentation"></div>
    <div class="relative bg-white dark:bg-gray-900 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 w-full max-w-md mx-4 p-6">
      <div class="flex items-center gap-3 mb-4">
        <div class="w-10 h-10 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
          <svg class="w-5 h-5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
        <div>
          <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100">Eliminar persona</h3>
          <p class="text-sm text-gray-500 dark:text-gray-400">Esta accion no se puede deshacer</p>
        </div>
      </div>
      <p class="text-sm text-gray-700 dark:text-gray-300 mb-6">
        Seguro que queres eliminar a <strong class="font-medium">{deleteTarget.nombre}</strong> (CUIT: {deleteTarget.cuit})?
      </p>
      <div class="flex justify-end gap-3">
        <button on:click={cancelDelete} disabled={deleting}
          class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors cursor-pointer disabled:opacity-50">
          Cancelar
        </button>
        <button on:click={executeDelete} disabled={deleting}
          class="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 disabled:bg-red-400 rounded-lg transition-colors cursor-pointer disabled:cursor-not-allowed">
          {deleting ? 'Eliminando...' : 'Eliminar'}
        </button>
      </div>
    </div>
  </div>
{/if}
