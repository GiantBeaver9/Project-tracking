<script>
  import { login } from '$lib/api/client.js';
  import { goto } from '$app/navigation';

  let username = $state('');
  let password = $state('');
  let error = $state('');
  let loading = $state(false);

  async function handleSubmit(e) {
    e.preventDefault();
    error = '';
    loading = true;

    try {
      await login(username, password);
      goto('/dashboard');
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }
</script>

<div class="login-page">
  <div class="login-card">
    <h1>Project Tracker</h1>
    <p class="subtitle">Sign in to your account</p>

    <form onsubmit={handleSubmit}>
      {#if error}
        <div class="error-msg">{error}</div>
      {/if}

      <div class="field">
        <label for="username">Username</label>
        <input
          id="username"
          type="text"
          bind:value={username}
          placeholder="Enter your username"
          required
          autocomplete="username"
        />
      </div>

      <div class="field">
        <label for="password">Password</label>
        <input
          id="password"
          type="password"
          bind:value={password}
          placeholder="Enter your password"
          required
          autocomplete="current-password"
        />
      </div>

      <button type="submit" class="primary login-btn" disabled={loading}>
        {loading ? 'Signing in...' : 'Sign In'}
      </button>
    </form>

    <div class="sso-divider">
      <span>or</span>
    </div>

    <button class="sso-btn" disabled>
      Sign in with SSO
    </button>
  </div>
</div>

<style>
  .login-page {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    background: var(--color-bg);
  }
  .login-card {
    background: var(--color-surface);
    padding: 2.5rem;
    border-radius: 12px;
    box-shadow: var(--shadow-md);
    width: 100%;
    max-width: 400px;
  }
  h1 {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--color-primary);
    text-align: center;
  }
  .subtitle {
    text-align: center;
    color: var(--color-text-muted);
    font-size: 0.875rem;
    margin: 0.5rem 0 1.5rem;
  }
  .field {
    margin-bottom: 1rem;
  }
  .login-btn {
    width: 100%;
    margin-top: 0.5rem;
    padding: 0.75rem;
    font-size: 1rem;
  }
  .login-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  .error-msg {
    background: #fee2e2;
    color: #991b1b;
    padding: 0.625rem 0.75rem;
    border-radius: var(--radius);
    font-size: 0.875rem;
    margin-bottom: 1rem;
  }
  .sso-divider {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin: 1.5rem 0;
    color: var(--color-text-muted);
    font-size: 0.75rem;
  }
  .sso-divider::before,
  .sso-divider::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--color-border);
  }
  .sso-btn {
    width: 100%;
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    color: var(--color-text);
    padding: 0.75rem;
    font-size: 0.875rem;
  }
  .sso-btn:hover:not(:disabled) {
    background: var(--color-bg);
  }
  .sso-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
</style>
