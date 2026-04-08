/**
 * DC86 Stream Toolkit - Auth Hook
 * React Context für JWT Token-Management und User-State.
 */

import { createContext, useContext, useState, useEffect, useCallback } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(() => {
    // Token aus sessionStorage laden (überlebt Page-Refresh)
    try {
      return window.sessionStorage?.getItem('dc86_token') || null
    } catch {
      return null
    }
  })
  const [loading, setLoading] = useState(true)

  // ── Token speichern ──
  const saveToken = useCallback((newToken) => {
    setToken(newToken)
    try {
      if (newToken) {
        window.sessionStorage?.setItem('dc86_token', newToken)
      } else {
        window.sessionStorage?.removeItem('dc86_token')
      }
    } catch {
      // sessionStorage nicht verfügbar — kein Problem
    }
  }, [])

  // ── User-Daten laden ──
  const fetchUser = useCallback(async (authToken) => {
    if (!authToken) {
      setUser(null)
      setLoading(false)
      return
    }

    try {
      const res = await fetch(`${API_URL}/api/auth/me`, {
        headers: { Authorization: `Bearer ${authToken}` },
      })

      if (res.ok) {
        const data = await res.json()
        setUser(data)
      } else {
        // Token ungültig → aufräumen
        saveToken(null)
        setUser(null)
      }
    } catch (err) {
      console.error('User-Fetch fehlgeschlagen:', err)
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [saveToken])

  // ── Beim Start: User laden wenn Token vorhanden ──
  useEffect(() => {
    fetchUser(token)
  }, [token, fetchUser])

  // ── Login: Redirect zu Twitch ──
  const login = () => {
    window.location.href = `${API_URL}/api/auth/login`
  }

  // ── Logout ──
  const logout = async () => {
    if (token) {
      try {
        await fetch(`${API_URL}/api/auth/logout`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
        })
      } catch {
        // Ignorieren — wir loggen trotzdem aus
      }
    }
    saveToken(null)
    setUser(null)
  }

  // ── API-Helper mit Auth ──
  const apiFetch = useCallback(async (endpoint, options = {}) => {
    const res = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers,
      },
    })
    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: 'Unbekannter Fehler' }))
      throw new Error(error.detail || `HTTP ${res.status}`)
    }
    return res.json()
  }, [token])

  const value = {
    user,
    token,
    loading,
    login,
    logout,
    saveToken,
    apiFetch,
    isAuthenticated: !!user,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth muss innerhalb von AuthProvider verwendet werden')
  }
  return context
}
