<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { auth } from '$lib/stores/auth';

  onMount(() => {
    if ($auth.token) {
      goto('/inmuebles');
    } else {
      goto('/login');
    }
  });
</script>
