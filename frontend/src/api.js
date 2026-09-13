const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function request(path, options = {}) {
  let response
  try {
    response = await fetch(`${API_BASE}${path}`, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options,
    })
  } catch {
    throw new Error(`Unable to reach the sales API at ${API_BASE}. Start FastAPI on port 8000 and retry.`)
  }
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(body.detail || `Request failed with status ${response.status}`)
  }
  return response.json()
}

export const api = {
  getLeads: () => request('/leads'),
  getStats: () => request('/leads/stats'),
  getLead: (id) => request(`/leads/${id}`),
  createLead: (payload) => request('/leads', { method: 'POST', body: JSON.stringify(payload) }),
  importLeads: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5 * 60 * 1000); // 5 min timeout
    let response;
    try {
      response = await fetch(`${API_BASE}/leads/import`, {
        method: 'POST',
        body: formData,
        signal: controller.signal,
      });
    } catch (err) {
      clearTimeout(timeout);
      if (err.name === 'AbortError') {
        throw new Error('Import timed out. Try importing fewer leads at a time.');
      }
      throw new Error('Unable to reach the API. Make sure the backend is running.');
    }
    clearTimeout(timeout);
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw new Error(body.detail || `Import failed with status ${response.status}`);
    }
    return response.json();
  },
  runCompetitorAnalysis: (id) => request(`/leads/${id}/competitor-analysis`, { method: 'POST' }),
  generateOutreach: (id) => request(`/leads/${id}/outreach`, { method: 'POST' }),
  getPipeline: () => request('/pipeline'),
  getForecast: () => request('/pipeline/forecast'),
  createPipeline: (payload) => request('/pipeline', { method: 'POST', body: JSON.stringify(payload) }),
  seedPipeline: () => request('/pipeline/seed', { method: 'POST' }),
  getIntegrations: () => request('/integrations/status'),
}
