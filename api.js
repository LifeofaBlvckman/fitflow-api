// Use your live Render URL
const API_BASE = 'https://fitflow-api-k10o.onrender.com/api';

// Rest of your api.js code - keep all functions exactly the same
async function login(username, password) {
    try {
        const response = await fetch(`${API_BASE}/auth/login/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const data = await response.json();
        if (response.ok && data.token) {
            localStorage.setItem('fitflow_token', data.token);
            if (data.user) {
                localStorage.setItem('fitflow_user', JSON.stringify(data.user));
            }
            return data;
        }
        throw new Error(data.message || 'Login failed');
    } catch (error) {
        console.error('Login error:', error);
        throw error;
    }
}

async function register(userData) {
    try {
        const response = await fetch(`${API_BASE}/auth/register/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        });
        const data = await response.json();
        if (response.ok && data.token) {
            localStorage.setItem('fitflow_token', data.token);
            if (data.user) {
                localStorage.setItem('fitflow_user', JSON.stringify(data.user));
            }
            return data;
        }
        throw new Error(data.message || 'Registration failed');
    } catch (error) {
        console.error('Register error:', error);
        throw error;
    }
}

function getToken() {
    return localStorage.getItem('fitflow_token');
}

function getUser() {
    const userStr = localStorage.getItem('fitflow_user');
    return userStr ? JSON.parse(userStr) : null;
}

async function fetchDashboard() {
    const token = getToken();
    if (!token) throw new Error('Not authenticated');
    const response = await fetch(`${API_BASE}/progress/dashboard/`, {
        headers: { 'Authorization': `Token ${token}` }
    });
    return response.json();
}

async function fetchWorkouts() {
    const token = getToken();
    if (!token) throw new Error('Not authenticated');
    const response = await fetch(`${API_BASE}/workouts/workouts/`, {
        headers: { 'Authorization': `Token ${token}` }
    });
    return response.json();
}

async function createWorkout(workoutData) {
    const token = getToken();
    const response = await fetch(`${API_BASE}/workouts/workouts/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Token ${token}`
        },
        body: JSON.stringify(workoutData)
    });
    return response.json();
}

async function addSet(workoutId, setData) {
    const token = getToken();
    const response = await fetch(`${API_BASE}/workouts/workouts/${workoutId}/add_set/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Token ${token}`
        },
        body: JSON.stringify(setData)
    });
    return response.json();
}

async function fetchExercises(params = {}) {
    let url = `${API_BASE}/workouts/exercises/`;
    const queryParams = new URLSearchParams(params).toString();
    if (queryParams) url += '?' + queryParams;
    const response = await fetch(url);
    return response.json();
}

async function fetchWeightEntries() {
    const token = getToken();
    const response = await fetch(`${API_BASE}/progress/weight/`, {
        headers: { 'Authorization': `Token ${token}` }
    });
    return response.json();
}

async function fetchPersonalRecords() {
    const token = getToken();
    const response = await fetch(`${API_BASE}/progress/prs/`, {
        headers: { 'Authorization': `Token ${token}` }
    });
    return response.json();
}
