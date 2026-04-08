/**
 * DC86 Stream Toolkit - App
 * Haupt-App mit Routing und Layout.
 */

import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './hooks/useAuth'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Dashboard from './pages/Dashboard'
import Overlays from './pages/Overlays'
import Status from './pages/Status'
import AuthSuccess from './pages/AuthSuccess'
import AuthError from './pages/AuthError'

// ── Protected Route ──
function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-[80vh] flex items-center justify-center">
        <div className="w-10 h-10 border-4 border-dc-violet/30 border-t-dc-violet rounded-full animate-spin" />
      </div>
    )
  }

  return isAuthenticated ? children : <Navigate to="/" replace />
}

export default function App() {
  return (
    <div className="min-h-screen bg-dc-darker flex flex-col">
      <Navbar />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/dashboard" element={
            <ProtectedRoute><Dashboard /></ProtectedRoute>
          } />
          <Route path="/overlays" element={
            <ProtectedRoute><Overlays /></ProtectedRoute>
          } />
          <Route path="/status" element={
            <ProtectedRoute><Status /></ProtectedRoute>
          } />
          <Route path="/auth/success" element={<AuthSuccess />} />
          <Route path="/auth/error" element={<AuthError />} />
        </Routes>
      </main>

      {/* Footer */}
      <footer className="border-t border-dc-gray/30 mt-auto">
        <div className="max-w-7xl mx-auto px-4 py-6 flex items-center justify-between text-sm text-gray-500">
          <span>DC86 Stream Toolkit v0.2.0</span>
          <span>Made with 🎮 by derchrist</span>
        </div>
      </footer>
    </div>
  )
}
