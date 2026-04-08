/**
 * DC86 Stream Toolkit - Status Page
 * System-Status mit Details zu allen Services.
 */

import { useState, useEffect } from 'react'
import { useAuth } from '../hooks/useAuth'
import {
  Activity, Database, Wifi, Tv, Server,
  CheckCircle, AlertCircle, XCircle, RefreshCw
} from 'lucide-react'

export default function Status() {
  const { apiFetch } = useAuth()
  const [status, setStatus] = useState(null)
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  const fetchStatus = async () => {
    setLoading(true)
    try {
      const [healthRes, readyRes] = await Promise.all([
        fetch(`${API_URL}/api/status/health`).then(r => r.json()),
        apiFetch('/api/status/ready').catch(() => null),
      ])
      setHealth(healthRes)
      setStatus(readyRes)
    } catch (err) {
      console.error('Status-Fetch fehlgeschlagen:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchStatus() }, [])

  const StatusIcon = ({ s }) => {
    if (s === 'connected' || s === 'configured' || s === 'ready' || s === 'online')
      return <CheckCircle size={18} className="text-dc-mint" />
    if (s === 'degraded' || s === 'not_configured')
      return <AlertCircle size={18} className="text-yellow-400" />
    return <XCircle size={18} className="text-red-400" />
  }

  const getIcon = (key) => {
    switch (key) {
      case 'database': return <Database size={20} className="text-blue-400" />
      case 'cache': return <Wifi size={20} className="text-green-400" />
      case 'twitch': return <Tv size={20} className="text-dc-violet" />
      default: return <Server size={20} className="text-gray-400" />
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold flex items-center gap-3">
          <Activity size={28} className="text-dc-mint" />
          System Status
        </h1>
        <button
          onClick={fetchStatus}
          className="btn-secondary !px-3 !py-2 text-sm flex items-center gap-2"
        >
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {/* Overall Status */}
      <div className={`card mb-6 flex items-center gap-4 ${
        status?.status === 'ready'
          ? '!border-dc-mint/30'
          : '!border-yellow-500/30'
      }`}>
        <StatusIcon s={status?.status || health?.status} />
        <div>
          <span className="font-semibold text-lg">
            {health?.app || 'DC86 Stream Toolkit'}
          </span>
          <p className="text-sm text-gray-400">
            {health?.message || 'Status wird geladen...'}
          </p>
        </div>
        <span className={`ml-auto px-3 py-1 rounded-full text-xs font-medium ${
          status?.status === 'ready'
            ? 'bg-dc-mint/10 text-dc-mint'
            : 'bg-yellow-500/10 text-yellow-400'
        }`}>
          {status?.status || 'loading'}
        </span>
      </div>

      {/* Service Details */}
      <div className="space-y-4">
        {status?.checks && Object.entries(status.checks).map(([key, val]) => (
          <div key={key} className="card flex items-center gap-4">
            {getIcon(key)}
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span className="font-medium capitalize">{key}</span>
                <span className="text-xs text-gray-500">
                  {val.type || ''}
                </span>
              </div>
              {val.hint && (
                <p className="text-xs text-yellow-400 mt-0.5">{val.hint}</p>
              )}
              {val.error && (
                <p className="text-xs text-red-400 mt-0.5">{val.error}</p>
              )}
            </div>
            <div className="flex items-center gap-2">
              <StatusIcon s={val.status} />
              <span className="text-sm text-gray-400">{val.status}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
