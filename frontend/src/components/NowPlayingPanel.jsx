/**
 * DC86 Stream Toolkit - Now Playing Panel
 * In Dashboard.jsx einbauen: import NowPlayingPanel from '../components/NowPlayingPanel'
 * Dann irgendwo im JSX: <NowPlayingPanel apiFetch={apiFetch} />
 */

import { useState } from 'react'
import { Music, X, ExternalLink, Play } from 'lucide-react'

export default function NowPlayingPanel({ apiFetch }) {
  const [url, setUrl]         = useState('')
  const [status, setStatus]   = useState(null)  // { title, author, thumbnail } | null
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)

  const handleSet = async () => {
    if (!url.trim()) return
    setLoading(true)
    setError(null)
    try {
      const res = await apiFetch('/api/music/set', {
        method: 'POST',
        body: JSON.stringify({ url }),
      })
      setStatus(res)
    } catch (err) {
      setError('Konnte nicht gesetzt werden – gültige YouTube URL?')
    } finally {
      setLoading(false)
    }
  }

  const handleClear = async () => {
    try {
      await apiFetch('/api/music/clear', { method: 'DELETE' })
      setStatus(null)
      setUrl('')
    } catch {}
  }

  return (
    <div className="card">
      <h2 className="text-lg font-semibold flex items-center gap-2 mb-4">
        <Music size={20} className="text-dc-violet" />
        Now Playing
      </h2>

      {/* Aktuell läuft */}
      {status && (
        <div className="flex items-center gap-3 bg-dc-darker rounded-lg p-3 mb-4">
          {status.thumbnail && (
            <img
              src={status.thumbnail}
              alt=""
              className="w-12 h-12 rounded object-cover flex-shrink-0"
            />
          )}
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate text-white">{status.title}</p>
            <p className="text-xs text-gray-400 truncate">{status.author}</p>
          </div>
          <a
            href={url}
            target="_blank"
            rel="noreferrer"
            className="text-dc-violet hover:text-dc-purple flex-shrink-0"
          >
            <ExternalLink size={16} />
          </a>
          <button
            onClick={handleClear}
            className="text-gray-500 hover:text-red-400 flex-shrink-0 transition-colors"
            title="Song entfernen"
          >
            <X size={16} />
          </button>
        </div>
      )}

      {/* URL Eingabe */}
      <div className="flex gap-2">
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSet()}
          placeholder="YouTube URL einfügen..."
          className="flex-1 bg-dc-dark border border-dc-gray rounded-lg px-3 py-2 text-white text-sm
                     focus:border-dc-violet focus:outline-none transition-colors"
        />
        <button
          onClick={handleSet}
          disabled={loading || !url.trim()}
          className="btn-primary !px-3 !py-2 flex items-center gap-1.5 text-sm"
        >
          <Play size={14} />
          {loading ? '...' : 'Setzen'}
        </button>
      </div>

      {error && (
        <p className="text-xs text-red-400 mt-2">{error}</p>
      )}

      <p className="text-xs text-gray-600 mt-2">
        Titel & Thumbnail werden automatisch von YouTube geladen.
      </p>
    </div>
  )
}
