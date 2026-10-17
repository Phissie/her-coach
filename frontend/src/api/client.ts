const BASE = '/api'

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('token')
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${BASE}${path}`, { ...options, headers })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Request failed')
  }
  return res.json()
}

export const api = {
  // Auth
  register: (data: { email: string; name: string; password: string; cycle_length?: number; period_length?: number }) =>
    request<{ access_token: string; user: any }>('/auth/register', { method: 'POST', body: JSON.stringify(data) }),
  login: (data: { email: string; password: string }) =>
    request<{ access_token: string; user: any }>('/auth/login', { method: 'POST', body: JSON.stringify(data) }),
  getMe: () => request<any>('/auth/me'),

  // Cycle
  logCycle: (data: { phase: string; date: string; notes?: string }) =>
    request<any>('/cycle/log', { method: 'POST', body: JSON.stringify(data) }),
  getCycleEntries: () => request<any[]>('/cycle/entries'),
  getCurrentPhase: () => request<{ phase: string | null; message?: string }>('/cycle/current'),

  // Check-in
  createCheckin: (data: { sleep_hours?: number; energy_level?: number; mood_level?: number; cravings?: string; notes?: string }) =>
    request<any>('/checkin/', { method: 'POST', body: JSON.stringify(data) }),
  getRecentCheckins: () => request<any[]>('/checkin/recent'),
  getLatestCheckin: () => request<any>('/checkin/latest'),

  // Coaching
  chat: (data: { check_in_id?: number; message?: string; phase?: string }) =>
    request<{ advice: string; phase: string | null }>('/coach/chat', { method: 'POST', body: JSON.stringify(data) }),
  getPhaseInfo: (phase: string) => request<any>(`/coach/phase-info/${phase}`),

  // Notifications
  getNotifications: () => request<any[]>('/notifications/'),
  markRead: (id: number) => request<any>(`/notifications/${id}/read`, { method: 'POST' }),
}