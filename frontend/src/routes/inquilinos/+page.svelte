<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { auth } from '$lib/stores/auth';
  import { api } from '$lib/api';
  import type { InquilinoPublic } from '$lib/api';

  let inquilinos: InquilinoPublic[] = [];
  let loading = true;
  let error = '';

  // ── Create/Edit modal ──
  let showModal = false;
  let editTarget: InquilinoPublic | null = null;
  let form = {
    nombre: '',
    dni: '',
    telefono: '',
    email: '',
    direccion: '',
  };
  let submitting = false;
  let success = '';
  let formError = '';

  // ── Delete modal ──
  let showDeleteConfirm = false;
  let deleteTarget: InquilinoPublic | null = null;
  let deleting = false;

  $: isAdmin = $auth.user?.role === 'admin';

  onMount(() => {
    if (!$auth.token) {
      goto('/login');
      return;
    }
    loadInquilinos();
  });

  async function loadInquilinos() {
    if (!$auth.token) return;
    loading = true;
    error = '';
    try {
      inquilinos = await api.getInquilinos($auth.token);
    } catch (err) {
      error = err instanceof Error ? err.message : 'Error al cargar inquilinos';
    } finally {
      loading = false;
    }
  }

  // ── Create / Edit ──
  function openCreate() {
    editTarget = null;
    form = { nombre: '', dni: '', telefono: '', email: '', direccion: '' };
    success = '';
    formError = '';
    showModal = true;
  }

  function openEdit(inq: InquilinoPublic) {
    editTarget = inq;
    form = {
      nombre: inq.nombre,
      dni: inq.dni,
      telefono: inq.telefono ?? '',
      email: inq.email ?? '',
      direccion: inq.direccion ?? '',
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
        await api.updateInquilino($auth.token, editTarget.id, {
          nombre: form.nombre,
          dni: form.dni,
          telefono: form.telefono || undefined,
          email: form.email || undefined,
          direccion: form.direccion || undefined,
        });
        success = 'Inquilino actualizado';
      } else {
        await api.createInquilino($auth.token, {
          nombre: form.nombre,
          dni: form.dni,
          telefono: form.telefono || undefined,
          email: form.email || undefined,
          direccion: form.direccion || undefined,
        });
        success = 'Inquilino creado';
      }
      await loadInquilinos();
      setTimeout(() => {
        showModal = false;
        editTarget = null;
      }, 1200);
    } catch (err) {
      formError = err instanceof Error ? err.message : 'Error al guardar inquilino';
    } finally {
      submitting = false;
    }
  }

  // ── Delete ──
  function confirmDelete(inq: InquilinoPublic) {
    deleteTarget = inq;
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
      await api.deleteInquilino($auth.token, deleteTarget.id);
      inquilinos = inquilinos.filter((i) => i.id !== deleteTarget!.id);
      showDeleteConfirm = false;
      deleteTarget = null;
    } catch (err) {
      error = err instanceof Error ? err.message : 'Error al eliminar inquilino';
      showDeleteConfirm = false;
    } finally {
      deleting = false;
    }
  }
</script>

<div class="max-w-7xl mx-auto px-4 md:px-6 lg:px-8 py-6 md:py-8">
  <div class="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800">
    <!-- Header bar -->
    <div class="px-4 md:px-6 py-3 border-b border-gray-100 dark:border-gray-800">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 class="text-xl font-bold text-gray-900 dark:text-gray-100">Inquilinos</h1>
          <p class="text-gray-500 dark:text-gray-400 mt-0.5 text-sm">Gestion de inquilinos</p>
        </div>
        {#if isAdmin}
          <button
            on:click={openCreate}
            class="inline-flex items-center gap-2 px-3.5 py-1.5 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 active:bg-primary-800 rounded-lg shadow-sm transition-colors cursor-pointer"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Nuevo inquilino
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
        {#each Array(4) as _}
          <div class="flex gap-4 animate-pulse">
            <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/4"></div>
            <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/6"></div>
            <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/6"></div>
          </div>
        {/each}
      </div>
    {:else if inquilinos.length === 0}
      <div class="px-6 py-16 text-center">
        <div class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg px-6 py-5 max-w-md mx-auto mb-6">
          <div class="flex items-center gap-3">
            <svg class="w-5 h-5 text-amber-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <p class="text-sm text-amber-700 dark:text-amber-300 font-medium">No hay inquilinos cargados</p>
          </div>
          <p class="text-xs text-amber-600 dark:text-amber-400 mt-2">
            Cargue los primeros inquilinos para poder generar contratos.
          </p>
        </div>
        <svg class="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 4.354a4 4 0 110 7.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
        <p class="text-gray-500 dark:text-gray-400 text-sm">No se encontraron inquilinos</p>
      </div>
    {:else}
      <div class="overflow-x-auto -mx-4 md:mx-0">
        <table class="w-full min-w-[600px]">
          <thead>
            <tr class="text-left text-[11px] font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider border-b border-gray-100 dark:border-gray-800">
              <th class="px-4 md:px-5 py-2">Nombre</th>
              <th class="px-4 md:px-5 py-2">DNI</th>
              <th class="px-4 md:px-5 py-2 hidden sm:table-cell">Telefono</th>
              <th class="px-4 md:px-5 py-2 hidden md:table-cell">Email</th>
              <th class="px-4 md:px-5 py-2 text-right">Acciones</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50 dark:divide-gray-800">
            {#each inquilinos as inq (inq.id)}
              <tr class="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                <td class="px-4 md:px-5 py-2">
                  <div class="text-[13px] font-medium text-gray-900 dark:text-gray-100">{inq.nombre}</div>
                  <div class="text-[11px] text-gray-400 dark:text-gray-500 mt-0.5 sm:hidden">{inq.dni}</div>
                </td>
                <td class="px-4 md:px-5 py-2 text-[13px] text-gray-600 dark:text-gray-400">{inq.dni}</td>
                <td class="px-4 md:px-5 py-2 text-[13px] text-gray-600 dark:text-gray-400 hidden sm:table-cell">{inq.telefono ?? '-'}</td>
                <td class="px-4 md:px-5 py-2 text-[13px] text-gray-600 dark:text-gray-400 hidden md:table-cell">{inq.email ?? '-'}</td>
                <td class="px-4 md:px-5 py-2 text-right">
                  {#if isAdmin}
                    <div class="flex items-center justify-end gap-0.5">
                      <button
                        on:click={() => openEdit(inq)}
                        class="p-1.5 rounded-md text-gray-400 hover:text-violet-600 hover:bg-violet-50 dark:hover:bg-violet-900/20 transition-colors cursor-pointer"
                        title="Editar inquilino"
                      >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </button>
                      <button
                        on:click={() => confirmDelete(inq)}
                        class="p-1.5 rounded-md text-gray-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors cursor-pointer"
                        title="Eliminar inquilino"
                      >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  {/if}
                </td>
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
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 7.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
        </div>
        <div>
          <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100">{editTarget ? 'Editar inquilino' : 'Nuevo inquilino'}</h3>
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
        <div>
          <label for="inq-nombre" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Nombre *</label>
          <input id="inq-nombre" type="text" bind:value={form.nombre} required placeholder="Nombre completo"
            class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="inq-dni" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">DNI *</label>
            <input id="inq-dni" type="text" bind:value={form.dni} required placeholder="DNI"
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
          </div>
          <div>
            <label for="inq-telefono" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Telefono</label>
            <input id="inq-telefono" type="text" bind:value={form.telefono} placeholder="Telefono"
              class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
          </div>
        </div>

        <div>
          <label for="inq-email" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Email</label>
          <input id="inq-email" type="email" bind:value={form.email} placeholder="email@ejemplo.com"
            class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
        </div>

        <div>
          <label for="inq-direccion" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Direccion</label>
          <input id="inq-direccion" type="text" bind:value={form.direccion} placeholder="Direccion personal"
            class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent" />
        </div>

        <div class="flex justify-end gap-3 pt-2">
          <button type="button" on:click={cancelModal} disabled={submitting}
            class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors cursor-pointer disabled:opacity-50">
            Cancelar
          </button>
          <button type="submit" disabled={submitting || !form.nombre || !form.dni}
            class="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 disabled:bg-primary-400 rounded-lg transition-colors cursor-pointer disabled:cursor-not-allowed">
            {submitting ? 'Guardando...' : editTarget ? 'Actualizar' : 'Crear inquilino'}
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
          <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100">Eliminar inquilino</h3>
          <p class="text-sm text-gray-500 dark:text-gray-400">Esta accion no se puede deshacer</p>
        </div>
      </div>
      <p class="text-sm text-gray-700 dark:text-gray-300 mb-6">
        Seguro que queres eliminar a <strong class="font-medium">{deleteTarget.nombre}</strong> (DNI: {deleteTarget.dni})?
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
