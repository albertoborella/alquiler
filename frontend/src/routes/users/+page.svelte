<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { auth } from '$lib/stores/auth';
  import { api } from '$lib/api';

  type User = {
    id: string;
    email: string;
    full_name: string | null;
    role: string;
    is_active: boolean;
    created_at: string | null;
  };

  let users: User[] = [];
  let loading = true;
  let error = '';
  let roleFilter = '';

  // Delete modal
  let showDeleteConfirm = false;
  let deleteTarget: User | null = null;
  let deleting = false;

  $: isAdmin = $auth.user?.role === 'admin';

  onMount(() => {
    if (!$auth.token) {
      goto('/login');
      return;
    }
    loadUsers();
  });

  async function loadUsers() {
    if (!$auth.token) return;
    loading = true;
    error = '';
    try {
      users = await api.getUsers($auth.token, roleFilter || undefined);
    } catch (err) {
      error = err instanceof Error ? err.message : 'Error al cargar usuarios';
    } finally {
      loading = false;
    }
  }

  function handleFilterChange() {
    loadUsers();
  }

  function confirmDeleteUser(user: User) {
    deleteTarget = user;
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
      await api.deleteUser($auth.token, deleteTarget.id);
      users = users.filter((u) => u.id !== deleteTarget!.id);
      showDeleteConfirm = false;
      deleteTarget = null;
    } catch (err) {
      error = err instanceof Error ? err.message : 'Error al eliminar usuario';
      showDeleteConfirm = false;
    } finally {
      deleting = false;
    }
  }

  function formatDate(dateStr: string | null): string {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('es-AR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  }

  function getRoleBadgeClass(role: string): string {
    return role === 'admin'
      ? 'bg-primary-100 dark:bg-primary-900/40 text-primary-800 dark:text-primary-200'
      : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300';
  }

  function getRoleLabel(role: string): string {
    return role === 'admin' ? 'Admin' : 'Empleado';
  }
</script>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
  <div class="mb-8">
    <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">Usuarios</h1>
    <p class="text-gray-500 dark:text-gray-400 mt-1">Gestión de usuarios del sistema</p>
  </div>

  <div class="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800">
    <div class="px-6 py-3 border-b border-gray-100 dark:border-gray-800">
      <div class="flex items-center gap-4">
        <label for="roleFilter" class="text-sm font-medium text-gray-700 dark:text-gray-300">
          Filtrar por rol:
        </label>
        <select
          id="roleFilter"
          bind:value={roleFilter}
          on:change={handleFilterChange}
          class="px-3 py-1.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        >
          <option value="">Todos</option>
          <option value="admin">Admin</option>
          <option value="empleado">Empleado</option>
        </select>
      </div>
    </div>

    {#if error}
      <div class="px-6 py-3 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 text-sm border-b border-red-100 dark:border-red-900/30">
        {error}
      </div>
    {/if}

    {#if loading}
      <div class="p-6 space-y-3">
        {#each Array(5) as _}
          <div class="flex gap-4 animate-pulse">
            <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/4"></div>
            <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/4"></div>
            <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/6"></div>
            <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/6"></div>
            <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/6"></div>
          </div>
        {/each}
      </div>
    {:else if users.length === 0}
      <!-- Empty state with alert -->
      <div class="px-6 py-16 text-center">
        <div class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg px-6 py-5 max-w-md mx-auto mb-6">
          <div class="flex items-center gap-3">
            <svg class="w-5 h-5 text-amber-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <p class="text-sm text-amber-700 dark:text-amber-300 font-medium">No hay usuarios cargados</p>
          </div>
          <p class="text-xs text-amber-600 dark:text-amber-400 mt-2">
            Registrá los primeros usuarios para empezar a gestionar el sistema.
          </p>
        </div>
        <svg class="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        <p class="text-gray-500 dark:text-gray-400 text-sm">No se encontraron usuarios</p>
      </div>
    {:else}
      <div class="overflow-x-auto -mx-4 md:mx-0">
        <table class="w-full min-w-[520px]">
          <thead>
            <tr class="text-left text-[11px] font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider border-b border-gray-100 dark:border-gray-800">
              <th class="px-3 md:px-4 py-1">Nombre</th>
              <th class="px-3 md:px-4 py-1 hidden sm:table-cell">Email</th>
              <th class="px-3 md:px-4 py-1">Rol</th>
              <th class="px-3 md:px-4 py-1">Estado</th>
              <th class="px-3 md:px-4 py-1 hidden md:table-cell">Fecha creación</th>
              {#if isAdmin}
                <th class="px-3 md:px-4 py-1 text-right">Acciones</th>
              {/if}
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50 dark:divide-gray-800">
            {#each users as user (user.id)}
              <tr class="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                <td class="px-3 py-1 text-xs font-medium text-gray-900 dark:text-gray-100">
                  {user.full_name || '-'}
                </td>
                <td class="px-3 py-1 text-xs text-gray-600 dark:text-gray-400">
                  {user.email}
                </td>
                <td class="px-3 py-1">
                  <span
                    class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium {getRoleBadgeClass(
                      user.role
                    )}"
                  >
                    {getRoleLabel(user.role)}
                  </span>
                </td>
                <td class="px-3 py-1">
                  <div class="flex items-center gap-2">
                    <div
                      class="w-1.5 h-1.5 rounded-full {user.is_active
                        ? 'bg-green-500'
                        : 'bg-red-500'}"
                    ></div>
                    <span class="text-xs text-gray-600 dark:text-gray-400">
                      {user.is_active ? 'Activo' : 'Inactivo'}
                    </span>
                  </div>
                </td>
                <td class="px-3 py-1 text-xs text-gray-500 dark:text-gray-400">
                  {formatDate(user.created_at)}
                </td>
                {#if isAdmin}
                  <td class="px-3 py-1 text-right">
                    <div class="flex items-center justify-end gap-1">
                      <!-- Edit icon -->
                      <a
                        href="/users/{user.id}/editar"
                        class="p-1.5 rounded-md text-gray-400 hover:text-primary-600 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-colors"
                        title="Editar usuario"
                      >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </a>
                      <!-- Delete icon -->
                      <button
                        on:click={() => confirmDeleteUser(user)}
                        class="p-1.5 rounded-md text-gray-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors cursor-pointer"
                        title="Eliminar usuario"
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

<!-- Delete confirmation modal -->
{#if showDeleteConfirm && deleteTarget}
  <div class="fixed inset-0 z-50 flex items-center justify-center">
    <!-- Backdrop -->
    <div class="absolute inset-0 bg-black/50" on:click={cancelDelete} role="presentation"></div>

    <!-- Modal -->
    <div class="relative bg-white dark:bg-gray-900 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 w-full max-w-md mx-4 p-6">
      <div class="flex items-center gap-3 mb-4">
        <div class="w-10 h-10 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
          <svg class="w-5 h-5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
        <div>
          <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100">Eliminar usuario</h3>
          <p class="text-sm text-gray-500 dark:text-gray-400">Esta acción no se puede deshacer</p>
        </div>
      </div>

      <p class="text-sm text-gray-700 dark:text-gray-300 mb-6">
        ¿Seguro que querés eliminar al usuario <strong class="font-medium">{deleteTarget.full_name || deleteTarget.email}</strong>?
      </p>

      <div class="flex justify-end gap-3">
        <button
          on:click={cancelDelete}
          disabled={deleting}
          class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors cursor-pointer disabled:opacity-50"
        >
          Cancelar
        </button>
        <button
          on:click={executeDelete}
          disabled={deleting}
          class="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 disabled:bg-red-400 rounded-lg transition-colors cursor-pointer disabled:cursor-not-allowed"
        >
          {deleting ? 'Eliminando...' : 'Eliminar'}
        </button>
      </div>
    </div>
  </div>
{/if}
