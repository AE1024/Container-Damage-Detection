import { useState, useEffect, createContext, useContext } from 'react'
import AuthPage from './pages/AuthPage'
import DashboardPage from './pages/DashboardPage'
import Toast from './components/Toast'

export const AuthContext = createContext(null)
export const ToastContext = createContext(null)

export function useAuth() { return useContext(AuthContext) }
export function useToast() { return useContext(ToastContext) }

export default function App() {
  const [token,    setToken]   = useState(() => localStorage.getItem('cg_token'))
  const [user,     setUser]    = useState(() => {
    try { return JSON.parse(localStorage.getItem('cg_user')) } catch { return null }
  })
  const [toast,    setToast]   = useState(null)
  const [checking, setChecking] = useState(() => !!localStorage.getItem('cg_token'))

  useEffect(() => {
    if (!token) return
    fetch('/api/v1/auth/me', {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(res => {
        if (!res.ok) throw new Error('invalid')
      })
      .catch(() => {
        localStorage.removeItem('cg_token')
        localStorage.removeItem('cg_user')
        setToken(null)
        setUser(null)
      })
      .finally(() => setChecking(false))
  }, [])

  const login = (tok, userData) => {
    localStorage.setItem('cg_token', tok)
    localStorage.setItem('cg_user',  JSON.stringify(userData))
    setToken(tok)
    setUser(userData)
  }

  const logout = () => {
    localStorage.removeItem('cg_token')
    localStorage.removeItem('cg_user')
    setToken(null)
    setUser(null)
  }

  const showToast = (message, type = 'info') => {
    setToast({ message, type })
    setTimeout(() => setToast(null), 3500)
  }

  if (checking) return null

  return (
    <AuthContext.Provider value={{ token, user, setUser, login, logout }}>
      <ToastContext.Provider value={{ showToast }}>
        {token ? <DashboardPage /> : <AuthPage />}
        {toast && <Toast message={toast.message} type={toast.type} />}
      </ToastContext.Provider>
    </AuthContext.Provider>
  )
}
