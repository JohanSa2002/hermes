import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export const authApi = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  logout: () => api.post('/auth/logout'),
}

export const businessApi = {
  getMe: () => api.get('/business/me'),
  updateMe: (data) => api.put('/business/me', data),
  getConfig: () => api.get('/business/me/config'),
  updateConfig: (data) => api.put('/business/me/config', data),
}

export const whatsappApi = {
  getStatus: () => api.get('/whatsapp/status'),
  connect: (data) => api.post('/whatsapp/connect', data),
  disconnect: () => api.post('/whatsapp/disconnect'),
}

export const reservationsApi = {
  list: (params) => api.get('/reservations/', { params }),
  create: (data) => api.post('/reservations/', data),
  get: (id) => api.get(`/reservations/${id}`),
  update: (id, data) => api.put(`/reservations/${id}`, data),
  updateStatus: (id, status) => api.patch(`/reservations/${id}/status`, { status }),
  delete: (id) => api.delete(`/reservations/${id}`),
}

export const serviceApi = {
  list: () => api.get('/business/me/services'),
  create: (data) => api.post('/business/me/services', data),
  update: (id, data) => api.put(`/business/me/services/${id}`, data),
  remove: (id) => api.delete(`/business/me/services/${id}`),
}

export const tableApi = {
  list: () => api.get('/business/me/tables'),
  create: (data) => api.post('/business/me/tables', data),
  update: (id, data) => api.put(`/business/me/tables/${id}`, data),
  remove: (id) => api.delete(`/business/me/tables/${id}`),
}

export const calendarApi = {
  getAvailability: (date) => api.get('/calendar/availability', { params: { date } }),
  getAvailabilityRange: (start, end) =>
    api.get('/calendar/availability/range', { params: { start_date: start, end_date: end } }),
  blockDate: (date) => api.post('/calendar/blocked-dates', { date }),
  unblockDate: (date) => api.delete(`/calendar/blocked-dates/${date}`),
}

export const dashboardApi = {
  getStats: () => api.get('/dashboard/stats'),
  getAgenda: (date) => api.get('/dashboard/agenda', { params: { date } }),
  getPeakHours: () => api.get('/dashboard/peak-hours'),
}

export const billingApi = {
  getPlan: () => api.get('/billing/plan'),
  getUsage: () => api.get('/billing/usage'),
  upgrade: (plan) => api.post('/billing/upgrade', { plan }),
}

export default api
