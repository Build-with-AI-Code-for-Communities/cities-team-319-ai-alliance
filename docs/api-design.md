# API Design

Base URL (local): `http://localhost:8000/api`. Interactive docs (Swagger UI) are always available at `http://localhost:8000/docs`.

All error responses follow FastAPI's standard shape:

```json
{ "detail": "Human-readable error message." }
```

---

## `POST /api/upload`

Validate, resize, and store an image; extract GPS from EXIF if present.

**Request:** `multipart/form-data`

| Field | Type | Description |
|---|---|---|
| `file` | file | JPEG/PNG/WEBP, max 25MB |

**Response `201`:**

```json
{
  "image_name": "3f9a1b2c4d5e6f70.jpg",
  "latitude": 21.2812,
  "longitude": -86.9084,
  "message": "Image uploaded and processed successfully."
}
```

**Errors:** `400` — unsupported type, file too large, or empty file.

---

## `POST /api/analyze`

Run the full pipeline (Gemini classification + weather + risk engine) on a previously uploaded image and persist the result.

**Request body:**

```json
{
  "image_name": "3f9a1b2c4d5e6f70.jpg",
  "latitude": 21.2812,
  "longitude": -86.9084
}
```

`latitude`/`longitude` are optional — omit if unknown (e.g., browser geolocation also denied); weather/risk fields will be `null`.

**Response `201`:**

```json
{
  "id": 1,
  "image_name": "3f9a1b2c4d5e6f70.jpg",
  "latitude": 21.2812,
  "longitude": -86.9084,
  "classification": "Partially Bleached",
  "severity": "Moderate",
  "confidence": 78,
  "possible_cause": "Elevated sea surface temperature consistent with thermal stress.",
  "recommendation": "Monitor weekly; report to local marine authority if bleaching progresses.",
  "risk_level": "High",
  "risk_score": 60,
  "temperature": 30.1,
  "weather": {
    "temperature_c": 29.4,
    "wind_speed_kmh": 14.2,
    "weather_code": 1,
    "sea_surface_temperature_c": 30.1,
    "source": "open-meteo"
  },
  "created_at": "2026-08-06T10:32:00Z"
}
```

**Errors:** `404` — `image_name` not found (upload it first via `/api/upload`).

---

## `POST /api/report/{survey_id}`

Generate a one-page PDF report for a survey.

**Response `201`:**

```json
{
  "id": 1,
  "survey_id": 1,
  "pdf_path": "reports/survey_1_report.pdf",
  "created_at": "2026-08-06T10:33:00Z"
}
```

**Errors:** `404` — survey not found.

---

## `GET /api/report/{survey_id}/download`

Download the most recently generated PDF for a survey. Behavior depends on `STORAGE_BACKEND`:

- **`local`** (default): streams the PDF directly (`200`, `application/pdf`).
- **`s3`**: `307` redirect to a short-lived presigned URL (expires after `S3_PRESIGNED_URL_EXPIRY_SECONDS`, default 1 hour).

**Errors:** `404` — survey not found, or no report generated yet (call `POST /api/report/{survey_id}` first).

---

## `GET /api/dashboard/surveys`

List past surveys, most recent first.

**Query params:** `limit` (default 50, max 200), `offset` (default 0)

**Response `200`:** array of the same shape as the `/api/analyze` response.

---

## `GET /api/dashboard/surveys/{survey_id}`

Fetch a single survey by ID. Same response shape as above. `404` if not found.

---

## `GET /api/dashboard/stats`

Aggregate classification counts across all surveys, used for the dashboard header.

**Response `200`:**

```json
{
  "total_surveys": 42,
  "healthy": 12,
  "partially_bleached": 15,
  "severely_bleached": 9,
  "dead_coral": 4,
  "unknown": 2
}
```

---

## `GET /health`

Liveness check (outside `/api` prefix). Returns `{ "status": "healthy" }`.
