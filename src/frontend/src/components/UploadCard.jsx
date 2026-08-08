import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import toast from 'react-hot-toast'

import { analyzeImage, uploadImage } from '../services/api.js'
import Loader from './Loader.jsx'

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

export default function UploadCard({ onResult }) {
  const [preview, setPreview] = useState(null)
  const [stage, setStage] = useState('idle') // idle | uploading | analyzing
  const [submittedBy, setSubmittedBy] = useState('')

  const onDrop = useCallback(
    async (acceptedFiles) => {
      const file = acceptedFiles[0]
      if (!file) return

      setPreview(URL.createObjectURL(file))

      try {
        setStage('uploading')
        const uploaded = await uploadImage(file)

        let { latitude, longitude } = uploaded
        if (latitude == null || longitude == null) {
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
    [onResult, submittedBy],
  )

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    onDrop,
    accept: { 'image/jpeg': [], 'image/png': [], 'image/webp': [] },
    maxFiles: 1,
    disabled: stage !== 'idle',
    noClick: true,
    noKeyboard: true,
  })

  const busy = stage !== 'idle'

  return (
    <div className="space-y-4">
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

      <div
        {...getRootProps()}
        className={`flex min-h-[280px] flex-col items-center justify-center rounded-2xl border-2 border-dashed p-8 text-center transition-colors ${
          isDragActive ? 'border-ocean-500 bg-ocean-50' : 'border-slate-300 bg-white'
        }`}
      >
        <input {...getInputProps()} />

        {busy ? (
          <Loader label={stage === 'uploading' ? 'Uploading image...' : 'Analyzing coral health with Gemini...'} />
        ) : preview ? (
          <img src={preview} alt="Preview" className="max-h-52 rounded-lg object-cover shadow" />
        ) : (
          <>
            <p className="text-4xl">🐠</p>
            <p className="mt-3 text-base font-medium text-slate-700">
              Drag &amp; drop an underwater coral photo here
            </p>
            <p className="mt-1 text-sm text-slate-400">or</p>
          </>
        )}

        {!busy && (
          <button
            type="button"
            onClick={open}
            className="mt-4 rounded-lg bg-ocean-700 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-ocean-800"
          >
            Choose a photo
          </button>
        )}
        {!busy && <p className="mt-2 text-xs text-slate-400">JPEG, PNG, or WEBP — max 10MB</p>}
      </div>
    </div>
  )
}
