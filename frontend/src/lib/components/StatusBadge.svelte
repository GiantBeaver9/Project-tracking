<script>
  let { status = '', variant = 'default' } = $props();

  const colorMap = {
    ACTIVE: 'badge-green',
    GREEN: 'badge-green',
    COMPLETE: 'badge-green',
    APPROVED: 'badge-green',
    DRAFT: 'badge-gray',
    PENDING: 'badge-gray',
    TODO: 'badge-gray',
    INACTIVE: 'badge-amber',
    AMBER: 'badge-amber',
    IN_PROGRESS: 'badge-blue',
    SUBMITTED: 'badge-blue',
    IN_REVIEW: 'badge-blue',
    RED: 'badge-red',
    REJECTED: 'badge-red',
    MISSED: 'badge-red',
    ARCHIVED: 'badge-muted',
    CANCELLED: 'badge-muted',
  };

  const badgeClass = $derived(colorMap[status] || 'badge-gray');
</script>

<span class="badge {badgeClass}">{status}</span>

<style>
  .badge {
    display: inline-block;
    padding: 0.125rem 0.5rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.025em;
  }
  .badge-green { background: #dcfce7; color: #166534; }
  .badge-gray { background: #f1f5f9; color: #475569; }
  .badge-amber { background: #fef3c7; color: #92400e; }
  .badge-blue { background: #dbeafe; color: #1e40af; }
  .badge-red { background: #fee2e2; color: #991b1b; }
  .badge-muted { background: #e2e8f0; color: #64748b; }
</style>
