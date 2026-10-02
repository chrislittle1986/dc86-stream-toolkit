/**
 * DC86 Stream Toolkit - Bot Status Dot
 * Kleiner pulsierender Punkt, zeigt ob der Twitch-Bot gerade online ist.
 */

import { useBotStatus } from '../hooks/useBotStatus'

export default function BotStatusDot() {
  const botStatus = useBotStatus()

  const isOnline = botStatus === 'ok'

  const colorClass = isOnline ? 'bg-dc-mint' : 'bg-red-400'

  return (
    <div className="flex items-center gap-2" title={`Bot: ${botStatus}`}>
      <span className="relative flex h-3 w-3">
        {isOnline && (
          <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${colorClass} opacity-75`} />
        )}
        <span className={`relative inline-flex rounded-full h-3 w-3 ${colorClass}`} />
      </span>
      <span className="text-sm text-gray-400">
        {isOnline ? 'Bot online' : 'Bot offline'}
      </span>
    </div>
  )
}