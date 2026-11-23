import api from './api'

export const leadService = {
  list: async (params) => (await api.get('/leads', { params })).data,
  create: async (data) => (await api.post('/leads', data)).data,
  update: async (id, data) => (await api.put(`/leads/${id}`, data)).data,
  updateStatus: async (id, status) => (await api.patch(`/leads/${id}/status`, { status })).data,
  remove: async (id) => api.delete(`/leads/${id}`),
  stats: async () => (await api.get('/dashboard/stats')).data,
}
