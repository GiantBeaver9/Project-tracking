import { goto } from '$app/navigation';
import { browser } from '$app/environment';

const API_BASE = '/api/v1';

function getToken() {
  if (!browser) return null;
  return localStorage.getItem('access_token');
}

function getHeaders() {
  const headers = { 'Content-Type': 'application/json' };
  const token = getToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

async function handleResponse(response) {
  if (response.status === 401) {
    if (browser) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      goto('/login');
    }
    throw new Error('Unauthorized');
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || 'Request failed');
  }

  return response.json();
}

export async function apiGet(path) {
  const response = await fetch(`${API_BASE}${path}`, { headers: getHeaders() });
  return handleResponse(response);
}

export async function apiPost(path, body) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(body),
  });
  return handleResponse(response);
}

export async function apiPatch(path, body) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'PATCH',
    headers: getHeaders(),
    body: JSON.stringify(body),
  });
  return handleResponse(response);
}

export async function login(username, password) {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Login failed' }));
    throw new Error(error.detail || 'Login failed');
  }

  const data = await response.json();
  if (browser) {
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
  }
  return data;
}

export function logout() {
  if (browser) {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }
  goto('/login');
}

export function isAuthenticated() {
  if (!browser) return false;
  return !!localStorage.getItem('access_token');
}
