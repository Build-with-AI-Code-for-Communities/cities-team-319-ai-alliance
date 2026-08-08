import { Link, NavLink } from 'react-router-dom'

const linkClass = ({ isActive }) =>
  `rounded-lg px-2 py-2 text-xs font-semibold transition-colors sm:px-3 sm:text-sm ${
    isActive ? 'bg-ocean-700 text-white shadow-sm' : 'text-ocean-900 hover:bg-ocean-100'
  }`

export default function Navbar() {
  return (
    <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-3 py-3 sm:px-4">
        <Link to="/" className="flex shrink-0 items-center gap-1.5 sm:gap-2">
          <span className="text-xl">🪸</span>
          <span className="text-base font-bold text-ocean-800 sm:text-lg">CoralAI</span>
        </Link>
        <nav className="flex gap-1 sm:gap-2">
          <NavLink to="/" className={linkClass} end>
            Upload
          </NavLink>
          <NavLink to="/dashboard" className={linkClass}>
            Dashboard
          </NavLink>
          <NavLink to="/about" className={linkClass}>
            About
          </NavLink>
        </nav>
      </div>
    </header>
  )
}
