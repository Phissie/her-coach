import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import Layout from './components/Layout'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import CheckIn from './pages/CheckIn'
import CycleLog from './pages/CycleLog'

function Protected({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="text-center py-20 text-gray-400">Loading...</div>
  if (!user) return <Navigate to="/login" replace />
  return <Layout>{children}</Layout>
}

function Public({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="text-center py-20 text-gray-400">Loading...</div>
  if (user) return <Navigate to="/" replace />
  return <>{children}</>
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Public><Login /></Public>} />
      <Route path="/register" element={<Public><Register /></Public>} />
      <Route path="/" element={<Protected><Dashboard /></Protected>} />
      <Route path="/check-in" element={<Protected><CheckIn /></Protected>} />
      <Route path="/cycle" element={<Protected><CycleLog /></Protected>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}