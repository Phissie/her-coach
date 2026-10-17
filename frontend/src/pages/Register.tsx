import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { api } from '../api/client'

export default function Register() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', name: '', password: '', cycle_length: 28, period_length: 5 })
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const res = await api.register(form)
      login(res.access_token, res.user)
      navigate('/')
    } catch (err: any) {
      setError(err.message)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="bg-white rounded-2xl shadow-lg p-8 w-full max-w-sm">
        <h1 className="text-2xl font-bold text-rose-600 text-center mb-2">🌸 Cycle Coach</h1>
        <p className="text-gray-500 text-center text-sm mb-6">Start your cycle-synced journey</p>
        {error && <p className="text-red-500 text-sm mb-4">{error}</p>}
        <form onSubmit={handleSubmit} className="space-y-3">
          <input
            type="text" placeholder="Name" required
            value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })}
            className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-rose-300"
          />
          <input
            type="email" placeholder="Email" required
            value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })}
            className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-rose-300"
          />
          <input
            type="password" placeholder="Password" required
            value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })}
            className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-rose-300"
          />
          <div className="flex gap-3">
            <div className="flex-1">
              <label className="text-xs text-gray-400">Cycle length (days)</label>
              <input
                type="number" min={21} max={45}
                value={form.cycle_length} onChange={(e) => setForm({ ...form, cycle_length: +e.target.value })}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-rose-300 text-sm"
              />
            </div>
            <div className="flex-1">
              <label className="text-xs text-gray-400">Period length (days)</label>
              <input
                type="number" min={2} max={10}
                value={form.period_length} onChange={(e) => setForm({ ...form, period_length: +e.target.value })}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-rose-300 text-sm"
              />
            </div>
          </div>
          <button
            type="submit"
            className="w-full bg-rose-500 text-white py-2 rounded-lg hover:bg-rose-600 transition font-medium mt-2"
          >
            Create account
          </button>
        </form>
        <p className="text-center text-sm text-gray-400 mt-6">
          Already have an account? <Link to="/login" className="text-rose-500 hover:underline">Log in</Link>
        </p>
      </div>
    </div>
  )
}