const API_BASE = 'https://fitflow-api-production-c25a.up.railway.app/api';

function getToken() { return localStorage.getItem('fitflow_token'); }
function getUser() { try { return JSON.parse(localStorage.getItem('fitflow_user')); } catch { return null; } }
function setAuth(token, user) {
  localStorage.setItem('fitflow_token', token);
  localStorage.setItem('fitflow_user', JSON.stringify(user));
}
function clearAuth() {
  localStorage.removeItem('fitflow_token');
  localStorage.removeItem('fitflow_user');
}

async function login(username, password) {
  const r = await fetch(`${API_BASE}/auth/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  const data = await r.json();
  if (data.token) setAuth(data.token, data.user);
  return data;
}

async function register(payload) {
  const r = await fetch(`${API_BASE}/auth/register/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  const data = await r.json();
  if (data.token) setAuth(data.token, data.user);
  return data;
}

function logout() {
  clearAuth();
  location.href = 'login.html';
}

async function authFetch(path, options = {}) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (token) headers['Authorization'] = `Token ${token}`;
  const r = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (r.status === 401) { clearAuth(); location.href = 'login.html'; return null; }
  return r;
}

async function getWorkouts() {
  const r = await authFetch('/workouts/workouts/');
  if (!r || !r.ok) return [];
  const d = await r.json();
  return d.results || d || [];
}

async function getDashboard() {
  const r = await authFetch('/progress/dashboard/');
  if (!r || !r.ok) return {};
  return r.json();
}

async function logWeight(weight_kg) {
  const r = await authFetch('/progress/weight/', {
    method: 'POST',
    body: JSON.stringify({ weight_kg, date: new Date().toISOString().split('T')[0] })
  });
  if (!r) return null;
  return r.json();
}

async function getPRs() {
  const r = await authFetch('/progress/prs/');
  if (!r || !r.ok) return [];
  const d = await r.json();
  return d.results || d || [];
}

async function getProfile() {
  const r = await authFetch('/auth/profile/');
  if (!r || !r.ok) return null;
  return r.json();
}

async function getExercises() {
  const r = await authFetch('/workouts/exercises/');
  if (!r || !r.ok) return [];
  const d = await r.json();
  return d.results || d || [];
}
