import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Layout({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen flex flex-col">
      <nav className="bg-white shadow-sm border-b border-rose-200">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 text-xl font-bold text-rose-600">
            <span>🌸</span>
            <span>Cycle Coach</span>
          </Link>
          {user && (
            <div className="flex items-center gap-4 text-sm">
              <Link to="/" className="hover:text-rose-600 transition">Dashboard</Link>
              <Link to="/check-in" className="hover:text-rose-600 transition">Check-in</Link>
              <Link to="/cycle" className="hover:text-rose-600 transition">Cycle</Link>
              <span className="text-gray-400">|</span>
              <span className="text-gray-500">{user.name}</span>
              <button onClick={handleLogout} className="text-gray-400 hover:text-rose-600 transition">
                Log out
              </button>
            </div>
          )}
        </div>
      </nav>
      <main className="flex-1 max-w-4xl w-full mx-auto px-4 py-6">
        {children}
      </main>
    </div>
  )
}