# Deployment Plan

Target stack: **Vercel** (frontend) + **Render free tier** (backend) + **Neon** (managed PostgreSQL). Object storage (Cloudflare R2 or similar) is optional — see below.

Render's free web services are ideal for a hackathon budget, but come with two constraints this plan works around:

- **No persistent disk** — the local filesystem is wiped on every redeploy and periodically on restart. SQLite and local `uploads/`/`reports/` don't survive this.
- **Spins down after 15 min idle** — the first request after idle takes ~30-50s to cold-start. Nothing to fix here; just expect it in a demo.

Neon solves the first problem for the database. The second (uploaded images and generated PDFs not surviving a redeploy) only matters if you need those specific files to persist long-term — **survey data itself (classification, risk score, weather, everything the dashboard shows) is safe in Neon either way.** For a hackathon demo, it's reasonable to skip object storage entirely and accept that files reset on redeploy (which won't happen mid-demo). `render.yaml` defaults to this (`STORAGE_BACKEND=local`) so there's nothing to configure.

## 1. Database — Neon (free Postgres)

1. Create a free project at https://neon.tech.
2. Copy the connection string (looks like `postgresql://user:password@ep-xxxx.neon.tech/coral_ai?sslmode=require`).
3. This becomes `DATABASE_URL` for the backend service below. SQLAlchemy + `psycopg2-binary` (already in `requirements.txt`) handle the rest — no code changes needed.
4. Treat this connection string as a secret: paste it only into Render's environment variable dashboard, never into a file that gets committed, a chat, or a public channel. If it's ever been pasted somewhere it shouldn't have, reset the password from the Neon dashboard (Settings → Reset password) — takes seconds and immediately invalidates the old one.

## 2. Object Storage (optional) — Cloudflare R2, Backblaze B2, or skip it

The backend's storage layer (`src/backend/app/services/storage_service.py`) supports any S3-compatible provider via `STORAGE_BACKEND=s3` — pick whichever free tier is easiest to sign up for:

| Provider | Free tier | Notes |
|---|---|---|
| **Skip it** (`STORAGE_BACKEND=local`, the `render.yaml` default) | N/A | Zero setup. Images/PDFs reset on redeploy; survey data does not. Recommended unless you specifically need file persistence. |
| **Backblaze B2** | 10GB free, no credit card | Often the least friction to sign up for. Create a bucket + "Application Key" (their term for API key) at https://www.backblaze.com/b2/. |
| **Cloudflare R2** | 10GB free | Requires a Cloudflare account with R2 enabled (sometimes asks for a credit card for verification even though usage stays free under 10GB). |

Whichever you pick, set these on the Render service (see below) — the variable names are identical for every provider:

```bash
STORAGE_BACKEND=s3
S3_ENDPOINT_URL=<provider's S3 endpoint>      # R2: https://<account_id>.r2.cloudflarestorage.com
                                                # B2: https://s3.<region>.backblazeb2.com
S3_REGION=auto                                 # B2: use the region from your bucket, e.g. us-west-004
S3_BUCKET_NAME=coral-ai
S3_ACCESS_KEY_ID=<access key id>
S3_SECRET_ACCESS_KEY=<secret access key>
```

With this set, uploaded images and generated PDF reports are written straight to the bucket instead of local disk — they survive redeploys, and `GET /api/report/{id}/download` transparently 307-redirects to a short-lived presigned URL instead of serving a local file.

## 3. Backend — Render

The repo root includes a [`render.yaml`](../render.yaml) blueprint that already sets the correct `rootDir` (`src/backend`), build/start commands, and health check. Fastest path:

1. In the [Render dashboard](https://dashboard.render.com), click **New → Blueprint**, connect this GitHub repo, and Render reads `render.yaml` automatically.
2. It'll prompt you to fill in the vars marked `sync: false` in `render.yaml` (`DATABASE_URL`, `GEMINI_API_KEY`, `CORS_ORIGINS`, `S3_*`, etc.) — paste in the Neon connection string and R2 credentials from the steps above.

Or configure it manually without the blueprint:

1. Push this repo to GitHub.
2. In Render, create a **New Web Service** pointing at `src/backend/`.
3. Build command:
   ```bash
   pip install -r requirements.txt
   ```
4. Start command:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
5. Set environment variables (mirroring `.env.example`):
   - `DATABASE_URL` → the Neon connection string
   - `GEMINI_API_KEY` → production Gemini key
   - `CORS_ORIGINS` → the deployed frontend's URL (e.g. `https://coral-ai.vercel.app`)
   - `STORAGE_BACKEND=s3` + the `S3_*` vars from step 2 above
   - `NASA_SST_ENABLED`, `NASA_API_KEY` → optional

## 4. Frontend — Vercel

1. Deploy the backend first (step 3) so you have its Render URL (e.g. `https://coral-ai-backend.onrender.com`).
2. In the [Vercel dashboard](https://vercel.com/new), **Import Project** from this GitHub repo.
3. Vercel needs a subdirectory, not the repo root:
   - **Root Directory** → `src/frontend/`
   - **Framework Preset** → Vite (auto-detected)
   - **Build Command** → `npm run build` (default)
   - **Output Directory** → `dist` (default)
4. Add one environment variable before deploying:
   - `VITE_API_BASE_URL` → `https://coral-ai-backend.onrender.com/api` (your Render URL + `/api`)
   - `src/services/api.js` reads this at build time — Vite bakes it into the bundle, so it must be set *before* clicking Deploy (not added afterward without a redeploy).
5. Click **Deploy**. Once live, copy the resulting Vercel URL (e.g. `https://coral-ai.vercel.app`).
6. Go back to the Render service and update `CORS_ORIGINS` to that Vercel URL, then let it redeploy — until this is set, the backend will reject the frontend's requests with a CORS error.

## 5. Post-Deploy Checklist

- [ ] Confirm `/health` returns `200` on the Render URL.
- [ ] Confirm CORS allows the Vercel domain (check `CORS_ORIGINS`).
- [ ] Run one end-to-end upload → analyze → report → dashboard flow against production.
- [ ] Redeploy once on purpose, then confirm a survey created *before* the redeploy still shows up on `/api/dashboard/surveys` (proves Neon is wired correctly) and its report still downloads (proves R2 is wired correctly).
- [ ] Rotate any API keys committed accidentally during local development.

## Local Parity (optional)

To mirror production locally before deploying, run Postgres via Docker Compose instead of SQLite:

```bash
docker compose up -d postgres
# src/backend/.env:
# DATABASE_URL=postgresql://coral:coral@localhost:5432/coral_ai
```

You can also point `src/backend/.env` at your real R2 bucket locally (set `STORAGE_BACKEND=s3` + the `S3_*` vars) to test the exact storage path production will use, without needing Render at all.

## Future: Containerized Deployment

For teams preferring containers over Render's native Python buildpack, both `src/backend/` and `src/frontend/` are structured to support a straightforward `Dockerfile` per service (not included in the hackathon MVP) — deployable to any container platform (Fly.io, Railway, AWS ECS) with the same environment variables described above.
