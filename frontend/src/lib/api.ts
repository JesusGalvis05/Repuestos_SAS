import axios from 'axios'
import type { Tokens } from '../types'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
  withCredentials: true,
  timeout: 15000,
})
let accessToken: string | null = null
let refreshPromise: Promise<Tokens> | null = null
let onExpired: () => void = () => {}

export function setAccessToken(token: string | null) {
  accessToken = token
}
export function setExpiredHandler(handler: () => void) {
  onExpired = handler
}

export function refreshSession(): Promise<Tokens> {
  if (!refreshPromise) {
    const request = async () => {
      const { data } = await api.post<Tokens>('/auth/refresh')
      setAccessToken(data.access_token)
      return data
    }
    // El bloqueo del navegador serializa renovaciones entre pestañas del mismo origen.
    refreshPromise = (
      'locks' in navigator ? navigator.locks.request('jg-refresh', request) : request()
    ).finally(() => {
      refreshPromise = null
    })
  }
  return refreshPromise
}

api.interceptors.request.use((config) => {
  if (accessToken) config.headers.Authorization = `Bearer ${accessToken}`
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config
    if (
      error.response?.status === 401 &&
      config &&
      !config._retried &&
      !['/auth/login', '/auth/refresh', '/auth/logout'].includes(config.url)
    ) {
      config._retried = true
      try {
        await refreshSession()
        return await api(config)
      } catch {
        setAccessToken(null)
        onExpired()
      }
    }
    return Promise.reject(error)
  },
)

export function errorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    if (!error.response) return 'No se pudo conectar con el servidor. Inténtelo nuevamente.'
    return error.response.data?.error?.message || 'No fue posible completar la operación.'
  }
  return 'Ocurrió un error inesperado.'
}
