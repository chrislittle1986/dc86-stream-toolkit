import { useState, useEffect } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export function useBotStatus(pollMs = 10000) {
  const [botStatus, setBotStatus] = useState('unknown')

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const res = await fetch(`${API_URL}/health`)
        const data = await res.json()
        setBotStatus(data.checks?.bot || 'unknown')
      } catch (err) {
        setBotStatus('unknown')
      }
    }

    fetchHealth()  // einmal sofort
    const interval = setInterval(fetchHealth, pollMs)

    return () => clearInterval(interval)  // aufräumen beim Unmount
  }, [pollMs])

  return botStatus
}