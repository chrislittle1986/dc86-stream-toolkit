/**
 * DC86 Stream Toolkit - Navbar
 */

import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { Tv, LogOut, LogIn, Activity, LayoutDashboard, Monitor } from 'lucide-react'

export default function Navbar() {
  const { user, isAuthenticated, login, logout } = useAuth()
  const location = useLocation()

  const isActive = (path) => location.pathname === path

  const navLink = (to, label, icon) => {
    const Icon = icon
    return (
      <Link
        to={to}
        className={`text-sm flex items-center gap-1.5 transition-colors ${
          isActive(to) ? 'text-white font-medium' : 'text-gray-400 hover:text-white'
        }`}
      >
        <Icon size={14} />
        {label}
      </Link>
    )
  }

  return (
    <nav className="bg-dc-dark border-b border-dc-gray/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-9 h-9 bg-dc-violet rounded-lg flex items-center justify-center
                          group-hover:bg-dc-purple transition-colors">
              <Tv size={20} />
            </div>
            <span className="text-lg font-bold tracking-tight">
              DC<span className="text-dc-violet">86</span>
            </span>
          </Link>

          {isAuthenticated && (
            <div className="hidden sm:flex items-center gap-6">
              {navLink('/dashboard', 'Dashboard', LayoutDashboard)}
              {navLink('/overlays', 'Overlays', Monitor)}
              {navLink('/status', 'Status', Activity)}
            </div>
          )}

          <div className="flex items-center gap-4">
            {isAuthenticated ? (
              <>
                <div className="flex items-center gap-3">
                  {user?.profile_image_url && (
                    <img
                      src={user.profile_image_url}
                      alt={user.display_name}
                      className="w-8 h-8 rounded-full ring-2 ring-dc-violet/50"
                    />
                  )}
                  <span className="text-sm font-medium hidden sm:block">
                    {user?.display_name}
                  </span>
                </div>
                <button onClick={logout} className="btn-secondary !px-3 !py-2 text-sm flex items-center gap-1.5">
                  <LogOut size={14} />
                  <span className="hidden sm:inline">Logout</span>
                </button>
              </>
            ) : (
              <button onClick={login} className="btn-primary !px-4 !py-2 text-sm flex items-center gap-2">
                <LogIn size={16} />
                Mit Twitch einloggen
              </button>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}
