import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'

const PHASE_COLORS: Record<string, string> = {
  menstrual: 'bg-rose-100 border-rose-300 text-rose-800',
  follicular: 'bg-teal-100 border-teal-300 text-teal-800',
  ovulatory: 'bg-amber-100 border-amber-300 text-amber-800',
  luteal: 'bg-indigo-100 border-indigo-300 text-indigo-800',
}

const PHASE_EMOJIS: Record<string, string> = {
  menstrual: '🩸',
  follicular: '🌱',
  ovulatory: '🌕',
  luteal: '🌙',
}

const PHASE_TIPS: Record<string, string> = {
  menstrual: 'Rest, iron-rich foods, gentle movement. Your body is doing important work.',
  follicular: 'Energy rising! Great time for strength training and starting new projects.',
  ovulatory: 'You\'re at your peak. HIIT, cardio, social plans — you\'ve got this.',
  luteal: 'Energy dipping. Complex carbs, magnesium, lower-impact movement. Be patient.',
}

export default function Dashboard() {
  const { user } = useAuth()
  const [phase, setPhase] = useState<string | null>(null)
  const [latestCheckin, setLatestCheckin] = useState<any>(null)
  const [coachAdvice, setCoachAdvice] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.getCurrentPhase(),
      api.getLatestCheckin(),
    ]).then(([phaseData, checkin]) => {
      setPhase(phaseData.phase)
      setLatestCheckin(checkin)
    }).finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (phase) {
      api.chat({ phase, message: 'Give me my daily coaching based on my current phase.' })
        .then((r) => setCoachAdvice(r.advice))
        .catch(() => {})
    }
  }, [phase])

  if (loading) {
    return <div className="text-center py-20 text-gray-400">Loading your cycle data...</div>
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Hello, {user?.name} 👋</h1>

      {!phase && (
        <div className="bg-white border border-rose-200 rounded-xl p-6 text-center">
          <p className="text-gray-500 mb-3">You haven't logged your cycle phase yet.</p>
          <Link to="/cycle" className="inline-block bg-rose-500 text-white px-6 py-2 rounded-lg hover:bg-rose-600 transition font-medium">
            Log your cycle phase
          </Link>
        </div>
      )}

      {phase && (
        <div className={`border-2 rounded-xl p-5 ${PHASE_COLORS[phase] || 'bg-gray-100'}`}>
          <div className="flex items-center gap-3 mb-2">
            <span className="text-3xl">{PHASE_EMOJIS[phase]}</span>
            <div>
              <h2 className="text-lg font-bold capitalize">{phase} Phase</h2>
              <p className="text-sm opacity-80">{PHASE_TIPS[phase]}</p>
            </div>
          </div>
        </div>
      )}

      {coachAdvice && (
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h3 className="font-semibold text-rose-600 mb-2">💬 Coach says</h3>
          <p className="text-gray-700 text-sm leading-relaxed whitespace-pre-line">{coachAdvice}</p>
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        <Link to="/check-in" className="bg-white rounded-xl border border-gray-200 p-5 hover:border-rose-300 transition text-center">
          <span className="text-2xl block mb-1">📝</span>
          <span className="font-medium text-sm">Daily Check-in</span>
          {latestCheckin && (
            <p className="text-xs text-gray-400 mt-1">
              {latestCheckin.sleep_hours ? `${latestCheckin.sleep_hours}h sleep` : 'No sleep logged'} ·
              Energy {latestCheckin.energy_level || '?'}/5
            </p>
          )}
        </Link>
        <Link to="/cycle" className="bg-white rounded-xl border border-gray-200 p-5 hover:border-rose-300 transition text-center">
          <span className="text-2xl block mb-1">📅</span>
          <span className="font-medium text-sm">Cycle Log</span>
          <p className="text-xs text-gray-400 mt-1">Track your phases</p>
        </Link>
      </div>
    </div>
  )
}