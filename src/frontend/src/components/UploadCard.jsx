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
        const survey = await analyzeImage({ imageName: uploaded.image_name, latitude, longitude })

        toast.success(`Classified: ${survey.classification}`)
        onResult(survey)
      } catch (err) {
        const message = err.response?.data?.detail || 'Upload failed. Please try again.'
        toast.error(message)
      } finally {
        setStage('idle')
      }
    },
    [onResult],
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/jpeg': [], 'image/png': [], 'image/webp': [] },
    maxFiles: 1,
    disabled: stage !== 'idle',
  })

  const busy = stage !== 'idle'

  return (
    <div
      {...getRootProps()}
      className={`flex min-h-[280px] cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed p-8 text-center transition-colors ${
        isDragActive ? 'border-ocean-500 bg-ocean-50' : 'border-slate-300 bg-white hover:border-ocean-400'
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
            Drag & drop an underwater coral photo here
          </p>
          <p className="mt-1 text-sm text-slate-400">or click to browse (JPEG, PNG, WEBP — max 10MB)</p>
        </>
      )}
    </div>
  )
}
