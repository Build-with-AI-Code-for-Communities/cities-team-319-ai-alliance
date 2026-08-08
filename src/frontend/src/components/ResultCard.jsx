import { useState } from 'react'
import toast from 'react-hot-toast'

import { generateReport } from '../services/api.js'
import MapView from './MapView.jsx'

const SEVERITY_STYLES = {
  Healthy: 'bg-emerald-100 text-emerald-800 border-emerald-300',
  'Partially Bleached': 'bg-amber-100 text-amber-800 border-amber-300',
  'Severely Bleached': 'bg-orange-100 text-orange-800 border-orange-300',
  'Dead Coral': 'bg-red-100 text-red-800 border-red-300',
  Unknown: 'bg-slate-100 text-slate-700 border-slate-300',
}

const RISK_STYLES = {
  Low: 'text-emerald-600',
  Moderate: 'text-amber-600',
  High: 'text-orange-600',
  Critical: 'text-red-600',
}

export default function ResultCard({ survey }) {
  const [downloading, setDownloading] = useState(false)

  const badgeClass = SEVERITY_STYLES[survey.classification] ?? SEVERITY_STYLES.Unknown

  async function handleDownload() {
    try {
      setDownloading(true)
      const url = await generateReport(survey.id)
      window.open(url, '_blank', 'noopener,noreferrer')
    } catch {
      toast.error('Could not generate report. Please try again.')
    } finally {
      setDownloading(false)
    }
  }

  return (
    <div className="grid gap-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm md:grid-cols-2">
      <div>
        <div className="flex items-center justify-between gap-2">
          <div className={`inline-flex items-center rounded-full border px-3 py-1 text-sm font-semibold ${badgeClass}`}>
            {survey.classification}
          </div>
          {survey.submitted_by && (
            <span className="text-xs text-slate-400">Submitted by {survey.submitted_by}</span>
          )}
        </div>

        <dl className="mt-4 space-y-2 text-sm">
          <div className="flex justify-between border-b border-slate-100 py-1.5">
            <dt className="text-slate-500">Severity</dt>
            <dd className="font-medium">{survey.severity}</dd>
          </div>
          <div className="flex justify-between border-b border-slate-100 py-1.5">
            <dt className="text-slate-500">Confidence</dt>
            <dd className="font-medium">{survey.confidence.toFixed(0)}%</dd>
          </div>
          <div className="flex justify-between border-b border-slate-100 py-1.5">
            <dt className="text-slate-500">Risk Level</dt>
            <dd className={`font-semibold ${RISK_STYLES[survey.risk_level] ?? ''}`}>
              {survey.risk_level ?? 'N/A'}
            </dd>
          </div>
          <div className="flex justify-between border-b border-slate-100 py-1.5">
            <dt className="text-slate-500">Temperature</dt>
            <dd className="font-medium">
              {survey.temperature != null ? `${survey.temperature.toFixed(1)} °C` : 'N/A'}
            </dd>
          </div>
        </dl>

        <div className="mt-4 space-y-3">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Possible Cause</p>
            <p className="mt-1 text-sm text-slate-700">{survey.possible_cause || 'Not determined.'}</p>
          </div>
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Recommendation</p>
            <p className="mt-1 text-sm text-slate-700">{survey.recommendation || 'No recommendation available.'}</p>
          </div>
        </div>

        <button
          onClick={handleDownload}
          disabled={downloading}
          className="mt-5 rounded-lg bg-ocean-700 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-ocean-800 disabled:opacity-50"
        >
          {downloading ? 'Generating...' : 'Download PDF Report'}
        </button>
      </div>

      <div className="h-64 overflow-hidden rounded-xl md:h-full">
        <MapView latitude={survey.latitude} longitude={survey.longitude} label={survey.classification} />
      </div>
    </div>
  )
}
