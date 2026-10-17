import { useState, useEffect } from 'react'
import { api } from '../api/client'

const PHASES = ['menstrual', 'follicular', 'ovulatory', 'luteal'] as const
const PHASE_EMOJIS: Record<string, string> = { menstrual: '🩸', follicular: '🌱', ovulatory: '🌕', luteal: '🌙' }
const PHASE_COLORS: Record<string, string> = {
  menstrual: 'border-rose-300 bg-rose-50',
  follicular: 'border-teal-300 bg-teal-50',
  ovulatory: 'border-amber-300 bg-amber-50',
  luteal: 'border-indigo-300 bg-indigo-50',
}

export default function CycleLog() {
  const [selectedPhase, setSelectedPhase] = useState<string>('')
  const [notes, setNotes] = useState('')
  const [entries, setEntries] = useState<any[]>([])
  const [phaseInfo, setPhaseInfo] = useState<any>(null)

  useEffect(() => {
    api.getCycleEntries().then(setEntries).catch(() => {})
  }, [])

  const handleSelect = async (phase: string) => {
    setSelectedPhase(phase)
    const info = await api.getPhaseInfo(phase)
    setPhaseInfo(info)
  }

  const handleLog = async () => {
    if (!selectedPhase) return
    const today = new Date().toISOString().split('T')[0]
    await api.logCycle({ phase: selectedPhase, date: today, notes })
    const updated = await api.getCycleEntries()
    setEntries(updated)
    setNotes('')
  }

  const latestPhase = entries[0]?.phase

  return (
    <div className="max-w-lg mx-auto space-y-6">
      <h1 className="text-2xl font-bold">Track Your Cycle</h1>

      <div className="grid grid-cols-2 gap-3">
        {PHASES.map((p) => (
          <button
            key={p}
            onClick={() => handleSelect(p)}
            className={`p-4 rounded-xl border-2 text-center transition ${
              selectedPhase === p
                ? `${PHASE_COLORS[p]} ring-2 ring-rose-400`
                : 'bg-white border-gray-200 hover:border-rose-300'
            }`}
          >
            <span className="text-2xl block mb-1">{PHASE_EMOJIS[p]}</span>
            <span className="font-medium capitalize text-sm">{p}</span>
            {latestPhase === p && (
              <span className="block text-xs text-rose-500 mt-1">Current</span>
            )}
          </button>
        ))}
      </div>

      {phaseInfo && (
        <div className="bg-white rounded-xl border border-gray-200 p-4 text-sm space-y-2">
          <h3 className="font-semibold text-rose-600 capitalize">{selectedPhase} phase</h3>
          <p><strong>Hormones:</strong> {phaseInfo.hormones}</p>
          <p><strong>Energy:</strong> {phaseInfo.energy}</p>
          <p><strong>Exercise:</strong> {phaseInfo.exercise}</p>
          <p><strong>Nutrition:</strong> {phaseInfo.nutrition}</p>
          <p><strong>Dopamine tip:</strong> {phaseInfo.dopamine_tip}</p>
        </div>
      )}

      {selectedPhase && (
        <div className="flex gap-3">
          <input
            type="text"
            placeholder="Notes (optional)"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            className="flex-1 px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-rose-300"
          />
          <button
            onClick={handleLog}
            className="bg-rose-500 text-white px-5 py-2 rounded-lg hover:bg-rose-600 transition font-medium"
          >
            Log phase
          </button>
        </div>
      )}

      {entries.length > 0 && (
        <div>
          <h3 className="font-semibold text-gray-600 mb-2">History</h3>
          <div className="space-y-2">
            {entries.slice(0, 10).map((e) => (
              <div key={e.id} className="bg-white border border-gray-200 rounded-lg px-4 py-2 flex items-center gap-3 text-sm">
                <span>{PHASE_EMOJIS[e.phase]}</span>
                <span className="font-medium capitalize">{e.phase}</span>
                <span className="text-gray-400 text-xs ml-auto">
                  {new Date(e.date).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}