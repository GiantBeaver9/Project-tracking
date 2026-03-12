<script>
  let { count = 0 } = $props();
</script>

<button class="bell" aria-label="Notifications">
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
    <path d="M13.73 21a2 2 0 0 1-3.46 0" />
  </svg>
  {#if count > 0}
    <span class="badge">{count}</span>
  {/if}
</button>

<style>
  .bell {
    position: relative;
    background: transparent;
    padding: 0.5rem;
    color: var(--color-text-muted);
  }
  .bell:hover { color: var(--color-text); }
  .badge {
    position: absolute;
    top: 2px;
    right: 2px;
    background: var(--color-danger);
    color: white;
    font-size: 0.625rem;
    font-weight: 700;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }
</style>
