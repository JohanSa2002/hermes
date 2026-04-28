import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { authApi } from '@/lib/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      const stored = localStorage.getItem('user')
      if (stored) setUser(JSON.parse(stored))
    }
    setLoading(false)
  }, [])

  const login = useCallback(async (email, password) => {
    const { data } = await authApi.login({ email, password })
    localStorage.setItem('token', data.access_token)
    const userData = { email, business_id: data.business_id }
    localStorage.setItem('user', JSON.stringify(userData))
    setUser(userData)
    return data
  }, [])

  const register = useCallback(async (payload) => {
    const { data } = await authApi.register(payload)
    localStorage.setItem('token', data.access_token)
    const userData = { email: payload.email, business_id: data.business_id }
    localStorage.setItem('user', JSON.stringify(userData))
    setUser(userData)
    return data
  }, [])

  const logout = useCallback(async () => {
    try { await authApi.logout() } catch {}
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setUser(null)
  }, [])

  const isAuthenticated = Boolean(user)

  return (
    <AuthContext.Provider value={{ user, loading, isAuthenticated, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
