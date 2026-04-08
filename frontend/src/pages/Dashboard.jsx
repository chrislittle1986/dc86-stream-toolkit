/**
 * DC86 Stream Toolkit - Stream Dashboard
 * Komplett-Übersicht: Live-Status, Quick-Actions, Go-Live Checklist, Bot-Control.
 */

import { useState, useEffect, useCallback, useRef } from 'react'
import { useAuth } from '../hooks/useAuth'
import NowPlayingPanel from '../components/NowPlayingPanel'
import {
  Tv, Radio, Edit3, Tag, CheckSquare, Square, RefreshCw,
  Play, Clock, Users, MessageSquare, Zap, Settings,
  ChevronDown, ChevronUp, Save, X, ToggleLeft, ToggleRight,
  Volume2, VolumeX, Shield, Gamepad2, AlertCircle
} from 'lucide-react'

// ── Go-Live Checklist Items (Standard) ──
const DEFAULT_CHECKLIST = [
  { id: 'obs', label: 'OBS gestartet & Szene gecheckt', category: 'setup' },
  { id: 'audio', label: 'Audio-Check (Mic, Game, Music)', category: 'setup' },
  { id: 'title', label: 'Stream-Titel gesetzt', category: 'twitch' },
  { id: 'game', label: 'Game/Kategorie ausgewählt', category: 'twitch' },
  { id: 'tags', label: 'Tags aktualisiert', category: 'twitch' },
  { id: 'bot', label: 'Bot läuft & Commands gecheckt', category: 'tools' },
  { id: 'overlay', label: 'Overlays sichtbar & aktuell', category: 'tools' },
  { id: 'social', label: 'Going-Live Post (Discord/Twitter)', category: 'social' },
  { id: 'water', label: 'Wasser/Getränk bereitgestellt', category: 'personal' },
  { id: 'notifications', label: 'Benachrichtigungen stumm', category: 'personal' },
]

// ── Quick-Action Presets für Games ──
const GAME_PRESETS = [
  { name: 'World of Warcraft', id: '18122' },
  { name: 'Minecraft', id: '27471' },
  { name: 'Just Chatting', id: '509658' },
  { name: 'Music', id: '26936' },
  { name: 'Software & Game Dev', id: '1469308723' },
]

export default function Dashboard() {
  const { user, apiFetch } = useAuth()

  // ── State ──
  const [channel, setChannel] = useState(null)
  const [liveInfo, setLiveInfo] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Title/Game Edit
  const [editMode, setEditMode] = useState(null) // 'title' | 'game' | null
  const [newTitle, setNewTitle] = useState('')
  const [newGameId, setNewGameId] = useState('')
  const [saving, setSaving] = useState(false)
  const isTitleEditingRef = useRef(false) // Fix: verhindert Race Condition beim Auto-Refresh

  // Checklist
  const [checklist, setChecklist] = useState(() => {
    return DEFAULT_CHECKLIST.map(item => ({ ...item, checked: false }))
  })

  // Bot Control
  const [botSettings, setBotSettings] = useState({
    linkProtection: true,
    capsProtection: true,
    autoGreet: false,
  })

  // Panels
  const [expandedPanels, setExpandedPanels] = useState({
    quickActions: true,
    checklist: true,
    botControl: true,
  })

  // ── Daten laden ──
  const fetchData = useCallback(async () => {
    try {
      setLoading(true)
      const [channelData, liveData] = await Promise.all([
        apiFetch('/api/channel/info').catch(() => null),
        apiFetch('/api/channel/live').catch(() => null),
      ])
      setChannel(channelData)
      setLiveInfo(liveData)
      if (channelData?.title && !isTitleEditingRef.current) setNewTitle(channelData.title)
      setError(null)
    } catch (err) {
      setError('Daten konnten nicht geladen werden')
    } finally {
      setLoading(false)
    }
  }, [apiFetch])

  useEffect(() => { fetchData() }, [fetchData])

  // Auto-Refresh alle 30 Sekunden
  useEffect(() => {
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [fetchData])

  // ── Title Update ──
  const handleTitleUpdate = async () => {
    if (!newTitle.trim()) return
    setSaving(true)
    try {
      await apiFetch('/api/channel/update', {
        method: 'PATCH',
        body: JSON.stringify({ title: newTitle }),
      })
      setChannel(prev => ({ ...prev, title: newTitle }))
      isTitleEditingRef.current = false
      setEditMode(null)
    } catch (err) {
      setError('Titel konnte nicht aktualisiert werden')
    } finally {
      setSaving(false)
    }
  }

  // ── Game Update ──
  const handleGameUpdate = async (gameId, gameName) => {
    setSaving(true)
    try {
      await apiFetch('/api/channel/update', {
        method: 'PATCH',
        body: JSON.stringify({ game_id: gameId }),
      })
      setChannel(prev => ({ ...prev, game_name: gameName, game_id: gameId }))
      setEditMode(null)
    } catch (err) {
      setError('Game konnte nicht aktualisiert werden')
    } finally {
      setSaving(false)
    }
  }

  // ── Checklist Toggle ──
  const toggleCheckItem = (id) => {
    setChecklist(prev =>
      prev.map(item => item.id === id ? { ...item, checked: !item.checked } : item)
    )
  }

  const checklistProgress = checklist.filter(i => i.checked).length
  const checklistTotal = checklist.length
  const checklistPercent = Math.round((checklistProgress / checklistTotal) * 100)

  // ── Panel Toggle ──
  const togglePanel = (panel) => {
    setExpandedPanels(prev => ({ ...prev, [panel]: !prev[panel] }))
  }

  // ── Uptime berechnen ──
  const getUptime = (startedAt) => {
    if (!startedAt) return '—'
    const start = new Date(startedAt)
    const now = new Date()
    const diff = Math.floor((now - start) / 1000)
    const hours = Math.floor(diff / 3600)
    const minutes = Math.floor((diff % 3600) / 60)
    return `${hours}h ${minutes}m`
  }

  if (loading && !channel) {
    return (
      <div className="min-h-[80vh] flex items-center justify-center">
        <div className="w-10 h-10 border-4 border-dc-violet/30 border-t-dc-violet rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      {/* ── Header ── */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-3">
            <Gamepad2 size={28} className="text-dc-violet" />
            Stream Dashboard
          </h1>
          <p className="text-gray-400 text-sm mt-1">
            Willkommen zurück, {user?.display_name}
          </p>
        </div>
        <button
          onClick={fetchData}
          className="btn-secondary !px-3 !py-2 text-sm flex items-center gap-2"
        >
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          Aktualisieren
        </button>
      </div>

      {/* ── Error Banner ── */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-3 mb-6 flex items-center gap-3">
          <AlertCircle size={18} className="text-red-400" />
          <span className="text-red-300 text-sm">{error}</span>
          <button onClick={() => setError(null)} className="ml-auto text-red-400 hover:text-red-300">
            <X size={16} />
          </button>
        </div>
      )}

      {/* ── Live Status Banner ── */}
      <div className={`rounded-xl border p-5 mb-6 ${
        liveInfo?.is_live
          ? 'bg-gradient-to-r from-red-500/10 to-dc-dark border-red-500/40'
          : 'bg-dc-dark border-dc-gray/50'
      }`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className={`w-4 h-4 rounded-full ${
              liveInfo?.is_live ? 'bg-red-500 animate-pulse' : 'bg-gray-600'
            }`} />
            <div>
              <span className="text-lg font-bold">
                {liveInfo?.is_live ? '🔴 LIVE' : '⚫ Offline'}
              </span>
              {liveInfo?.is_live && (
                <p className="text-sm text-gray-400 mt-0.5">
                  {liveInfo.title}
                </p>
              )}
            </div>
          </div>

          {liveInfo?.is_live && (
            <div className="flex items-center gap-6 text-sm">
              <div className="flex items-center gap-2 text-gray-300">
                <Users size={16} className="text-dc-violet" />
                <span className="font-medium">{liveInfo.viewer_count}</span>
                <span className="text-gray-500">Viewer</span>
              </div>
              <div className="flex items-center gap-2 text-gray-300">
                <Clock size={16} className="text-dc-mint" />
                <span className="font-medium">{getUptime(liveInfo.started_at)}</span>
                <span className="text-gray-500">Uptime</span>
              </div>
              <div className="flex items-center gap-2 text-gray-300">
                <Tv size={16} className="text-yellow-400" />
                <span className="font-medium">{liveInfo.game_name}</span>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* ══════════ LINKE SPALTE (2/3) ══════════ */}
        <div className="lg:col-span-2 space-y-6">

          {/* ── Channel Info + Quick Actions ── */}
          <div className="card">
            <button
              onClick={() => togglePanel('quickActions')}
              className="w-full flex items-center justify-between mb-4"
            >
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <Zap size={20} className="text-yellow-400" />
                Quick Actions
              </h2>
              {expandedPanels.quickActions ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
            </button>

            {expandedPanels.quickActions && (
              <div className="space-y-4">
                {/* Titel */}
                <div className="bg-dc-darker rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-400 flex items-center gap-1.5">
                      <Edit3 size={14} /> Stream-Titel
                    </span>
                    {editMode !== 'title' ? (
                      <button
                        onClick={() => { isTitleEditingRef.current = true; setEditMode('title') }}
                        className="text-xs text-dc-violet hover:text-dc-purple transition-colors"
                      >
                        Bearbeiten
                      </button>
                    ) : (
                      <div className="flex gap-2">
                        <button
                          onClick={handleTitleUpdate}
                          disabled={saving}
                          className="text-xs text-dc-mint hover:text-green-400 flex items-center gap-1"
                        >
                          <Save size={12} /> {saving ? 'Speichern...' : 'Speichern'}
                        </button>
                        <button
                          onClick={() => { isTitleEditingRef.current = false; setEditMode(null); setNewTitle(channel?.title || '') }}
                          className="text-xs text-gray-400 hover:text-white"
                        >
                          <X size={12} />
                        </button>
                      </div>
                    )}
                  </div>
                  {editMode === 'title' ? (
                    <input
                      type="text"
                      value={newTitle}
                      onChange={(e) => setNewTitle(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && handleTitleUpdate()}
                      className="w-full bg-dc-dark border border-dc-gray rounded-lg px-3 py-2 text-white
                               focus:border-dc-violet focus:outline-none transition-colors"
                      placeholder="Neuer Stream-Titel..."
                      autoFocus
                    />
                  ) : (
                    <p className="font-medium">{channel?.title || 'Kein Titel gesetzt'}</p>
                  )}
                </div>

                {/* Game */}
                <div className="bg-dc-darker rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-400 flex items-center gap-1.5">
                      <Gamepad2 size={14} /> Game / Kategorie
                    </span>
                    <span className="text-sm font-medium text-dc-violet">
                      {channel?.game_name || 'Nicht gesetzt'}
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {GAME_PRESETS.map(game => (
                      <button
                        key={game.id}
                        onClick={() => handleGameUpdate(game.id, game.name)}
                        disabled={saving}
                        className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                          channel?.game_id === game.id
                            ? 'bg-dc-violet text-white'
                            : 'bg-dc-dark border border-dc-gray text-gray-300 hover:border-dc-violet hover:text-white'
                        }`}
                      >
                        {game.name}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Tags */}
                {channel?.tags?.length > 0 && (
                  <div className="bg-dc-darker rounded-lg p-4">
                    <span className="text-sm text-gray-400 flex items-center gap-1.5 mb-2">
                      <Tag size={14} /> Tags
                    </span>
                    <div className="flex flex-wrap gap-2">
                      {channel.tags.map(tag => (
                        <span key={tag} className="px-2.5 py-1 bg-dc-violet/20 text-dc-violet text-xs rounded-full">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* ── Bot Control Panel ── */}
          <div className="card">
            <button
              onClick={() => togglePanel('botControl')}
              className="w-full flex items-center justify-between mb-4"
            >
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <MessageSquare size={20} className="text-dc-mint" />
                Bot Control
              </h2>
              {expandedPanels.botControl ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
            </button>

            {expandedPanels.botControl && (
              <div className="space-y-3">
                {/* Bot Status */}
                <div className="flex items-center gap-3 bg-dc-darker rounded-lg p-3">
                  <div className="w-2.5 h-2.5 rounded-full bg-dc-mint animate-pulse" />
                  <span className="text-sm font-medium">DC86 Bot ist online</span>
                  <span className="text-xs text-gray-500 ml-auto">Channel: {user?.username || 'derchrist'}</span>
                </div>

                {/* Toggle Settings */}
                {[
                  {
                    key: 'linkProtection',
                    label: 'Link-Schutz',
                    desc: 'Links von Nicht-Mods werden gewarnt',
                    icon: Shield,
                    color: 'text-blue-400',
                  },
                  {
                    key: 'capsProtection',
                    label: 'Caps-Schutz',
                    desc: 'Übermäßige Großschreibung wird erkannt',
                    icon: VolumeX,
                    color: 'text-orange-400',
                  },
                  {
                    key: 'autoGreet',
                    label: 'Auto-Begrüßung',
                    desc: 'Neue Chatter werden automatisch begrüßt',
                    icon: Volume2,
                    color: 'text-green-400',
                  },
                ].map(({ key, label, desc, icon: Icon, color }) => (
                  <div
                    key={key}
                    className="flex items-center justify-between bg-dc-darker rounded-lg p-3 group hover:bg-dc-dark/80 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <Icon size={18} className={color} />
                      <div>
                        <span className="text-sm font-medium">{label}</span>
                        <p className="text-xs text-gray-500">{desc}</p>
                      </div>
                    </div>
                    <button
                      onClick={() => setBotSettings(prev => ({ ...prev, [key]: !prev[key] }))}
                      className="transition-colors"
                    >
                      {botSettings[key] ? (
                        <ToggleRight size={28} className="text-dc-mint" />
                      ) : (
                        <ToggleLeft size={28} className="text-gray-600" />
                      )}
                    </button>
                  </div>
                ))}

                {/* Quick Bot Commands */}
                <div className="pt-2">
                  <span className="text-xs text-gray-500 mb-2 block">Quick Commands</span>
                  <div className="flex flex-wrap gap-2">
                    {['!commands', '!uptime', '!leaderboard', '!quiz'].map(cmd => (
                      <span
                        key={cmd}
                        className="px-3 py-1.5 bg-dc-dark border border-dc-gray/50 rounded-lg text-xs font-mono text-gray-300"
                      >
                        {cmd}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* ══════════ RECHTE SPALTE (1/3) ══════════ */}
        <div className="space-y-6">

          {/* ── Go-Live Checklist ── */}
          <div className="card">
            <button
              onClick={() => togglePanel('checklist')}
              className="w-full flex items-center justify-between mb-4"
            >
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <CheckSquare size={20} className="text-dc-violet" />
                Go-Live Checklist
              </h2>
              {expandedPanels.checklist ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
            </button>

            {expandedPanels.checklist && (
              <>
                {/* Progress Bar */}
                <div className="mb-4">
                  <div className="flex items-center justify-between text-sm mb-1.5">
                    <span className="text-gray-400">{checklistProgress}/{checklistTotal}</span>
                    <span className={`font-medium ${
                      checklistPercent === 100 ? 'text-dc-mint' : 'text-dc-violet'
                    }`}>
                      {checklistPercent}%
                    </span>
                  </div>
                  <div className="w-full bg-dc-darker rounded-full h-2.5">
                    <div
                      className={`h-2.5 rounded-full transition-all duration-500 ${
                        checklistPercent === 100
                          ? 'bg-dc-mint'
                          : 'bg-gradient-to-r from-dc-purple to-dc-violet'
                      }`}
                      style={{ width: `${checklistPercent}%` }}
                    />
                  </div>
                </div>

                {/* Checklist Items */}
                <div className="space-y-1">
                  {checklist.map(item => (
                    <button
                      key={item.id}
                      onClick={() => toggleCheckItem(item.id)}
                      className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left
                                transition-all ${
                        item.checked
                          ? 'bg-dc-mint/5 text-gray-400'
                          : 'hover:bg-dc-darker text-white'
                      }`}
                    >
                      {item.checked ? (
                        <CheckSquare size={18} className="text-dc-mint flex-shrink-0" />
                      ) : (
                        <Square size={18} className="text-gray-600 flex-shrink-0" />
                      )}
                      <span className={`text-sm ${item.checked ? 'line-through' : ''}`}>
                        {item.label}
                      </span>
                    </button>
                  ))}
                </div>

                {/* Reset Button */}
                <button
                  onClick={() => setChecklist(prev => prev.map(i => ({ ...i, checked: false })))}
                  className="w-full mt-3 text-xs text-gray-500 hover:text-gray-300 transition-colors py-2"
                >
                  Checklist zurücksetzen
                </button>

                {/* Go Live Ready */}
                {checklistPercent === 100 && (
                  <div className="mt-3 bg-dc-mint/10 border border-dc-mint/30 rounded-lg p-3 text-center">
                    <Play size={20} className="text-dc-mint mx-auto mb-1" />
                    <p className="text-sm font-medium text-dc-mint">
                      Alles gecheckt — ready to go live! 🚀
                    </p>
                  </div>
                )}
              </>
            )}
          </div>

          {/* ── Stream Info Card ── */}
          <div className="card">
            <h2 className="text-lg font-semibold flex items-center gap-2 mb-4">
              <Radio size={20} className="text-red-400" />
              Stream Info
            </h2>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Channel</span>
                <span className="font-medium">{channel?.broadcaster_name || user?.username}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Game</span>
                <span className="font-medium">{channel?.game_name || '—'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Sprache</span>
                <span className="font-medium">{channel?.broadcaster_language || 'de'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Status</span>
                <span className={`font-medium ${liveInfo?.is_live ? 'text-red-400' : 'text-gray-500'}`}>
                  {liveInfo?.is_live ? 'Live' : 'Offline'}
                </span>
              </div>
            </div>
          </div>

          {/* ── Now Playing ── */}
          <NowPlayingPanel apiFetch={apiFetch} />

        </div>
      </div>
    </div>
  )
}
