import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { authService } from '../services/authService'

const AuthContext = createContext(null)
const TOKEN_KEY = 'lead-manager-token'

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const acceptSession = useCallback((session) => {
    window.localStorage.setItem(TOKEN_KEY, session.access_token)
    setUser(session.user)
  }, [])

  const signOut = useCallback(() => {
    window.localStorage.removeItem(TOKEN_KEY)
    setUser(null)
  }, [])

  useEffect(() => {
    const token = window.localStorage.getItem(TOKEN_KEY)
    if (!token) {
      setLoading(false)
      return
    }
    authService.me()
      .then(setUser)
      .catch(signOut)
      .finally(() => setLoading(false))
  }, [signOut])

  const value = useMemo(() => ({
    user,
    loading,
    login: async (credentials) => acceptSession(await authService.login(credentials)),
    register: async (details) => acceptSession(await authService.register(details)),
    signOut,
  }), [acceptSession, loading, signOut, user])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}
