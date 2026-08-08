import { useQuery } from '@tanstack/react-query'
import { MapContainer, Marker, Popup, TileLayer } from 'react-leaflet'

import Loader from '../components/Loader.jsx'
import { fetchStats, fetchSurveys } from '../services/api.js'

const SEVERITY_BADGE = {
  Healthy: 'bg-emerald-100 text-emerald-800 border-emerald-300',
  'Partially Bleached': 'bg-amber-100 text-amber-800 border-amber-300',
  'Severely Bleached': 'bg-orange-100 text-orange-800 border-orange-300',
  'Dead Coral': 'bg-red-100 text-red-800 border-red-300',
  Unknown: 'bg-slate-100 text-slate-700 border-slate-300',
}

const RISK_BADGE = {
  Low: 'bg-emerald-100 text-emerald-800',
  Moderate: 'bg-amber-100 text-amber-800',
  High: 'bg-orange-100 text-orange-800',
  Critical: 'bg-red-100 text-red-800',
}

const STAT_CARDS = [
  { key: 'total_surveys', label: 'Total Surveys', icon: '🪸', accent: 'bg-ocean-600 text-white', big: true },
  { key: 'healthy', label: 'Healthy', icon: '💚', accent: 'bg-emerald-50 text-emerald-700' },
  { key: 'partially_bleached', label: 'Partially Bleached', icon: '🟡', accent: 'bg-amber-50 text-amber-700' },
  { key: 'severely_bleached', label: 'Severely Bleached', icon: '🟠', accent: 'bg-orange-50 text-orange-700' },
  { key: 'dead_coral', label: 'Dead Coral', icon: '⚫', accent: 'bg-red-50 text-red-700' },
  { key: 'unknown', label: 'Unknown', icon: '❔', accent: 'bg-slate-100 text-slate-600' },
]

function StatCard({ label, value, icon, accent, big }) {
  return (
    <div className={`flex items-center gap-3 rounded-xl border border-slate-200 p-4 shadow-sm ${accent}`}>
      <span className={`text-2xl ${big ? '' : 'opacity-80'}`}>{icon}</span>
      <div>
        <p className={`font-bold ${big ? 'text-2xl' : 'text-xl'}`}>{value}</p>
        <p className={`text-xs ${big ? 'text-ocean-100' : 'opacity-80'}`}>{label}</p>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const surveysQuery = useQuery({ queryKey: ['surveys'], queryFn: () => fetchSurveys({ limit: 100 }) })
  const statsQuery = useQuery({ queryKey: ['stats'], queryFn: fetchStats })

  if (surveysQuery.isLoading || statsQuery.isLoading) {
    return <Loader label="Loading survey history..." />
  }

  if (surveysQuery.isError) {
    return <p className="text-center text-red-600">Failed to load surveys. Is the backend running?</p>
  }

  const surveys = surveysQuery.data ?? []
  const stats = statsQuery.data
  const pinned = surveys.filter((s) => s.latitude != null && s.longitude != null)
  const mapCenter = pinned.length ? [pinned[0].latitude, pinned[0].longitude] : [0, 0]

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-ocean-900">Survey Dashboard</h1>
        <p className="mt-1 text-sm text-slate-500">
          Every reef survey submitted through CoralAI, with live location pins and risk history.
        </p>
      </div>

      {stats && (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
          {STAT_CARDS.map((card) => (
            <StatCard key={card.key} label={card.label} value={stats[card.key]} icon={card.icon} accent={card.accent} big={card.big} />
          ))}
        </div>
      )}

      {pinned.length > 0 && (
        <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-100 px-5 py-3">
            <h2 className="text-sm font-semibold text-slate-700">Survey Locations</h2>
          </div>
          <div className="h-80">
            <MapContainer center={mapCenter} zoom={3} className="h-full w-full" scrollWheelZoom={false}>
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              {pinned.map((s) => (
                <Marker key={s.id} position={[s.latitude, s.longitude]}>
                  <Popup>
                    Survey #{s.id} — {s.classification}
                  </Popup>
                </Marker>
              ))}
            </MapContainer>
          </div>
        </div>
      )}

      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        <div className="flex items-center justify-between border-b border-slate-100 px-5 py-3">
          <h2 className="text-sm font-semibold text-slate-700">Recent Surveys</h2>
          <span className="text-xs text-slate-400">{surveys.length} total</span>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-100 text-sm">
            <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-5 py-3">ID</th>
                <th className="px-5 py-3">Classification</th>
                <th className="px-5 py-3">Confidence</th>
                <th className="px-5 py-3">Risk</th>
                <th className="px-5 py-3">Submitted by</th>
                <th className="px-5 py-3">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {surveys.map((s, i) => (
                <tr key={s.id} className={i % 2 === 1 ? 'bg-slate-50/60' : undefined}>
                  <td className="px-5 py-3 font-medium text-slate-500">#{s.id}</td>
                  <td className="px-5 py-3">
                    <span
                      className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${
                        SEVERITY_BADGE[s.classification] ?? SEVERITY_BADGE.Unknown
                      }`}
                    >
                      {s.classification}
                    </span>
                  </td>
                  <td className="px-5 py-3 text-slate-600">{s.confidence.toFixed(0)}%</td>
                  <td className="px-5 py-3">
                    {s.risk_level ? (
                      <span
                        className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                          RISK_BADGE[s.risk_level] ?? 'bg-slate-100 text-slate-600'
                        }`}
                      >
                        {s.risk_level}
                      </span>
                    ) : (
                      <span className="text-slate-400">N/A</span>
                    )}
                  </td>
                  <td className="px-5 py-3 text-slate-500">{s.submitted_by || '—'}</td>
                  <td className="px-5 py-3 text-slate-500">{new Date(s.created_at).toLocaleString()}</td>
                </tr>
              ))}
              {surveys.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-5 py-10 text-center text-slate-400">
                    <p className="text-2xl">🪸</p>
                    <p className="mt-2">No surveys yet — upload a coral photo to get started.</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
