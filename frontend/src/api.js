/**
 * API service for communicating with the FastAPI backend.
 */

const API_BASE = 'http://localhost:8000/api';
const WS_URL = 'ws://localhost:8000/ws';

// ─── REST API ───────────────────────────────────

async function request(endpoint, options = {}) {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({ detail: res.statusText }));
    const error = new Error(typeof data.detail === 'string' ? data.detail : 'API Error');
    error.status = res.status;
    error.data = data;
    throw error;
  }
  return res.json();
}

export const api = {
  // Users
  createUser: (data) => request('/users', { method: 'POST', body: JSON.stringify(data) }),
  getUsers: () => request('/users'),
  getUser: (id) => request(`/users/${id}`),
  deleteUser: (id) => request(`/users/${id}`, { method: 'DELETE' }),

  // AI Analysis
  analyze: (data) => request('/analyze', { method: 'POST', body: JSON.stringify(data) }),

  // Jobs
  createJob: (data) => request('/jobs', { method: 'POST', body: JSON.stringify(data) }),
  getJobs: () => request('/jobs'),
  getJob: (id) => request(`/jobs/${id}`),
  stopJob: (id) => request(`/jobs/${id}`, { method: 'DELETE' }),
  getJobLogs: (id, limit = 50) => request(`/jobs/${id}/logs?limit=${limit}`),

  // Bookings
  getBookings: () => request('/bookings'),

  // Health
  health: () => request('/health'),
};

// ─── WebSocket ──────────────────────────────────

export class AgentWebSocket {
  constructor(onMessage, onConnect, onDisconnect) {
    this.onMessage = onMessage;
    this.onConnect = onConnect;
    this.onDisconnect = onDisconnect;
    this.ws = null;
    this.reconnectTimer = null;
  }

  connect() {
    try {
      this.ws = new WebSocket(WS_URL);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.onConnect?.();
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.onMessage?.(data);
        } catch (e) {
          console.warn('WS parse error:', e);
        }
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.onDisconnect?.();
        // Auto-reconnect after 3 seconds
        this.reconnectTimer = setTimeout(() => this.connect(), 3000);
      };

      this.ws.onerror = (err) => {
        console.warn('WebSocket error:', err);
      };
    } catch (e) {
      console.warn('WebSocket connect failed:', e);
      this.reconnectTimer = setTimeout(() => this.connect(), 3000);
    }
  }

  disconnect() {
    clearTimeout(this.reconnectTimer);
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}
