import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { api } from '../api/client'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const res = await api.login({ email, password })
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
        <p className="text-gray-500 text-center text-sm mb-6">Welcome back</p>
        {error && <p className="text-red-500 text-sm mb-4">{error}</p>}
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-rose-300"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-rose-300"
          />
          <button
            type="submit"
            className="w-full bg-rose-500 text-white py-2 rounded-lg hover:bg-rose-600 transition font-medium"
          >
            Log in
          </button>
        </form>
        <p className="text-center text-sm text-gray-400 mt-6">
          New here? <Link to="/register" className="text-rose-500 hover:underline">Create account</Link>
        </p>
      </div>
    </div>
  )
}