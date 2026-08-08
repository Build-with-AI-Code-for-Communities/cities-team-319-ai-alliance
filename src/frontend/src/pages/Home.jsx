import { useState } from 'react'

import ResultCard from '../components/ResultCard.jsx'
import UploadCard from '../components/UploadCard.jsx'

export default function Home() {
  const [survey, setSurvey] = useState(null)

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-ocean-900">Survey a Coral Reef</h1>
        <p className="mt-2 text-slate-500">
          Upload an underwater photo to get an instant AI-powered health assessment.
        </p>
      </div>

      <div className="mx-auto max-w-xl">
        <UploadCard onResult={setSurvey} />
      </div>

      {survey && (
        <div className="mx-auto max-w-3xl">
          <ResultCard survey={survey} />
        </div>
      )}
    </div>
  )
}
