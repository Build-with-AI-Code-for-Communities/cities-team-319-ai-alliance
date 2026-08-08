import axios from 'axios'

// In local dev this stays '/api' and vite.config.js proxies it to localhost:8000.
// In production (e.g. Vercel), set VITE_API_BASE_URL to the deployed backend's
// full API URL (e.g. https://coral-ai-backend.onrender.com/api) at build time —
// Vercel and Render are different origins, so a relative path won't reach it.
const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api'

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
})

/** Upload a raw image file. Returns { image_name, latitude, longitude, message }. */
export async function uploadImage(file) {
  const formData = new FormData()
  formData.append('file', file)

  const { data } = await api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

/** Run the full analysis pipeline on a previously-uploaded image. */
export async function analyzeImage({ imageName, latitude, longitude, submittedBy }) {
  const { data } = await api.post('/analyze', {
    image_name: imageName,
    latitude,
    longitude,
    submitted_by: submittedBy || null,
  })
  return data
}

/** Fetch paginated list of past surveys. */
export async function fetchSurveys({ limit = 50, offset = 0 } = {}) {
  const { data } = await api.get('/dashboard/surveys', { params: { limit, offset } })
  return data
}

/** Fetch aggregate classification counts for the dashboard header. */
export async function fetchStats() {
  const { data } = await api.get('/dashboard/stats')
  return data
}

/** Fetch a single survey by ID. */
export async function fetchSurvey(surveyId) {
  const { data } = await api.get(`/dashboard/surveys/${surveyId}`)
  return data
}

/** Generate a PDF report for a survey, then return its download URL. */
export async function generateReport(surveyId) {
  await api.post(`/report/${surveyId}`)
  return `${API_BASE}/report/${surveyId}/download`
}
