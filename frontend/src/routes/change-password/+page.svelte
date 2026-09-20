<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { auth } from '$lib/stores/auth';
  import { api } from '$lib/api';

  let currentPassword = '';
  let newPassword = '';
  let confirmPassword = '';
  let error = '';
  let success = '';
  let loading = false;

  onMount(() => {
    if (!$auth.token) goto('/login');
  });

  async function handleSubmit(e: Event) {
    e.preventDefault();
    error = '';
    success = '';

    if (newPassword !== confirmPassword) {
      error = 'Las contraseñas nuevas no coinciden';
      return;
    }

    if (newPassword.length < 6) {
      error = 'La contraseña nueva debe tener al menos 6 caracteres';
      return;
    }

    loading = true;

    try {
      await api.changePassword($auth.token!, {
        current_password: currentPassword,
        new_password: newPassword,
      });
      success = 'Contraseña actualizada correctamente';
      currentPassword = '';
      newPassword = '';
      confirmPassword = '';
    } catch (err) {
      error = err instanceof Error ? err.message : 'Error al cambiar contraseña';
    } finally {
      loading = false;
    }
  }
</script>

<div class="min-h-screen flex items-start justify-center px-4 pt-20 pb-12">
  <div class="w-full max-w-md">
    <div class="text-center mb-8">
      <svg
        class="w-12 h-12 text-primary-600 mx-auto mb-4"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"
        />
      </svg>
      <h1 class="text-2xl font-bold text-gray-900">Cambiar Contraseña</h1>
      <p class="text-gray-500 mt-1">Actualizá tu contraseña de acceso</p>
    </div>

    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-8">
      <form on:submit={handleSubmit} class="space-y-5">
        {#if error}
          <div class="bg-red-50 text-red-700 text-sm rounded-lg px-4 py-3 border border-red-100">
            {error}
          </div>
        {/if}

        {#if success}
          <div class="bg-emerald-50 text-emerald-700 text-sm rounded-lg px-4 py-3 border border-emerald-100">
            {success}
          </div>
        {/if}

        <div>
          <label for="current-password" class="block text-sm font-medium text-gray-700 mb-1.5">
            Contraseña actual
          </label>
          <input
            id="current-password"
            type="password"
            bind:value={currentPassword}
            required
            class="w-full px-4 py-2.5 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition"
            placeholder="••••••••"
          />
        </div>

        <div>
          <label for="new-password" class="block text-sm font-medium text-gray-700 mb-1.5">
            Contraseña nueva
          </label>
          <input
            id="new-password"
            type="password"
            bind:value={newPassword}
            required
            minlength="6"
            class="w-full px-4 py-2.5 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition"
            placeholder="••••••••"
          />
        </div>

        <div>
          <label for="confirm-password" class="block text-sm font-medium text-gray-700 mb-1.5">
            Confirmar contraseña nueva
          </label>
          <input
            id="confirm-password"
            type="password"
            bind:value={confirmPassword}
            required
            minlength="6"
            class="w-full px-4 py-2.5 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition"
            placeholder="••••••••"
          />
        </div>

        <div class="flex gap-3">
          <a
            href="/login"
            class="flex-1 text-center py-2.5 rounded-lg text-sm font-medium border border-gray-300 text-gray-700 hover:bg-gray-50 transition-colors"
          >
            Volver
          </a>
          <button
            type="submit"
            disabled={loading}
            class="flex-1 bg-primary-600 hover:bg-primary-700 disabled:bg-primary-400 text-white py-2.5 rounded-lg text-sm font-medium transition-colors cursor-pointer disabled:cursor-not-allowed"
          >
            {loading ? 'Guardando...' : 'Guardar'}
          </button>
        </div>
      </form>
    </div>
  </div>
</div>
