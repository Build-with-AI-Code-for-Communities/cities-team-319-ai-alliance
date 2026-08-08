# Architecture

## Overview

CoralAI follows a classic three-tier architecture: a React SPA/PWA frontend, a FastAPI backend organized as **routes → services → models**, and a relational database (SQLite locally, PostgreSQL in production).

```
┌───────────────────────────────────────────────────────────────────────┐
│                              Frontend (React)                          │
│  Home (upload) ──▶ UploadCard ──▶ api.js ──▶ Dashboard ──▶ MapView     │
└──────────────────────────────┬──────────────────────────────────────┘
                                 │ REST (JSON / multipart)
┌──────────────────────────────▼──────────────────────────────────────┐
│                          FastAPI Backend                              │
│                                                                        │
│  api/upload.py  ──▶ utils/image_processing.py, utils/gps.py           │
│                 ──▶ services/storage_service.py                       │
│  api/analyze.py ──▶ services/storage_service.py (read image bytes)    │
│                 ──▶ services/gemini_service.py                        │
│                 ──▶ services/weather_service.py                       │
│                 ──▶ services/nasa_service.py (optional)               │
│                 ──▶ risk engine (in analyze.py)                       │
│                 ──▶ models/survey.py ──▶ database.py                  │
│  api/report.py  ──▶ services/report_service.py                       │
│                 ──▶ services/storage_service.py ──▶ models/report.py  │
│  api/dashboard.py ──▶ models/survey.py (read)                         │
└──────────────────────────────┬──────────────────────────────────────┘
                    │ SQLAlchemy ORM         │ storage_service (local disk or S3)
┌──────────────────▼───────────┐  ┌─────────▼──────────────────────────┐
│ SQLite (dev) / PostgreSQL(Neon)│  │ Local disk (dev) / S3-compatible   │
│ tables: surveys, reports       │  │ bucket, e.g. Cloudflare R2 (prod)  │
└─────────────────────────────────┘  └─────────────────────────────────┘
```

## Layering Principle

- **`api/`** — HTTP concerns only: request parsing, validation via Pydantic, calling services, shaping responses. No business logic.
- **`services/`** — all business logic and third-party integrations (Gemini, Open-Meteo, NASA, PDF generation, object storage). Pure functions/async functions that don't know about HTTP.
- **`models/`** — SQLAlchemy ORM models, the persistence shape of the domain.
- **`utils/`** — cross-cutting helpers (image processing, GPS extraction, logging) with no dependency on `api/` or `services/`.

`services/storage_service.py` is a deliberate seam: it exposes `save()`/`read()`/`exists()` behind one interface backed by either local disk (`STORAGE_BACKEND=local`, the default) or any S3-compatible bucket (`STORAGE_BACKEND=s3` — AWS S3, Cloudflare R2, MinIO). Every other module reads/writes images and PDFs through a storage *key* (e.g. `uploads/<uuid>.jpg`) and never touches a filesystem path directly, so switching backends for production is a config change, not a code change.

This keeps each layer independently testable and lets services be reused (e.g., the CLI or a batch job could call `gemini_service.analyze_coral_image` directly without going through FastAPI).

## End-to-End Data Flow

1. **Upload** (`POST /api/upload`) — client sends a multipart image. The backend validates type/size, extracts GPS from EXIF *before* the destructive resize (Pillow strips EXIF on save), auto-orients and downsamples it with Pillow entirely in memory, then persists the result via `storage_service.save()` under a key like `uploads/<uuid>.<ext>` — either a local file or an S3-compatible object, depending on `STORAGE_BACKEND`. The response returns that key as `image_name`.
2. **Analyze** (`POST /api/analyze`) — client sends `{ image_name, latitude, longitude }`. The backend:
   - Reads the image bytes back via `storage_service.read(image_name)` (404s if the key doesn't exist).
   - Calls `gemini_service.analyze_coral_image()` with the exact hardcoded marine-biologist prompt, parses the forced-JSON response, and validates the classification against the fixed enum.
   - Calls `weather_service.fetch_weather()` (Open-Meteo forecast + marine APIs) for air temperature, wind, and sea surface temperature.
   - Optionally calls `nasa_service.fetch_nasa_sst()` if `NASA_SST_ENABLED=true`, overlaying satellite SST when available.
   - Runs the **Coral Risk Engine**: combines the classification's base severity score with temperature thresholds (`RISK_TEMP_WARNING_C`, `RISK_TEMP_CRITICAL_C`) into a 0–100 risk score and a Low/Moderate/High/Critical label.
   - Persists a `Survey` row and returns it.
3. **Report** (`POST /api/report/{survey_id}` then `GET /api/report/{survey_id}/download`) — `report_service.generate_survey_report()` renders a one-page PDF via ReportLab into memory and persists it via `storage_service.save()` under `reports/survey_<id>_report.pdf`, tracked as a `Report` row. On download, the local backend streams the file directly; the S3 backend 307-redirects to a short-lived presigned URL.
4. **Dashboard** (`GET /api/dashboard/surveys`, `GET /api/dashboard/stats`) — read-only endpoints backing the React dashboard's table and map.

## Graceful Degradation

Every external integration is designed to degrade rather than fail the request:

- No `GEMINI_API_KEY` → classification falls back to `"Unknown"` with a safe recommendation, instead of raising.
- Weather/marine API failures → fields return `null`, logged as warnings.
- NASA SST disabled/unreachable → silently skipped, Open-Meteo marine SST is used instead.
- Ocean Color / OBIS (Tier 3) → not implemented, explicitly stubbed and documented as such.
