import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = window.localStorage.getItem('lead-manager-token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export function getErrorMessage(error) {
  if (axios.isAxiosError(error)) {
    if (error.response?.status === 503) return 'The service is temporarily unavailable. Please try again.'
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) return detail.map((item) => item.msg).join(' ')
    if (!error.response) return 'Unable to reach the server. Check your connection and try again.'
  }
  return 'Something went wrong. Please try again.'
}

export default api
