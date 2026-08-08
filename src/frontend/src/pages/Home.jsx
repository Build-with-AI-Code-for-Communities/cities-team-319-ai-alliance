import { useRef, useState } from 'react'
import { Link } from 'react-router-dom'

import ResultCard from '../components/ResultCard.jsx'
import UploadCard from '../components/UploadCard.jsx'

const STEPS = [
  {
    icon: '📸',
    title: '1. Photograph a reef',
    body: 'Snap an underwater photo of coral on your dive or snorkel — no special equipment needed.',
  },
  {
    icon: '🤖',
    title: '2. Gemini Vision analyzes it',
    body: 'Our AI classifies coral health in seconds: Healthy, Partially Bleached, Severely Bleached, or Dead.',
  },
  {
    icon: '🌊',
    title: '3. Get a risk-scored report',
    body: 'Weather, sea temperature, and a coral risk score are combined into a shareable PDF and map pin.',
  },
]

export default function Home() {
  const [survey, setSurvey] = useState(null)
  const uploadRef = useRef(null)

  function scrollToUpload() {
    uploadRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  return (
    <div className="space-y-16">
      <section className="text-center">
        <span className="inline-flex items-center rounded-full bg-ocean-100 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-ocean-700">
          AI-powered reef monitoring
        </span>
        <h1 className="mx-auto mt-4 max-w-2xl text-4xl font-extrabold tracking-tight text-ocean-900 sm:text-5xl">
          Every dive photo can help save a reef.
        </h1>
        <p className="mx-auto mt-4 max-w-xl text-lg text-slate-600">
          Upload an underwater coral photo and get an instant AI health assessment, environmental
          context, and a shareable report — pinned on a live map for researchers to track.
        </p>
        <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
          <button
            onClick={scrollToUpload}
            className="rounded-lg bg-ocean-700 px-6 py-3 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-ocean-800"
          >
            Survey a reef now
          </button>
          <Link
            to="/about"
            className="rounded-lg border border-slate-300 bg-white px-6 py-3 text-sm font-semibold text-slate-700 shadow-sm transition-colors hover:border-ocean-400 hover:text-ocean-800"
          >
            The science behind it
          </Link>
        </div>
      </section>

      <section className="grid gap-6 sm:grid-cols-3">
        {STEPS.map((step) => (
          <div key={step.title} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="text-3xl">{step.icon}</div>
            <h3 className="mt-3 font-semibold text-ocean-900">{step.title}</h3>
            <p className="mt-1 text-sm text-slate-500">{step.body}</p>
          </div>
        ))}
      </section>

      <section ref={uploadRef} className="scroll-mt-20 space-y-6">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-ocean-900">Survey a Coral Reef</h2>
          <p className="mt-1 text-slate-500">Drop in a photo below to get started.</p>
        </div>

        <div className="mx-auto max-w-xl">
          <UploadCard onResult={setSurvey} />
        </div>

        {survey && (
          <div className="mx-auto max-w-3xl">
            <ResultCard survey={survey} />
          </div>
        )}
      </section>
    </div>
  )
}
