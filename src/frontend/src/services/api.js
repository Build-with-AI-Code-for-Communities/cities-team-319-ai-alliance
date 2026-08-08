import axios from 'axios'

export const api = axios.create({
  baseURL: '/api',
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
export async function analyzeImage({ imageName, latitude, longitude }) {
  const { data } = await api.post('/analyze', {
    image_name: imageName,
    latitude,
    longitude,
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
  return `/api/report/${surveyId}/download`
}
