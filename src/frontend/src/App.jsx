import { Route, Routes } from 'react-router-dom'

import Navbar from './components/Navbar.jsx'
import About from './pages/About.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Home from './pages/Home.jsx'

export default function App() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar />
      <main className="mx-auto max-w-6xl px-4 py-8">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </main>
    </div>
  )
}
