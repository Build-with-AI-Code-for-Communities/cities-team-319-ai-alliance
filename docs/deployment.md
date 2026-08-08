# Deployment Plan

Target stack: **Vercel** (frontend) + **Render free tier** (backend) + **Neon** (managed PostgreSQL) + **Cloudflare R2** (object storage).

Render's free web services are ideal for a hackathon budget, but come with two constraints this plan works around:

- **No persistent disk** — the local filesystem is wiped on every redeploy and periodically on restart. SQLite and local `uploads/`/`reports/` don't survive this.
- **Spins down after 15 min idle** — the first request after idle takes ~30-50s to cold-start. Nothing to fix here; just expect it in a demo.

Neon solves the first problem for the database; R2 solves it for uploaded images and generated PDFs. Both have generous free tiers and need no credit card.

## 1. Database — Neon (free Postgres)

1. Create a free project at https://neon.tech.
2. Copy the connection string (looks like `postgresql://user:password@ep-xxxx.neon.tech/coral_ai?sslmode=require`).
3. This becomes `DATABASE_URL` for the backend service below. SQLAlchemy + `psycopg2-binary` (already in `requirements.txt`) handle the rest — no code changes needed.

## 2. Object Storage — Cloudflare R2 (free 10GB tier)

The backend's storage layer (`app/services/storage_service.py`) already supports any S3-compatible provider via `STORAGE_BACKEND=s3` — R2 is the recommended free option:

1. In the Cloudflare dashboard, go to **R2** and create a bucket (e.g. `coral-ai`).
2. Create an **R2 API token** (Account API Token, "Object Read & Write" permission) — this gives you an Access Key ID and Secret Access Key.
3. Your endpoint URL is `https://<account_id>.r2.cloudflarestorage.com` (account ID is shown on the R2 dashboard).
4. Set these on the Render service (see below):
   ```bash
   STORAGE_BACKEND=s3
   S3_ENDPOINT_URL=https://<account_id>.r2.cloudflarestorage.com
   S3_REGION=auto
   S3_BUCKET_NAME=coral-ai
   S3_ACCESS_KEY_ID=<your-r2-access-key-id>
   S3_SECRET_ACCESS_KEY=<your-r2-secret-access-key>
   ```

With this set, uploaded images and generated PDF reports are written straight to R2 instead of local disk — they survive redeploys, and `GET /api/report/{id}/download` transparently 307-redirects to a short-lived presigned URL instead of serving a local file.

Leaving `STORAGE_BACKEND=local` (the default) is fine for local development or a paid Render plan with a persistent disk mounted at `src/backend/uploads` and `src/backend/reports`.

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

1. In Vercel, import the repo with **root directory** set to `src/frontend/`.
2. Framework preset: **Vite**.
3. Build command: `npm run build`, output directory: `dist`.
4. Set environment/proxy: since the frontend calls relative `/api/*` paths, either:
   - Add a `vercel.json` rewrite forwarding `/api/*` to the Render backend URL, **or**
   - Point `axios`'s `baseURL` (in `src/services/api.js`) at the full Render URL via a `VITE_API_BASE_URL` env var for production builds.

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
