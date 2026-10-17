import { useState, useEffect } from 'react'
import { api } from '../api/client'

export default function CheckIn() {
  const [form, setForm] = useState({
    sleep_hours: '',
    energy_level: 3,
    mood_level: 3,
    cravings: '',
    notes: '',
  })
  const [advice, setAdvice] = useState('')
  const [saved, setSaved] = useState(false)
  const [phase, setPhase] = useState<string | null>(null)
  const [sending, setSending] = useState(false)

  useEffect(() => {
    api.getCurrentPhase().then((r) => setPhase(r.phase)).catch(() => {})
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSending(true)
    try {
      const checkin = await api.createCheckin({
        sleep_hours: form.sleep_hours ? parseFloat(form.sleep_hours) : undefined,
        energy_level: form.energy_level,
        mood_level: form.mood_level,
        cravings: form.cravings,
        notes: form.notes,
      })
      setSaved(true)
      const coach = await api.chat({
        check_in_id: checkin.id,
        phase: phase || undefined,
        message: form.notes || 'How am I doing today?',
      })
      setAdvice(coach.advice)
    } catch (err: any) {
      alert(err.message)
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="max-w-lg mx-auto space-y-6">
      <h1 className="text-2xl font-bold">Daily Check-in</h1>

      {!saved ? (
        <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">😴 Sleep hours</label>
            <input
              type="number" step="0.5" min={0} max={24}
              placeholder="e.g. 6.5"
              value={form.sleep_hours}
              onChange={(e) => setForm({ ...form, sleep_hours: e.target.value })}
              className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-rose-300"
            />
            {form.sleep_hours && parseFloat(form.sleep_hours) < 6 && (
              <p className="text-amber-600 text-xs mt-1">That's low sleep. Expect cravings today — we've got you.</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">⚡ Energy level</label>
            <div className="flex gap-2">
              {[1, 2, 3, 4, 5].map((n) => (
                <button
                  key={n}
                  type="button"
                  onClick={() => setForm({ ...form, energy_level: n })}
                  className={`w-10 h-10 rounded-full text-sm font-medium border transition ${
                    form.energy_level === n
                      ? 'bg-rose-500 text-white border-rose-500'
                      : 'bg-white text-gray-500 border-gray-200 hover:border-rose-300'
                  }`}
                >
                  {n}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">😊 Mood</label>
            <div className="flex gap-2">
              {[1, 2, 3, 4, 5].map((n) => (
                <button
                  key={n}
                  type="button"
                  onClick={() => setForm({ ...form, mood_level: n })}
                  className={`w-10 h-10 rounded-full text-sm font-medium border transition ${
                    form.mood_level === n
                      ? 'bg-rose-500 text-white border-rose-500'
                      : 'bg-white text-gray-500 border-gray-200 hover:border-rose-300'
                  }`}
                >
                  {['😢', '😕', '😐', '🙂', '😊'][n - 1]}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">🍪 Cravings (optional)</label>
            <input
              type="text"
              placeholder="e.g. coffee, chocolate, carbs"
              value={form.cravings}
              onChange={(e) => setForm({ ...form, cravings: e.target.value })}
              className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-rose-300"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">📝 Notes (optional)</label>
            <textarea
              rows={3}
              placeholder="How are you feeling today?"
              value={form.notes}
              onChange={(e) => setForm({ ...form, notes: e.target.value })}
              className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-rose-300 resize-none"
            />
          </div>

          <button
            type="submit"
            disabled={sending}
            className="w-full bg-rose-500 text-white py-2.5 rounded-lg hover:bg-rose-600 transition font-medium disabled:opacity-50"
          >
            {sending ? 'Checking in...' : 'Save check-in'}
          </button>
        </form>
      ) : (
        <div className="space-y-6">
          <div className="bg-green-50 border border-green-200 rounded-xl p-4 text-center">
            <span className="text-2xl">✅</span>
            <p className="text-green-700 font-medium mt-1">Check-in saved!</p>
          </div>

          {advice && (
            <div className="bg-white border border-rose-200 rounded-xl p-5">
              <h3 className="font-semibold text-rose-600 mb-2">💬 Your coaching</h3>
              <p className="text-gray-700 text-sm leading-relaxed whitespace-pre-line">{advice}</p>
            </div>
          )}

          <button
            onClick={() => { setSaved(false); setAdvice(''); setForm({ sleep_hours: '', energy_level: 3, mood_level: 3, cravings: '', notes: '' }) }}
            className="w-full bg-white border border-gray-200 text-gray-600 py-2 rounded-lg hover:border-rose-300 transition font-medium"
          >
            New check-in
          </button>
        </div>
      )}
    </div>
  )
}