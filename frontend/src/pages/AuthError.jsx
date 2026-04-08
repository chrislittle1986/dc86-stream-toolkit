/**
 * DC86 Stream Toolkit - Auth Error
 * Zeigt Fehlermeldungen nach fehlgeschlagenem OAuth2 Login.
 */

import { useSearchParams, Link } from 'react-router-dom'
import { AlertCircle } from 'lucide-react'

export default function AuthError() {
  const [searchParams] = useSearchParams()
  const error = searchParams.get('error') || 'Unbekannter Fehler'

  const errorMessages = {
    access_denied: 'Du hast den Twitch-Login abgebrochen.',
    no_token: 'Kein Token erhalten — bitte versuch es nochmal.',
    invalid_state: 'Ungültiger OAuth State — möglicher CSRF-Angriff.',
  }

  return (
    <div className="min-h-[80vh] flex flex-col items-center justify-center text-center px-4">
      <AlertCircle size={48} className="text-red-400 mb-4" />
      <h1 className="text-2xl font-bold mb-2">Login fehlgeschlagen</h1>
      <p className="text-gray-400 mb-6 max-w-md">
        {errorMessages[error] || `Fehler: ${error}`}
      </p>
      <Link to="/" className="btn-primary">
        Zurück zur Startseite
      </Link>
    </div>
  )
}
