<script>
  import { onMount } from 'svelte';
  import { isAuthenticated } from '$lib/api/client.js';
  import { goto } from '$app/navigation';

  onMount(() => {
    if (isAuthenticated()) {
      goto('/dashboard');
    } else {
      goto('/login');
    }
  });
</script>
