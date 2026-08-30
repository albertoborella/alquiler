<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { auth } from '$lib/stores/auth';
  import { api } from '$lib/api';
  import type { Propietario } from '$lib/api';

  let propietarios: Propietario[] = [];
  let loading = true;
  let error = '';

  // ── Create modal ──
  let showCreateModal = false;
  let createForm = { nombre: '', dni_cuit: '', telefono: '', email: '', direccion: '' };
  let creating = false;
  let createSuccess = '';
  let createError = '';

  // ── Edit modal ──
  let showEditModal = false;
  let editTarget: Propietario | null = null;
  let editForm = { nombre: '', dni_cuit: '', telefono: '', email: '', direccion: '' };
  let editing = false;
  let editSuccess = '';
  let editError = '';

  // ── Delete modal ──
  let showDeleteConfirm = false;
  let deleteTarget: Propietario | null = null;
  let deleting = false;

  $: isAdmin = $auth.user?.role === 'admin';

  onMount(() => {
    if (!$auth.token) {
      goto('/login');
      return;
    }
    loadPropietarios();
  });

  async function loadPropietarios() {
    if (!$auth.token) return;
    loading = true;
    error = '';
    try {
      propietarios = await api.getPropietarios($auth.token);
    } catch (err) {
      error = err instanceof Error ? err.message : 'Error al cargar propietarios';
    } finally {
      loading = false;
    }
  }

  function openCreate() {
    createForm = { nombre: '', dni_cuit: '', telefono: '', email: '', direccion: '' };
    createSuccess = '';
    createError = '';
    showCreateModal = true;
  }

  async function submitCreate() {
    if (!$auth.token) return;
    creating = true;
    createError = '';
    createSuccess = '';
    try {
      await api.createPropietario($auth.token, {
        nombre: createForm.nombre,
        dni_cuit: createForm.dni_cuit,
        telefono: createForm.telefono || undefined,
        email: createForm.email || undefined,
        direccion: createForm.direccion || undefined,
      });
      createSuccess = 'Propietario creado exitosamente';
      setTimeout(() => { showCreateModal = false; loadPropietarios(); }, 1200);
    } catch (err) {
      createError = err instanceof Error ? err.message : 'Error al crear propietario';
    } finally {
      creating = false;
    }
  }

  function openEdit(p: Propietario) {
    editTarget = p;
    editForm = {
      nombre: p.nombre,
      dni_cuit: p.dni_cuit,
      telefono: p.telefono || '',
      email: p.email || '',
      direccion: p.direccion || '',
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
      await api.updatePropietario($auth.token, editTarget.id, {
        nombre: editForm.nombre,
        dni_cuit: editForm.dni_cuit,
        telefono: editForm.telefono || undefined,
        email: editForm.email || undefined,
        direccion: editForm.direccion || undefined,
      });
      editSuccess = 'Propietario actualizado';
      setTimeout(() => { showEditModal = false; loadPropietarios(); }, 1200);
    } catch (err) {
      editError = err instanceof Error ? err.message : 'Error al actualizar';
    } finally {
      editing = false;
    }
  }

  function confirmDelete(p: Propietario) {
    deleteTarget = p;
    showDeleteConfirm = true;
  }

  async function submitDelete() {
    if (!$auth.token || !deleteTarget) return;
    deleting = true;
    try {
      await api.deletePropietario($auth.token, deleteTarget.id);
      showDeleteConfirm = false;
      deleteTarget = null;
      loadPropietarios();
    } catch (err) {
      error = err instanceof Error ? err.message : 'Error al eliminar';
    } finally {
      deleting = false;
    }
  }

  function formatDate(d: string | null): string {
    if (!d) return '-';
    return new Date(d).toLocaleDateString('es-AR', { day: '2-digit', month: '2-digit', year: 'numeric' });
  }
</script>

<div class="max-w-7xl mx-auto px-4 md:px-6 lg:px-8 py-6 md:py-8">
  <div class="mb-6 md:mb-8">
    <h1 class="text-xl md:text-2xl font-bold text-gray-900 dark:text-gray-100">Propietarios</h1>
    <p class="text-gray-500 dark:text-gray-400 mt-1">Gestión de propietarios de inmuebles</p>
  </div>

  <div class="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800">
    <!-- Header bar -->
    <div class="px-4 md:px-6 py-3 border-b border-gray-100 dark:border-gray-800">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <p class="text-sm text-gray-500 dark:text-gray-400">
          {propietarios.length} propietario{propietarios.length !== 1 ? 's' : ''}
        </p>
        {#if isAdmin}
          <button
            on:click={openCreate}
            class="inline-flex items-center gap-2 px-3.5 py-1.5 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 active:bg-primary-800 rounded-lg shadow-sm transition-colors cursor-pointer"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Nuevo propietario
          </button>
        {/if}
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
            <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/5"></div>
            <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/6"></div>
          </div>
        {/each}
      </div>
    {:else if propietarios.length === 0}
      <div class="px-6 py-16 text-center">
        <div class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg px-6 py-5 max-w-md mx-auto mb-6">
          <div class="flex items-center gap-3">
            <svg class="w-5 h-5 text-amber-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <p class="text-sm text-amber-700 dark:text-amber-300 font-medium">No hay propietarios cargados</p>
          </div>
        </div>
      </div>
    {:else}
      <div class="overflow-x-auto -mx-4 md:mx-0">
        <table class="w-full min-w-[640px]">
          <thead>
            <tr class="text-left text-[11px] font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider border-b border-gray-100 dark:border-gray-800">
              <th class="px-3 md:px-4 py-1">Nombre</th>
              <th class="px-3 md:px-4 py-1">DNI/CUIT</th>
              <th class="px-3 md:px-4 py-1 hidden sm:table-cell">Teléfono</th>
              <th class="px-3 md:px-4 py-1 hidden md:table-cell">Email</th>
              <th class="px-3 md:px-4 py-1 hidden lg:table-cell">Dirección</th>
              <th class="px-3 md:px-4 py-1 hidden lg:table-cell">Creado</th>
              {#if isAdmin}
                <th class="px-3 md:px-4 py-1 text-right">Acciones</th>
              {/if}
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50 dark:divide-gray-800">
            {#each propietarios as p (p.id)}
              <tr class="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                <td class="px-3 md:px-4 py-2 text-sm font-medium text-gray-900 dark:text-gray-100">{p.nombre}</td>
                <td class="px-3 md:px-4 py-2 text-sm text-gray-700 dark:text-gray-300 font-mono">{p.dni_cuit}</td>
                <td class="px-3 md:px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hidden sm:table-cell">{p.telefono || '-'}</td>
                <td class="px-3 md:px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hidden md:table-cell">{p.email || '-'}</td>
                <td class="px-3 md:px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hidden lg:table-cell">{p.direccion || '-'}</td>
                <td class="px-3 md:px-4 py-2 text-sm text-gray-500 dark:text-gray-400 hidden lg:table-cell">{formatDate(p.created_at)}</td>
                {#if isAdmin}
                  <td class="px-3 md:px-4 py-2 text-right">
                    <div class="flex items-center justify-end gap-1">
                      <button
                        on:click={() => openEdit(p)}
                        class="p-1.5 rounded-md text-gray-400 hover:text-primary-600 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-colors cursor-pointer"
                        title="Editar propietario"
                      >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </button>
                      <button
                        on:click={() => confirmDelete(p)}
                        class="p-1.5 rounded-md text-gray-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors cursor-pointer"
                        title="Eliminar propietario"
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
<!-- CREATE MODAL                                                -->
<!-- ═══════════════════════════════════════════════════════════ -->
{#if showCreateModal}
  <div class="fixed inset-0 z-50 flex items-center justify-center">
    <div class="absolute inset-0 bg-black/50" on:click={() => { showCreateModal = false; }} role="presentation"></div>
    <div class="relative bg-white dark:bg-gray-900 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 w-full max-w-lg mx-4 p-6">
      <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100 mb-4">Nuevo propietario</h3>
      {#if createError}
        <div class="bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 text-sm rounded-lg px-4 py-3 border border-red-100 dark:border-red-800 mb-4">{createError}</div>
      {/if}
      {#if createSuccess}
        <div class="bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-300 text-sm rounded-lg px-4 py-3 border border-emerald-100 dark:border-emerald-800 mb-4">{createSuccess}</div>
      {/if}
      <form on:submit|preventDefault={submitCreate} class="space-y-3">
        <div>
          <label for="cr-nombre" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Nombre *</label>
          <input id="cr-nombre" type="text" bind:value={createForm.nombre} required
            class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
        </div>
        <div>
          <label for="cr-dni" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">DNI/CUIT *</label>
          <input id="cr-dni" type="text" bind:value={createForm.dni_cuit} required
            class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label for="cr-tel" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Teléfono</label>
            <input id="cr-tel" type="text" bind:value={createForm.telefono}
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
          </div>
          <div>
            <label for="cr-email" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Email</label>
            <input id="cr-email" type="email" bind:value={createForm.email}
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
          </div>
        </div>
        <div>
          <label for="cr-dir" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Dirección</label>
          <input id="cr-dir" type="text" bind:value={createForm.direccion}
            class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
        </div>
        <div class="flex justify-end gap-3 pt-2">
          <button type="button" on:click={() => { showCreateModal = false; }} disabled={creating}
            class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors cursor-pointer disabled:opacity-50">
            Cancelar
          </button>
          <button type="submit" disabled={creating || !createForm.nombre || !createForm.dni_cuit}
            class="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 disabled:bg-primary-400 rounded-lg transition-colors cursor-pointer disabled:cursor-not-allowed">
            {creating ? 'Creando...' : 'Crear propietario'}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

<!-- ═══════════════════════════════════════════════════════════ -->
<!-- EDIT MODAL                                                  -->
<!-- ═══════════════════════════════════════════════════════════ -->
{#if showEditModal && editTarget}
  <div class="fixed inset-0 z-50 flex items-center justify-center">
    <div class="absolute inset-0 bg-black/50" on:click={() => { showEditModal = false; }} role="presentation"></div>
    <div class="relative bg-white dark:bg-gray-900 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 w-full max-w-lg mx-4 p-6">
      <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100 mb-4">Editar propietario</h3>
      {#if editError}
        <div class="bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 text-sm rounded-lg px-4 py-3 border border-red-100 dark:border-red-800 mb-4">{editError}</div>
      {/if}
      {#if editSuccess}
        <div class="bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-300 text-sm rounded-lg px-4 py-3 border border-emerald-100 dark:border-emerald-800 mb-4">{editSuccess}</div>
      {/if}
      <form on:submit|preventDefault={submitEdit} class="space-y-3">
        <div>
          <label for="ed-nombre" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Nombre *</label>
          <input id="ed-nombre" type="text" bind:value={editForm.nombre} required
            class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
        </div>
        <div>
          <label for="ed-dni" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">DNI/CUIT *</label>
          <input id="ed-dni" type="text" bind:value={editForm.dni_cuit} required
            class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label for="ed-tel" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Teléfono</label>
            <input id="ed-tel" type="text" bind:value={editForm.telefono}
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
          </div>
          <div>
            <label for="ed-email" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Email</label>
            <input id="ed-email" type="email" bind:value={editForm.email}
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
          </div>
        </div>
        <div>
          <label for="ed-dir" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Dirección</label>
          <input id="ed-dir" type="text" bind:value={editForm.direccion}
            class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
        </div>
        <div class="flex justify-end gap-3 pt-2">
          <button type="button" on:click={() => { showEditModal = false; }} disabled={editing}
            class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors cursor-pointer disabled:opacity-50">
            Cancelar
          </button>
          <button type="submit" disabled={editing || !editForm.nombre || !editForm.dni_cuit}
            class="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 disabled:bg-primary-400 rounded-lg transition-colors cursor-pointer disabled:cursor-not-allowed">
            {editing ? 'Guardando...' : 'Guardar cambios'}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

<!-- ═══════════════════════════════════════════════════════════ -->
<!-- DELETE CONFIRMATION                                         -->
<!-- ═══════════════════════════════════════════════════════════ -->
{#if showDeleteConfirm && deleteTarget}
  <div class="fixed inset-0 z-50 flex items-center justify-center">
    <div class="absolute inset-0 bg-black/50" on:click={() => { showDeleteConfirm = false; }} role="presentation"></div>
    <div class="relative bg-white dark:bg-gray-900 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 w-full max-w-md mx-4 p-6">
      <div class="flex items-center gap-3 mb-4">
        <div class="w-10 h-10 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
          <svg class="w-5 h-5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
        <div>
          <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100">Eliminar propietario</h3>
          <p class="text-sm text-gray-500 dark:text-gray-400">Esta acción no se puede deshacer</p>
        </div>
      </div>
      <p class="text-sm text-gray-700 dark:text-gray-300 mb-6">
        ¿Seguro que querés eliminar a <strong class="font-medium">{deleteTarget.nombre}</strong>?
      </p>
      <div class="flex justify-end gap-3">
        <button on:click={() => { showDeleteConfirm = false; }} disabled={deleting}
          class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors cursor-pointer disabled:opacity-50">
          Cancelar
        </button>
        <button on:click={submitDelete} disabled={deleting}
          class="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 disabled:bg-red-400 rounded-lg transition-colors cursor-pointer disabled:cursor-not-allowed">
          {deleting ? 'Eliminando...' : 'Eliminar'}
        </button>
      </div>
    </div>
  </div>
{/if}
