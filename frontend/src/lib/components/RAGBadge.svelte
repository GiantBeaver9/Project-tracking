<script>
  let { health = 'GREEN' } = $props();
</script>

<span class="rag rag-{health.toLowerCase()}" title="Health: {health}"></span>

<style>
  .rag {
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
  }
  .rag-green { background: #16a34a; }
  .rag-amber { background: #d97706; }
  .rag-red { background: #dc2626; }
</style>
