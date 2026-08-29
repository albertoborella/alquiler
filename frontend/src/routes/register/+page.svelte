<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { auth } from '$lib/stores/auth';
  import { api } from '$lib/api';

  let fullName = '';
  let email = '';
  let password = '';
  let confirmPassword = '';
  let error = '';
  let loading = false;

  onMount(() => {
    if ($auth.token) goto('/inmuebles');
  });

  async function handleSubmit(e: Event) {
    e.preventDefault();
    error = '';

    if (password !== confirmPassword) {
      error = 'Las contraseñas no coinciden';
      return;
    }

    if (password.length < 6) {
      error = 'La contraseña debe tener al menos 6 caracteres';
      return;
    }

    loading = true;

    try {
      const res = await api.login({ email, password: 'temp' });
      await api.createUser(res.access_token, {
        email,
        password,
        full_name: fullName || undefined,
        role: 'empleado',
      });
      goto('/login');
    } catch (err) {
      error = err instanceof Error ? err.message : 'Error al registrarse';
    } finally {
      loading = false;
    }
  }
</script>

<div class="min-h-screen flex items-center justify-center px-4 py-12">
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
          d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"
        />
      </svg>
      <h1 class="text-2xl font-bold text-gray-900">Crear Cuenta</h1>
      <p class="text-gray-500 mt-1">Registrate para empezar</p>
    </div>

    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-8">
      <form on:submit={handleSubmit} class="space-y-5">
        {#if error}
          <div class="bg-red-50 text-red-700 text-sm rounded-lg px-4 py-3 border border-red-100">
            {error}
          </div>
        {/if}

        <div>
          <label for="fullName" class="block text-sm font-medium text-gray-700 mb-1.5">
            Nombre completo
          </label>
          <input
            id="fullName"
            type="text"
            bind:value={fullName}
            class="w-full px-4 py-2.5 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition"
            placeholder="Juan Pérez"
          />
        </div>

        <div>
          <label for="email" class="block text-sm font-medium text-gray-700 mb-1.5">
            Email
          </label>
          <input
            id="email"
            type="email"
            bind:value={email}
            required
            class="w-full px-4 py-2.5 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition"
            placeholder="tu@email.com"
          />
        </div>

        <div>
          <label for="password" class="block text-sm font-medium text-gray-700 mb-1.5">
            Contraseña
          </label>
          <input
            id="password"
            type="password"
            bind:value={password}
            required
            class="w-full px-4 py-2.5 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition"
            placeholder="••••••••"
          />
        </div>

        <div>
          <label for="confirmPassword" class="block text-sm font-medium text-gray-700 mb-1.5">
            Confirmar contraseña
          </label>
          <input
            id="confirmPassword"
            type="password"
            bind:value={confirmPassword}
            required
            class="w-full px-4 py-2.5 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition"
            placeholder="••••••�•••"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          class="w-full bg-primary-600 hover:bg-primary-700 disabled:bg-primary-400 text-white py-2.5 rounded-lg text-sm font-medium transition-colors cursor-pointer disabled:cursor-not-allowed"
        >
          {loading ? 'Creando cuenta...' : 'Registrarse'}
        </button>
      </form>
    </div>

    <p class="text-center text-sm text-gray-500 mt-6">
      ¿Ya tenés cuenta?
      <a href="/login" class="text-primary-600 hover:text-primary-700 font-medium">
        Iniciá sesión
      </a>
    </p>
  </div>
</div>
