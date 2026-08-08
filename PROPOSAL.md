# Architecture Proposal

> Fill this out and commit it by **Friday, July 24 · 11:59 PM IST**. This file *is*
> your Ideation-Phase submission — no separate form. Keep it living; update it as
> your design evolves.

- **Team name:** AI Alliance
- **Team code:** team-319
- **Track:** Sustainable Cities & Climate Action
- **Members:** Prince T Philip (@psycho-prince), Anujan, Vishalakshi

## 1. Problem
Coral reefs support ~25% of all marine species and protect coastlines for over 500 million people, yet they're dying at an alarming rate from ocean warming, pollution, and acidification. Bleaching events — where corals expel their symbiotic algae and turn white — are a leading indicator of reef stress, but tracking them at scale requires trained marine biologists, consistent geotagged documentation, and correlation with environmental data. This process is slow and expensive, and doesn't scale to the thousands of reef sites worldwide that need monitoring — while divers and snorkelers take thousands of reef photos every day that go unanalyzed.

## 2. Who it helps
Field volunteers and citizen scientists (divers, snorkelers, dive shop staff) who want to contribute to conservation with photos they're already taking; marine researchers & NGOs who need aggregated, geotagged bleaching data without funding manual surveys everywhere; and educators teaching coral health concepts with instant, visual feedback.

## 3. Proposed solution
**CoralAI** turns any smartphone photo of a coral reef into an instant, structured health assessment. A volunteer photographs coral with our web app; within seconds, the system validates and resizes the image, uses Gemini Vision to classify coral health (Healthy / Partially Bleached / Severely Bleached / Dead Coral), cross-references real-time weather and sea temperature for that location, computes a simple Coral Risk Score, and generates a shareable PDF report pinned on a public map dashboard.

## 4. High-level architecture
_Key components and how data flows. A diagram is welcome (drop an image in `/docs`)._

```
React PWA (Vite + Tailwind + Leaflet)
        │  upload photo (multipart)
        ▼
FastAPI backend (src/backend) — routes → services → models
        │
        ├─▶ Gemini Vision API        (coral health classification, forced JSON)
        ├─▶ Open-Meteo API           (weather + marine/SST, no key needed)
        ├─▶ NASA POWER API           (satellite SST — optional, graceful fallback)
        ├─▶ Coral Risk Engine        (classification + temperature → risk score)
        ├─▶ ReportLab                (one-page PDF report, in-memory)
        │
        ▼
SQLite (dev) / PostgreSQL via Neon (prod)   +   local disk (dev) / S3-compatible
   tables: surveys, reports                     object storage via Cloudflare R2 (prod)
```

## 5. Tech stack
- **Frontend:** React 18, Vite, Tailwind CSS, React Router, TanStack Query, Axios, React Dropzone, React Leaflet, React Hot Toast
- **Backend:** FastAPI, Pydantic v2, SQLAlchemy 2.0, Pillow, ReportLab, httpx, boto3
- **AI:** Google Gemini Vision (`gemini-2.0-flash`)
- **Data:** Open-Meteo (weather + marine/SST, no key), NASA POWER API (SST, optional)
- **Database:** SQLite (local) / PostgreSQL via Neon (production)
- **Storage:** local disk (dev) / S3-compatible object storage via Cloudflare R2 (production)
- **Infra:** Render (backend), Vercel (frontend), GitHub Actions CI

## 6. Milestones to hackathon day
- [x] Backend (FastAPI) — clean architecture, Gemini Vision pipeline, weather/risk engine, PDF reports
- [x] Frontend (React) — upload flow, results view, map, dashboard
- [x] Object storage + managed Postgres wiring for production hosting (Render free tier)
- [ ] Deploy backend to Render + frontend to Vercel
- [ ] Live demo run-through with real coral photos
- [ ] Talk to a real diver/snorkeler or reef conservation volunteer about the workflow

## 7. Open questions / help needed
- Looking for mentor feedback on the simple Coral Risk Engine (classification + temperature thresholds) — is there a better lightweight signal we're missing before hackathon judging?
- Interested in connecting with a real marine conservation volunteer or dive shop to validate the classification UX before the final demo.
