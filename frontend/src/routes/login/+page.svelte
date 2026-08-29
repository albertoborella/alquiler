<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { auth } from '$lib/stores/auth';
  import { api } from '$lib/api';

  let email = '';
  let password = '';
  let error = '';
  let loading = false;

  onMount(() => {
    if ($auth.token) goto('/inmuebles');
  });

  async function handleSubmit(e: Event) {
    e.preventDefault();
    error = '';
    loading = true;

    try {
      const res = await api.login({ email, password });
      const user = await api.getMe(res.access_token);
      auth.login(res.access_token, {
        id: user.id,
        email: user.email,
        full_name: user.full_name,
        role: user.role,
      });
      goto('/inmuebles');
    } catch (err) {
      error = err instanceof Error ? err.message : 'Error al iniciar sesión';
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
          d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
        />
      </svg>
      <h1 class="text-2xl font-bold text-gray-900">Alquiler App</h1>
      <p class="text-gray-500 mt-1">Ingresá a tu cuenta</p>
    </div>

    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-8">
      <form on:submit={handleSubmit} class="space-y-5">
        {#if error}
          <div class="bg-red-50 text-red-700 text-sm rounded-lg px-4 py-3 border border-red-100">
            {error}
          </div>
        {/if}

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

        <div class="text-right">
          <a href="#" class="text-sm text-primary-600 hover:text-primary-700">
            ¿Olvidaste tu contraseña?
          </a>
        </div>

        <button
          type="submit"
          disabled={loading}
          class="w-full bg-primary-600 hover:bg-primary-700 disabled:bg-primary-400 text-white py-2.5 rounded-lg text-sm font-medium transition-colors cursor-pointer disabled:cursor-not-allowed"
        >
          {loading ? 'Ingresando...' : 'Iniciar Sesión'}
        </button>
      </form>
    </div>

    <p class="text-center text-sm text-gray-500 mt-6">
      ¿No tenés cuenta?
      <a href="/register" class="text-primary-600 hover:text-primary-700 font-medium">
        Registrate
      </a>
    </p>
  </div>
</div>
