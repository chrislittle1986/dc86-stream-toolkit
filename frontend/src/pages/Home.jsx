/**
 * DC86 Stream Toolkit - Home Page
 * Landing Page (ausgeloggt) oder Redirect zum Dashboard (eingeloggt).
 */

import { Navigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import {
  Tv, Radio, MessageSquare, Layout, Film
} from 'lucide-react'

export default function Home() {
  const { isAuthenticated, loading, login } = useAuth()

  if (loading) {
    return (
      <div className="min-h-[80vh] flex items-center justify-center">
        <div className="w-10 h-10 border-4 border-dc-violet/30 border-t-dc-violet rounded-full animate-spin" />
      </div>
    )
  }

  // Eingeloggt → ab zum Dashboard
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }

  // Landing Page
  return (
    <div className="min-h-[80vh] flex flex-col items-center justify-center text-center px-4">
      {/* Hero */}
      <div className="mb-8">
        <div className="w-20 h-20 bg-dc-violet rounded-2xl flex items-center justify-center mx-auto mb-6
                      shadow-xl shadow-dc-violet/30">
          <Tv size={40} />
        </div>
        <h1 className="text-5xl font-extrabold tracking-tight mb-4">
          DC<span className="text-dc-violet">86</span> Stream Toolkit
        </h1>
        <p className="text-xl text-gray-400 max-w-lg mx-auto">
          Dein modulares Stream-Management-Toolkit für Twitch.
          Dashboard, Chat-Bot, Overlays — alles aus einer Hand.
        </p>
      </div>

      {/* Login Button */}
      <button onClick={login} className="btn-primary text-lg !px-8 !py-4 flex items-center gap-3">
        <svg viewBox="0 0 24 24" className="w-6 h-6 fill-current">
          <path d="M11.571 4.714h1.715v5.143H11.57zm4.715 0H18v5.143h-1.714zM6 0L1.714 4.286v15.428h5.143V24l4.286-4.286h3.428L22.286 12V0zm14.571 11.143l-3.428 3.428h-3.429l-3 3v-3H6.857V1.714h13.714z" />
        </svg>
        Mit Twitch einloggen
      </button>

      {/* Feature Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-16 max-w-5xl w-full">
        {[
          { icon: Layout, title: 'Dashboard', desc: 'Stream-Kontrolle auf einen Blick', color: 'text-dc-violet' },
          { icon: MessageSquare, title: 'Chat-Bot', desc: 'Custom Commands & Mini-Games', color: 'text-dc-mint' },
          { icon: Radio, title: 'Overlays', desc: 'OBS Widgets mit Live-Daten', color: 'text-yellow-400' },
          { icon: Film, title: 'Clips', desc: 'Auto-Clip & Highlight-Reel', color: 'text-pink-400' },
        ].map(({ icon: Icon, title, desc, color }) => (
          <div key={title} className="card text-left">
            <Icon size={24} className={`${color} mb-3`} />
            <h3 className="font-semibold mb-1">{title}</h3>
            <p className="text-sm text-gray-400">{desc}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
