const BASE = '/api'

async function fetchJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  return res.json()
}

async function putJSON<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  return res.json()
}

async function postJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { method: 'POST' })
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  return res.json()
}

export const api = {
  dashboard: () => fetchJSON('/dashboard'),
  reports: (page = 1) => fetchJSON<any[]>(`/reports?page=${page}`),
  report: (id: number) => fetchJSON<any>(`/reports/${id}`),
  reportLatest: () => fetchJSON<any>('/reports/latest'),
  performanceSummary: (period = '30d') => fetchJSON<any>(`/performance/summary?period=${period}`),
  recommendations: (status = 'all') => fetchJSON<any[]>(`/performance/recommendations?status=${status}`),
  sectors: (period = '30d') => fetchJSON<any[]>(`/performance/sectors?period=${period}`),
  timeseries: (period = '30d') => fetchJSON<any[]>(`/performance/timeseries?period=${period}`),
  weeklyAnalyses: () => fetchJSON<any[]>('/retrospective/weekly'),
  dailyChecks: () => fetchJSON<any[]>('/retrospective/daily-checks'),
  settings: () => fetchJSON<any>('/settings'),
  updateSettings: (data: any) => putJSON('/settings', data),
  testEmail: () => postJSON('/settings/test-email'),
  healthCheck: () => fetchJSON<any>('/settings/status'),
  triggerPipeline: () => postJSON('/pipeline/run'),
  pipelineStatus: () => fetchJSON<any>('/pipeline/status'),
}
