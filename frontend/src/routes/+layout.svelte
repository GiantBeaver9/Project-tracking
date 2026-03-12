<script>
  import '../app.css';
  import { isAuthenticated, logout } from '$lib/api/client.js';
  import NotificationBell from '$lib/components/NotificationBell.svelte';

  let { children } = $props();
  const authed = $derived(typeof window !== 'undefined' && isAuthenticated());
</script>

{#if authed}
  <nav class="topnav">
    <div class="nav-left">
      <a href="/dashboard" class="logo">Project Tracker</a>
      <a href="/dashboard">Dashboard</a>
      <a href="/projects">Projects</a>
      <a href="/timecard">Time Card</a>
      <a href="/approvals">Approvals</a>
      <a href="/reports">Reports</a>
      <a href="/admin">Admin</a>
    </div>
    <div class="nav-right">
      <NotificationBell count={0} />
      <button class="nav-btn" onclick={logout}>Logout</button>
    </div>
  </nav>
  <main class="app-main">
    {@render children()}
  </main>
{:else}
  {@render children()}
{/if}

<style>
  .topnav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--color-surface);
    border-bottom: 1px solid var(--color-border);
    padding: 0 1.5rem;
    height: 56px;
    box-shadow: var(--shadow-sm);
  }
  .nav-left {
    display: flex;
    align-items: center;
    gap: 1.5rem;
  }
  .nav-left a {
    text-decoration: none;
    color: var(--color-text-muted);
    font-size: 0.875rem;
    font-weight: 500;
  }
  .nav-left a:hover { color: var(--color-text); }
  .logo {
    font-weight: 700 !important;
    color: var(--color-primary) !important;
    font-size: 1rem !important;
    margin-right: 1rem;
  }
  .nav-right {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  .nav-btn {
    background: transparent;
    color: var(--color-text-muted);
    font-size: 0.875rem;
    padding: 0.375rem 0.75rem;
  }
  .nav-btn:hover { color: var(--color-text); }
  .app-main {
    max-width: 1400px;
    margin: 0 auto;
    padding: 1.5rem;
  }
</style>
