<script>
  import { onMount } from 'svelte';
  import { apiGet } from '$lib/api/client.js';
  import StatusBadge from '$lib/components/StatusBadge.svelte';
  import RAGBadge from '$lib/components/RAGBadge.svelte';

  let user = $state(null);
  let projects = $state([]);
  let loading = $state(true);

  onMount(async () => {
    try {
      const results = await Promise.all([
        apiGet('/auth/me'),
        apiGet('/projects?status=ACTIVE'),
      ]);
      user = results[0];
      projects = results[1];
    } catch (err) {
      console.error('Failed to load dashboard data', err);
    } finally {
      loading = false;
    }
  });
</script>

<div class="dashboard">
  <h1>Dashboard</h1>

  {#if loading}
    <p class="loading">Loading...</p>
  {:else}
    {#if user}
      <p class="welcome">Welcome back, <strong>{user.display_name}</strong></p>
    {/if}

    <div class="grid">
      <div class="card">
        <h3>Active Projects</h3>
        <div class="stat">{projects.length}</div>
      </div>
      <div class="card">
        <h3>Pending Approvals</h3>
        <div class="stat">0</div>
      </div>
      <div class="card">
        <h3>Time Card Status</h3>
        <StatusBadge status="DRAFT" />
      </div>
    </div>

    {#if projects.length > 0}
      <h2>Active Projects</h2>
      <div class="project-list">
        {#each projects as project (project.project_id)}
          <div class="project-row">
            <RAGBadge health={project.health_status} />
            <a href="/projects/{project.project_id}">{project.name}</a>
            <span class="code">{project.code}</span>
            <StatusBadge status={project.status} />
          </div>
        {/each}
      </div>
    {/if}
  {/if}
</div>

<style>
  .dashboard h1 {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
  }
  .welcome {
    color: var(--color-text-muted);
    margin-bottom: 1.5rem;
  }
  .loading {
    color: var(--color-text-muted);
  }
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
  }
  .card {
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius);
    padding: 1.25rem;
    box-shadow: var(--shadow-sm);
  }
  .card h3 {
    font-size: 0.875rem;
    color: var(--color-text-muted);
    margin-bottom: 0.5rem;
  }
  .stat {
    font-size: 2rem;
    font-weight: 700;
  }
  h2 {
    font-size: 1.125rem;
    margin-bottom: 0.75rem;
  }
  .project-list {
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius);
    overflow: hidden;
  }
  .project-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--color-border);
  }
  .project-row:last-child { border-bottom: none; }
  .project-row a {
    text-decoration: none;
    color: var(--color-primary);
    font-weight: 500;
    flex: 1;
  }
  .project-row a:hover { text-decoration: underline; }
  .code {
    color: var(--color-text-muted);
    font-size: 0.75rem;
    font-family: monospace;
  }
</style>
