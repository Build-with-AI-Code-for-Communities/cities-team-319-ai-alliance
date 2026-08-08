import { NavLink } from 'react-router-dom'

const linkClass = ({ isActive }) =>
  `rounded-md px-3 py-2 text-sm font-medium transition-colors ${
    isActive ? 'bg-ocean-700 text-white' : 'text-ocean-900 hover:bg-ocean-100'
  }`

export default function Navbar() {
  return (
    <header className="border-b border-slate-200 bg-white/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <div className="flex items-center gap-2">
          <span className="text-xl">🪸</span>
          <span className="text-lg font-bold text-ocean-800">CoralAI</span>
        </div>
        <nav className="flex gap-2">
          <NavLink to="/" className={linkClass} end>
            Upload
          </NavLink>
          <NavLink to="/dashboard" className={linkClass}>
            Dashboard
          </NavLink>
        </nav>
      </div>
    </header>
  )
}
