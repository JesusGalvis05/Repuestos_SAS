import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { api, refreshSession, setAccessToken, setExpiredHandler } from './lib/api'
import type { Tokens, User } from './types'

type Auth = {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  reload: () => Promise<void>
}
const Context = createContext<Auth | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const cache = useQueryClient()
  function clear() {
    setAccessToken(null)
    setUser(null)
    cache.clear()
  }
  useEffect(() => {
    let mounted = true
    setExpiredHandler(clear)
    refreshSession()
      .then((data) => {
        if (mounted) setUser(data.user)
      })
      .catch(() => {
        if (mounted) clear()
      })
      .finally(() => {
        if (mounted) setLoading(false)
      })
    return () => {
      mounted = false
    }
    // Una sola restauración de sesión por montaje.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])
  async function login(email: string, password: string) {
    const { data } = await api.post<Tokens>('/auth/login', { email, password })
    cache.clear()
    setAccessToken(data.access_token)
    setUser(data.user)
  }
  async function logout() {
    await api.post('/auth/logout')
    clear()
  }
  async function reload() {
    const { data } = await api.get<User>('/auth/me')
    setUser(data)
  }
  return (
    <Context.Provider value={{ user, loading, login, logout, reload }}>{children}</Context.Provider>
  )
}

export function useAuth() {
  const context = useContext(Context)
  if (!context) throw new Error('AuthProvider no disponible')
  return context
}
