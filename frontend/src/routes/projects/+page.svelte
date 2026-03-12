<script>
  import { onMount } from 'svelte';
  import { apiGet } from '$lib/api/client.js';
  import StatusBadge from '$lib/components/StatusBadge.svelte';
  import RAGBadge from '$lib/components/RAGBadge.svelte';

  let projects = $state([]);
  let loading = $state(true);
  let statusFilter = $state('');

  async function loadProjects() {
    loading = true;
    try {
      const params = statusFilter ? `?status=${statusFilter}` : '';
      projects = await apiGet(`/projects${params}`);
    } catch (err) {
      console.error('Failed to load projects', err);
    } finally {
      loading = false;
    }
  }

  onMount(loadProjects);
</script>

<div class="projects-page">
  <div class="header">
    <h1>Projects</h1>
    <div class="actions">
      <select bind:value={statusFilter} onchange={loadProjects}>
        <option value="">All Statuses</option>
        <option value="DRAFT">Draft</option>
        <option value="ACTIVE">Active</option>
        <option value="INACTIVE">Inactive</option>
        <option value="ARCHIVED">Archived</option>
      </select>
      <a href="/projects/new" class="btn-new">New Project</a>
    </div>
  </div>

  {#if loading}
    <p class="loading">Loading projects...</p>
  {:else if projects.length === 0}
    <p class="empty">No projects found.</p>
  {:else}
    <table class="project-table">
      <thead>
        <tr>
          <th>Health</th>
          <th>Code</th>
          <th>Name</th>
          <th>Status</th>
          <th>Type</th>
          <th>Start</th>
          <th>End</th>
          <th>Budget Hrs</th>
        </tr>
      </thead>
      <tbody>
        {#each projects as project}
          <tr>
            <td><RAGBadge health={project.health_status} /></td>
            <td class="code">{project.code}</td>
            <td><a href="/projects/{project.project_id}">{project.name}</a></td>
            <td><StatusBadge status={project.status} /></td>
            <td>{project.project_type}</td>
            <td>{project.start_date || '—'}</td>
            <td>{project.end_date || '—'}</td>
            <td>{project.budget_hours ?? '—'}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}
</div>

<style>
  .projects-page h1 { font-size: 1.5rem; }
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
  }
  .actions {
    display: flex;
    gap: 0.75rem;
    align-items: center;
  }
  .actions select { width: auto; }
  .btn-new {
    display: inline-block;
    background: var(--color-primary);
    color: white;
    padding: 0.625rem 1.25rem;
    border-radius: var(--radius);
    text-decoration: none;
    font-size: 0.875rem;
    font-weight: 500;
  }
  .btn-new:hover { background: var(--color-primary-hover); }
  .loading, .empty { color: var(--color-text-muted); }
  .project-table {
    width: 100%;
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius);
    border-collapse: collapse;
    font-size: 0.875rem;
  }
  .project-table th {
    text-align: left;
    padding: 0.75rem 1rem;
    background: var(--color-bg);
    border-bottom: 1px solid var(--color-border);
    font-weight: 600;
    color: var(--color-text-muted);
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  .project-table td {
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--color-border);
  }
  .project-table tr:last-child td { border-bottom: none; }
  .project-table a {
    color: var(--color-primary);
    text-decoration: none;
    font-weight: 500;
  }
  .project-table a:hover { text-decoration: underline; }
  .code { font-family: monospace; color: var(--color-text-muted); }
</style>
