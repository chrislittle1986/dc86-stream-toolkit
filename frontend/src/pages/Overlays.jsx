/**
 * DC86 Stream Toolkit - Overlays Page
 * Übersicht und Vorschau aller OBS Browser-Source Widgets.
 */

import { useState, useEffect } from 'react'
import { useAuth } from '../hooks/useAuth'
import {
  Monitor, Copy, CheckCircle, ExternalLink, Eye,
  BarChart3, Clock, Bell, Gamepad2, X
} from 'lucide-react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const OVERLAY_ICONS = {
  'goal-bar': BarChart3,
  'timer': Clock,
  'alerts': Bell,
  'now-playing': Gamepad2,
}

const OVERLAY_COLORS = {
  'goal-bar': 'text-dc-violet',
  'timer': 'text-yellow-400',
  'alerts': 'text-red-400',
  'now-playing': 'text-dc-mint',
}

export default function Overlays() {
  const { apiFetch } = useAuth()
  const [overlays, setOverlays] = useState(null)
  const [copied, setCopied] = useState(null)
  const [preview, setPreview] = useState(null)

  useEffect(() => {
    fetch(`${API_URL}/api/overlays`)
      .then(r => r.json())
      .then(setOverlays)
      .catch(err => console.error('Overlays laden fehlgeschlagen:', err))
  }, [])

  const copyToClipboard = (text, id) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(id)
      setTimeout(() => setCopied(null), 2000)
    })
  }

  const getFullUrl = (path) => `${API_URL}${path}`

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold flex items-center gap-3">
          <Monitor size={28} className="text-dc-violet" />
          OBS Overlays
        </h1>
        <p className="text-gray-400 text-sm mt-1">
          Browser-Source Widgets für OBS Studio. Kopiere die URL und füge sie als Browser-Source hinzu.
        </p>
      </div>

      {/* Setup Anleitung */}
      <div className="card mb-8 !bg-dc-violet/5 !border-dc-violet/20">
        <h3 className="font-semibold mb-2 flex items-center gap-2">
          <Monitor size={18} className="text-dc-violet" />
          So richtest du Overlays in OBS ein
        </h3>
        <div className="text-sm text-gray-300 space-y-1">
          <p>1. Kopiere die URL eines Overlays unten</p>
          <p>2. In OBS: Quellen → + → Browser</p>
          <p>3. Füge die URL ein</p>
          <p>4. Setze die Breite/Höhe (empfohlen: 500x80 für Goal-Bar, 400x120 für Timer)</p>
          <p>5. Haken bei "Seite neu laden wenn Szene aktiv wird"</p>
        </div>
      </div>

      {/* Overlay Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {overlays && Object.entries(overlays).map(([key, overlay]) => {
          const Icon = OVERLAY_ICONS[key] || Monitor
          const color = OVERLAY_COLORS[key] || 'text-gray-400'

          return (
            <div key={key} className="card">
              {/* Header */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-lg bg-dc-darker flex items-center justify-center`}>
                    <Icon size={22} className={color} />
                  </div>
                  <div>
                    <h3 className="font-semibold">{overlay.name}</h3>
                    <p className="text-xs text-gray-500">{overlay.description}</p>
                  </div>
                </div>
                <button
                  onClick={() => setPreview(preview === key ? null : key)}
                  className="text-xs text-dc-violet hover:text-dc-purple flex items-center gap-1 transition-colors"
                >
                  <Eye size={14} />
                  {preview === key ? 'Schließen' : 'Vorschau'}
                </button>
              </div>

              {/* URL Copy */}
              <div className="bg-dc-darker rounded-lg p-3 mb-3">
                <div className="flex items-center justify-between gap-2">
                  <code className="text-xs text-gray-300 truncate flex-1">
                    {getFullUrl(overlay.url)}
                  </code>
                  <button
                    onClick={() => copyToClipboard(getFullUrl(overlay.url), key)}
                    className="flex-shrink-0 text-gray-400 hover:text-white transition-colors"
                  >
                    {copied === key ? (
                      <CheckCircle size={16} className="text-dc-mint" />
                    ) : (
                      <Copy size={16} />
                    )}
                  </button>
                </div>
              </div>

              {/* Example URL */}
              {overlay.example && (
                <div className="mb-3">
                  <span className="text-xs text-gray-500 block mb-1">Beispiel mit Parametern:</span>
                  <div className="bg-dc-darker rounded-lg p-3 flex items-center justify-between gap-2">
                    <code className="text-xs text-dc-violet truncate flex-1">
                      {getFullUrl(overlay.example)}
                    </code>
                    <div className="flex gap-1 flex-shrink-0">
                      <button
                        onClick={() => copyToClipboard(getFullUrl(overlay.example), `${key}-example`)}
                        className="text-gray-400 hover:text-white transition-colors"
                      >
                        {copied === `${key}-example` ? (
                          <CheckCircle size={14} className="text-dc-mint" />
                        ) : (
                          <Copy size={14} />
                        )}
                      </button>
                      <a
                        href={getFullUrl(overlay.example)}
                        target="_blank"
                        rel="noopener"
                        className="text-gray-400 hover:text-white transition-colors"
                      >
                        <ExternalLink size={14} />
                      </a>
                    </div>
                  </div>
                </div>
              )}

              {/* Parameters */}
              {overlay.params && (
                <details className="text-xs">
                  <summary className="text-gray-500 cursor-pointer hover:text-gray-300 transition-colors">
                    Parameter anzeigen
                  </summary>
                  <div className="mt-2 space-y-1.5">
                    {Object.entries(overlay.params).map(([param, desc]) => (
                      <div key={param} className="flex gap-2">
                        <code className="text-dc-violet flex-shrink-0">?{param}=</code>
                        <span className="text-gray-400">{desc}</span>
                      </div>
                    ))}
                  </div>
                </details>
              )}

              {/* Preview iframe */}
              {preview === key && (
                <div className="mt-4 rounded-lg overflow-hidden border border-dc-gray/30">
                  <div className="bg-dc-darker px-3 py-2 flex items-center justify-between">
                    <span className="text-xs text-gray-500">Vorschau (klicken zum Testen)</span>
                    <button onClick={() => setPreview(null)} className="text-gray-500 hover:text-white">
                      <X size={14} />
                    </button>
                  </div>
                  <div className="bg-[#18181B] p-4">
                    <iframe
                      src={getFullUrl(overlay.example || overlay.url)}
                      width="100%"
                      height={key === 'alerts' ? '200' : key === 'timer' ? '160' : '100'}
                      style={{ border: 'none', background: 'transparent' }}
                      title={overlay.name}
                    />
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
