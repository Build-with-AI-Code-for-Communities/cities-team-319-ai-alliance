# 🪸 CoralAI — AI Alliance (team-319) · Tech for Good 2026:https://cities-team-319-ai-alliance.vercel.app/

**AI-powered coral bleaching detection for field volunteers and marine researchers.**

Upload an underwater reef photo → get an instant AI health assessment, environmental context, and a shareable PDF report — all pinned on a live map.

Built for **Build with AI: Code for Communities** — GDG Coimbatore (Aug 8–9, 2026, GRD College), track: *Sustainable Cities & Climate Action*. See [`PROPOSAL.md`](PROPOSAL.md) for the full submission and [`MILESTONES.md`](MILESTONES.md) for live progress.

[![Backend CI](https://github.com/Build-with-AI-Code-for-Communities/cities-team-319-ai-alliance/actions/workflows/backend.yml/badge.svg)](.github/workflows/backend.yml)
[![Frontend CI](https://github.com/Build-with-AI-Code-for-Communities/cities-team-319-ai-alliance/actions/workflows/frontend.yml/badge.svg)](.github/workflows/frontend.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Problem & Solution

Coral reefs are dying faster than researchers can survey them manually. CoralAI lets any volunteer with a smartphone photo contribute a structured, geotagged health assessment in seconds — powered by Gemini Vision instead of a marine biologist's field trip.

## How It Works

1. A volunteer photographs coral underwater and uploads it via the React PWA.
2. The backend validates and resizes the image, and extracts GPS from EXIF (with a browser-geolocation fallback).
3. **Gemini Vision** classifies the coral's health as `Healthy`, `Partially Bleached`, `Severely Bleached`, `Dead Coral`, or `Unknown`.
4. **Open-Meteo** (and optionally **NASA SST**) supply real-time weather and sea temperature for that location.
5. A simple **Coral Risk Engine** combines the classification and temperature into a Low/Moderate/High/Critical risk score.
6. The result is stored, rendered as a one-page **PDF report** (ReportLab), and shown on a **Leaflet map dashboard**.

## Architecture

```
┌─────────────────┐        ┌──────────────────────────────────────────────┐
│   React PWA      │  HTTP  │                FastAPI Backend                │
│  (Vite + Tailwind)│──────▶│  api/  →  services/  →  models/  →  database │
│  Upload · Dashboard│◀──────│                                                │
└─────────────────┘        │  ┌─────────────┐  ┌──────────────┐            │
                            │  │ Gemini Vision│  │ Open-Meteo   │            │
                            │  │  (classify)  │  │ (weather/SST)│            │
                            │  └─────────────┘  └──────────────┘            │
                            │  ┌─────────────┐  ┌──────────────┐            │
                            │  │ NASA SST     │  │ Coral Risk   │            │
                            │  │ (Tier 2)     │  │ Engine       │            │
                            │  └─────────────┘  └──────────────┘            │
                            │            │                                   │
                            │            ▼                                   │
                            │   SQLite (dev) / PostgreSQL via Neon (prod)    │
                            │            │                                   │
                            │            ▼                                   │
                            │  ReportLab PDF → local disk / S3 (R2) storage  │
                            └──────────────────────────────────────────────┘
```

See [`docs/architecture.md`](docs/architecture.md) for the detailed data flow and [`docs/ai-pipeline.md`](docs/ai-pipeline.md) for the Gemini prompt design.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, Tailwind CSS, React Router, TanStack Query, Axios, React Dropzone, React Leaflet, React Hot Toast |
| Backend | FastAPI, Pydantic v2 / pydantic-settings, SQLAlchemy 2.0, Pillow, ReportLab, httpx, boto3 |
| AI | Google Gemini Vision (`gemini-2.0-flash`) |
| Data | Open-Meteo (weather + marine/SST, no key), NASA POWER API (SST, optional) |
| Database | SQLite (local) / PostgreSQL via Neon (production) |
| Storage | Local disk (dev) / S3-compatible object storage via Cloudflare R2 (production) |
| Infra | Render (backend), Vercel (frontend), GitHub Actions CI |

## Repository Structure

```
.
├── PROPOSAL.md         # Ideation-phase submission
├── MILESTONES.md       # Live hackathon progress checklist
├── src/
│   ├── backend/        # FastAPI app (routes → services → models)
│   └── frontend/       # React + Vite PWA
├── docs/                # Architecture, API, DB, deployment, AI pipeline docs
├── assets/              # Screenshots & demo media
└── .github/             # CI workflows & issue templates
```

## Installation

### Prerequisites

- Python 3.11+
- Node.js 18+
- (Optional) Docker, for local PostgreSQL instead of SQLite

### 1. Clone and configure environment variables

```bash
git clone https://github.com/Build-with-AI-Code-for-Communities/cities-team-319-ai-alliance.git
cd cities-team-319-ai-alliance
cp .env.example src/backend/.env
```

Edit `src/backend/.env` and set at minimum:

```bash
GEMINI_API_KEY=your-gemini-api-key   # required — get one free at https://aistudio.google.com/apikey
```

Everything else (Open-Meteo, Leaflet/OpenStreetMap) works with **no API key**. NASA SST is optional (Tier 2) and gracefully falls back to Open-Meteo marine data if left unset.

### 2. Run the backend

```bash
cd src/backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API is now live at `http://localhost:8000`, with interactive docs at `http://localhost:8000/docs`.

### 3. Run the frontend

```bash
cd src/frontend
npm install
npm run dev
```

The app is now live at `http://localhost:5173` (proxies `/api` to the backend).

### 4. (Optional) Run PostgreSQL locally instead of SQLite

```bash
docker compose up -d postgres
# then set in src/backend/.env:
# DATABASE_URL=postgresql://coral:coral@localhost:5432/coral_ai
```

### 5. (Optional) Use object storage instead of local disk

By default, uploaded images and generated PDFs are written to `src/backend/uploads/` and `src/backend/reports/`. For production hosts with an ephemeral filesystem (e.g. Render's free tier), switch to S3-compatible object storage — works with AWS S3, MinIO, or Cloudflare R2 (free 10GB tier):

```bash
# src/backend/.env
STORAGE_BACKEND=s3
S3_ENDPOINT_URL=https://<account_id>.r2.cloudflarestorage.com   # blank for AWS S3
S3_REGION=auto                                                   # R2 uses "auto"
S3_BUCKET_NAME=coral-ai
S3_ACCESS_KEY_ID=...
S3_SECRET_ACCESS_KEY=...
```

No code changes needed — `app/services/storage_service.py` abstracts both backends behind the same interface. See [`docs/deployment.md`](docs/deployment.md) for the full Render + Neon + R2 setup.

## API Keys Reference

| Variable | Required? | Where to get it |
|---|---|---|
| `GEMINI_API_KEY` | **Yes** (Tier 1) | https://aistudio.google.com/apikey |
| `NASA_API_KEY` / `NASA_SST_ENABLED` | No (Tier 2) | https://api.nasa.gov — leave unset to skip |
| `S3_*` (object storage) | No (defaults to local disk) | https://dash.cloudflare.com/?to=/:account/r2 for Cloudflare R2's free tier |

No key is required for Open-Meteo (weather/marine data) or Leaflet/OpenStreetMap (maps).

## API Documentation

Full endpoint reference with request/response examples: [`docs/api-design.md`](docs/api-design.md). Interactive Swagger UI is also available at `/docs` once the backend is running.

## Database Schema

See [`docs/database.md`](docs/database.md) for the full ER diagram. Summary:

- **Survey**: `id, image_name, latitude, longitude, classification, severity, confidence, temperature, weather (JSON), recommendation, created_at`
- **Report**: `id, survey_id, pdf_path, created_at`

## Screenshots

> Add screenshots to `assets/screenshots/` before submission.

| Upload | Result | Dashboard |
|---|---|---|
| `assets/screenshots/upload.png` | `assets/screenshots/result.png` | `assets/screenshots/dashboard.png` |

## Deployment

Production deployment: **Vercel** (frontend) + **Render** (backend) + **Neon** (PostgreSQL) + **Cloudflare R2** (object storage). See [`docs/deployment.md`](docs/deployment.md) for the full step-by-step plan, including the exact Render env vars and one-click `render.yaml` blueprint at the repo root.

## Future Work

- Human-in-the-loop verification to build a labeled training dataset from volunteer submissions
- Historical trend tracking per reef site with bleaching-event timelines
- Push notifications when a monitored site's risk score spikes
- NASA Ocean Color (chlorophyll-a) and OBIS biodiversity integrations (currently stubbed — see `src/backend/app/services/ocean_color_service.py` and `obis_service.py`)
- Offline-first PWA support for dive sites with no connectivity

## License

[MIT](LICENSE)
