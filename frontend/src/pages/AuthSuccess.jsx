/**
 * DC86 Stream Toolkit - Auth Success
 * Fängt den JWT Token aus der URL nach dem Twitch OAuth2 Callback.
 */

import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export default function AuthSuccess() {
  const [searchParams] = useSearchParams()
  const { saveToken } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    const token = searchParams.get('token')
    if (token) {
      saveToken(token)
      setTimeout(() => navigate('/dashboard', { replace: true }), 500)
    } else {
      navigate('/auth/error?error=no_token', { replace: true })
    }
  }, [searchParams, saveToken, navigate])

  return (
    <div className="min-h-[80vh] flex flex-col items-center justify-center">
      <div className="w-12 h-12 border-4 border-dc-violet/30 border-t-dc-violet rounded-full animate-spin mb-4" />
      <p className="text-gray-400">Login erfolgreich! Weiterleitung zum Dashboard...</p>
    </div>
  )
}
