import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import toast from 'react-hot-toast'

import { analyzeImage, uploadImage } from '../services/api.js'

const MAX_UPLOAD_MB = 25

const STAGES = [
  { key: 'uploading', label: 'Uploading photo' },
  { key: 'analyzing', label: 'Analyzing with Gemini Vision' },
]

/** Fall back to browser geolocation when the image has no EXIF GPS data. */
function getBrowserLocation() {
  return new Promise((resolve) => {
    if (!navigator.geolocation) {
      resolve({ latitude: null, longitude: null })
      return
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => resolve({ latitude: pos.coords.latitude, longitude: pos.coords.longitude }),
      () => resolve({ latitude: null, longitude: null }),
      { timeout: 5000 },
    )
  })
}

function StageTracker({ stage }) {
  const activeIndex = STAGES.findIndex((s) => s.key === stage)
  return (
    <div className="flex flex-col items-center gap-5 py-4">
      <div className="h-12 w-12 animate-spin rounded-full border-4 border-ocean-200 border-t-ocean-600" />
      <div className="flex items-center gap-2 text-sm">
        {STAGES.map((s, i) => (
          <div key={s.key} className="flex items-center gap-2">
            <span
              className={`flex h-6 w-6 items-center justify-center rounded-full text-xs font-semibold ${
                i < activeIndex
                  ? 'bg-emerald-500 text-white'
                  : i === activeIndex
                    ? 'bg-ocean-600 text-white'
                    : 'bg-slate-200 text-slate-400'
              }`}
            >
              {i < activeIndex ? '✓' : i + 1}
            </span>
            <span className={i === activeIndex ? 'font-medium text-ocean-800' : 'text-slate-400'}>{s.label}</span>
            {i < STAGES.length - 1 && <span className="mx-1 h-px w-6 bg-slate-200" />}
          </div>
        ))}
      </div>
    </div>
  )
}

export default function UploadCard({ onResult }) {
  const [preview, setPreview] = useState(null)
  const [stage, setStage] = useState('idle') // idle | uploading | analyzing
  const [submittedBy, setSubmittedBy] = useState('')
  const [manualLat, setManualLat] = useState('')
  const [manualLon, setManualLon] = useState('')

  const onDrop = useCallback(
    async (acceptedFiles) => {
      const file = acceptedFiles[0]
      if (!file) return

      setPreview(URL.createObjectURL(file))

      try {
        setStage('uploading')
        const uploaded = await uploadImage(file)

        let { latitude, longitude } = uploaded
        const hasManualLocation = manualLat.trim() !== '' && manualLon.trim() !== ''

        if (hasManualLocation) {
          latitude = parseFloat(manualLat)
          longitude = parseFloat(manualLon)
        } else if (latitude == null || longitude == null) {
          const browserLocation = await getBrowserLocation()
          latitude = browserLocation.latitude
          longitude = browserLocation.longitude
        }

        setStage('analyzing')
        const survey = await analyzeImage({
          imageName: uploaded.image_name,
          latitude,
          longitude,
          submittedBy,
        })

        toast.success(`Classified: ${survey.classification}`)
        onResult(survey)
      } catch (err) {
        const message = err.response?.data?.detail || 'Upload failed. Please try again.'
        toast.error(message)
      } finally {
        setStage('idle')
      }
    },
    [onResult, submittedBy, manualLat, manualLon],
  )

  const onDropRejected = useCallback((rejections) => {
    const reason = rejections[0]?.errors?.[0]
    if (reason?.code === 'file-too-large') {
      toast.error(`File is too large. Max allowed is ${MAX_UPLOAD_MB}MB.`)
    } else if (reason?.code === 'file-invalid-type') {
      toast.error('Unsupported file type. Please upload a JPEG, PNG, or WEBP photo.')
    } else {
      toast.error('Could not accept this file. Please try another photo.')
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    onDrop,
    onDropRejected,
    accept: { 'image/jpeg': [], 'image/png': [], 'image/webp': [] },
    maxFiles: 1,
    maxSize: MAX_UPLOAD_MB * 1024 * 1024,
    disabled: stage !== 'idle',
    noClick: true,
    noKeyboard: true,
  })

  const busy = stage !== 'idle'

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-100 bg-gradient-to-r from-ocean-50 to-white px-6 py-5">
        <h3 className="text-lg font-bold text-ocean-900">Submit a Reef Survey</h3>
        <p className="mt-0.5 text-sm text-slate-500">
          Gemini Vision, live sea temperature, and NOAA heat-stress data combine into an instant
          coral health risk assessment.
        </p>
      </div>

      <div className="grid md:grid-cols-2">
        <div
          {...getRootProps()}
          className={`flex min-h-[320px] flex-col items-center justify-center border-b border-slate-100 p-8 text-center transition-colors md:border-b-0 md:border-r ${
            isDragActive ? 'bg-ocean-50' : 'bg-white'
          }`}
        >
          <input {...getInputProps()} />

          {busy ? (
            <StageTracker stage={stage} />
          ) : preview ? (
            <div className="w-full">
              <img src={preview} alt="Preview" className="mx-auto max-h-48 rounded-xl object-cover shadow" />
              <button
                type="button"
                onClick={open}
                className="mt-4 text-sm font-medium text-ocean-700 hover:underline"
              >
                Choose a different photo
              </button>
            </div>
          ) : (
            <>
              <div
                className={`flex h-16 w-16 items-center justify-center rounded-full text-3xl transition-colors ${
                  isDragActive ? 'bg-ocean-200' : 'bg-ocean-100'
                }`}
              >
                🐠
              </div>
              <p className="mt-4 text-base font-semibold text-slate-700">
                {isDragActive ? 'Drop it here' : 'Drag & drop a coral photo'}
              </p>
              <p className="mt-1 text-sm text-slate-400">or</p>
              <button
                type="button"
                onClick={open}
                className="mt-4 rounded-lg bg-ocean-700 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-ocean-800"
              >
                Choose a photo
              </button>
              <p className="mt-3 text-xs text-slate-400">JPEG, PNG, or WEBP — max {MAX_UPLOAD_MB}MB</p>
            </>
          )}
        </div>

        <div className="space-y-4 p-6">
          <div>
            <label htmlFor="submitted-by" className="block text-sm font-medium text-slate-700">
              Your name <span className="font-normal text-slate-400">(optional)</span>
            </label>
            <input
              id="submitted-by"
              type="text"
              value={submittedBy}
              onChange={(e) => setSubmittedBy(e.target.value)}
              disabled={busy}
              placeholder="e.g. Jamie Rivera"
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-800 shadow-sm focus:border-ocean-500 focus:outline-none focus:ring-1 focus:ring-ocean-500 disabled:opacity-50"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700">
              Reef location <span className="font-normal text-slate-400">(optional — overrides photo GPS)</span>
            </label>
            <div className="mt-1 grid grid-cols-2 gap-2">
              <input
                type="number"
                step="any"
                value={manualLat}
                onChange={(e) => setManualLat(e.target.value)}
                disabled={busy}
                placeholder="Latitude e.g. 9.0"
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-800 shadow-sm focus:border-ocean-500 focus:outline-none focus:ring-1 focus:ring-ocean-500 disabled:opacity-50"
              />
              <input
                type="number"
                step="any"
                value={manualLon}
                onChange={(e) => setManualLon(e.target.value)}
                disabled={busy}
                placeholder="Longitude e.g. 79.3"
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-800 shadow-sm focus:border-ocean-500 focus:outline-none focus:ring-1 focus:ring-ocean-500 disabled:opacity-50"
              />
            </div>
            <p className="mt-1 text-xs text-slate-400">
              Leave blank to use the photo&apos;s embedded GPS, or your device location as a fallback.
            </p>
          </div>

          <div className="rounded-xl bg-slate-50 p-4 text-xs text-slate-500">
            <p className="font-semibold text-slate-600">What happens next</p>
            <ul className="mt-1.5 space-y-1">
              <li>• Gemini Vision classifies bleaching severity</li>
              <li>• Live sea temperature + NOAA heat-stress data are pulled for your coordinates</li>
              <li>• A shareable PDF report and map pin are generated instantly</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
