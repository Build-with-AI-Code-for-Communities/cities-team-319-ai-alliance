import { useQuery } from '@tanstack/react-query'
import { MapContainer, Marker, Popup, TileLayer } from 'react-leaflet'

import Loader from '../components/Loader.jsx'
import { fetchStats, fetchSurveys } from '../services/api.js'

const SEVERITY_DOT = {
  Healthy: 'bg-emerald-500',
  'Partially Bleached': 'bg-amber-500',
  'Severely Bleached': 'bg-orange-500',
  'Dead Coral': 'bg-red-500',
  Unknown: 'bg-slate-400',
}

function StatCard({ label, value }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 text-center shadow-sm">
      <p className="text-2xl font-bold text-ocean-800">{value}</p>
      <p className="text-xs text-slate-500">{label}</p>
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
      <h1 className="text-2xl font-bold text-ocean-900">Survey Dashboard</h1>

      {stats && (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
          <StatCard label="Total" value={stats.total_surveys} />
          <StatCard label="Healthy" value={stats.healthy} />
          <StatCard label="Partially Bleached" value={stats.partially_bleached} />
          <StatCard label="Severely Bleached" value={stats.severely_bleached} />
          <StatCard label="Dead Coral" value={stats.dead_coral} />
          <StatCard label="Unknown" value={stats.unknown} />
        </div>
      )}

      {pinned.length > 0 && (
        <div className="h-80 overflow-hidden rounded-2xl border border-slate-200 shadow-sm">
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
      )}

      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-slate-100 text-sm">
          <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-4 py-3">ID</th>
              <th className="px-4 py-3">Classification</th>
              <th className="px-4 py-3">Confidence</th>
              <th className="px-4 py-3">Risk</th>
              <th className="px-4 py-3">Submitted by</th>
              <th className="px-4 py-3">Date</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {surveys.map((s) => (
              <tr key={s.id} className="hover:bg-slate-50">
                <td className="px-4 py-3 font-medium">#{s.id}</td>
                <td className="px-4 py-3">
                  <span className="inline-flex items-center gap-2">
                    <span className={`h-2 w-2 rounded-full ${SEVERITY_DOT[s.classification] ?? SEVERITY_DOT.Unknown}`} />
                    {s.classification}
                  </span>
                </td>
                <td className="px-4 py-3">{s.confidence.toFixed(0)}%</td>
                <td className="px-4 py-3">{s.risk_level ?? 'N/A'}</td>
                <td className="px-4 py-3 text-slate-500">{s.submitted_by || '—'}</td>
                <td className="px-4 py-3 text-slate-500">{new Date(s.created_at).toLocaleString()}</td>
              </tr>
            ))}
            {surveys.length === 0 && (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-slate-400">
                  No surveys yet — upload a coral photo to get started.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
