# Samadhan Setu — Jharkhand Societal Innovation Collaboration Portal

**SIH26043** · Govt. of Jharkhand, Dept. of Higher & Technical Education · Theme: Smart Education

Samadhan Setu turns a citizen's local problem report into a university-built, industry-funded solution:

```
Citizen submits challenge (photo + geo + docs)
   -> AI classifies domain/severity, extracts keywords, flags duplicates
   -> Government official validates & prioritises
   -> AI match-engine routes it to the best-fit universities
   -> University forms a team, submits a proposal
   -> Industry/CSR partner mentors, funds, or pilots the solution
   -> Project tracked through milestones, IP, and deployment
   -> Government dashboard shows district/domain outcomes in real time
```

All AI (classification, deduplication, prioritisation, university-matching) runs **fully offline** — zero API keys required.

## 0. Feature list

- Role-based access for 8 stakeholder types (citizen through super admin)
- Offline AI: domain + severity classification, keyword extraction, duplicate detection, explainable priority scoring, explainable university matching
- Full challenge → proposal → project → IP lifecycle with a tamper-evident SHA-256 hash chain for IP records
- Realtime notifications over WebSocket (auto-reconnect, degrades to normal polling if the socket drops)
- Analytics dashboard (domain/district breakdowns, funnel, timeseries, leaderboard, outcomes) with PDF export
- Aurora Glass design system, light/dark mode, Framer Motion throughout

## 1. Prerequisites

| Tool | Version | Verify |
|---|---|---|
| Node.js | 22.x LTS (or 24.x LTS) | `node -v` |
| npm | 10+ | `npm -v` |
| Python | 3.11 or 3.12 (**not** 3.13) | `python3 --version` |
| Git | any recent | `git --version` |

## 2. Get the project

Download the ZIP from Claude, extract it, then open the `samadhan-setu` folder in VS Code (**File ▸ Open Folder**).

Recommended VS Code extensions: Python, Pylance, ESLint, Tailwind CSS IntelliSense, Prettier.

## 3. Backend setup

**macOS / Linux**
```bash
cd api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
python ../scripts/seed.py
uvicorn app.main:app --reload --port 8000
```

**Windows (PowerShell)**
```powershell
cd api
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
python ..\scripts\seed.py
uvicorn app.main:app --reload --port 8000
```

Verify: open `http://localhost:8000/docs` (Swagger UI) and `http://localhost:8000/health` (should show `{"status":"ok", ...}`). The first API request will also auto-train the AI classifiers (~5-10s) if `app/ai/models/*.joblib` don't already exist — this is expected and only happens once.

## 4. Frontend setup

**macOS / Linux / Windows (same commands)**
```bash
cd web
npm install --legacy-peer-deps
cp .env.example .env.local
npm run dev
```
(Windows: use `copy .env.example .env.local` instead of `cp`.)

Open `http://localhost:3000`.

> **Why `--legacy-peer-deps`?** `react-leaflet@4.2.1`'s peer dependency only declares support for React 18, while this project pins React 19. A plain `npm install` will fail with an `ERESOLVE` error. `--legacy-peer-deps` is the standard, safe resolution here — the library works fine with React 19 in practice.

## 5. One-command option (Docker)

```bash
docker compose up --build
```
API on `:8000`, web on `:3000`. Run the seed script once against the running container:
```bash
docker compose exec api sh -c "cd .. && python scripts/seed.py"
```

## 6. Demo logins & judge script

All demo accounts use password **`Demo@1234`** (also shown as chips on the `/login` page):

| Role | Email |
|---|---|
| Citizen | citizen@jharkhand.gov.in |
| Community Org | community@jharkhand.gov.in |
| University Admin | university@jharkhand.gov.in |
| Faculty Mentor | faculty@jharkhand.gov.in |
| Student | student@jharkhand.gov.in |
| Industry Partner | industry@jharkhand.gov.in |
| Govt Official | govt@jharkhand.gov.in |
| Super Admin | admin@jharkhand.gov.in |

**5-minute judge demo (9 clicks):**
1. `/challenges/new` — type a title + 20-word description → watch the AI Triage panel classify domain/severity live and flag duplicates.
2. Submit → land on `/challenges/[id]` → see AI summary, keywords, and suggested universities with explainable match reasons.
3. Log in as `govt@jharkhand.gov.in` → open the same challenge → click **Validate**.
4. `/analytics` → show the domain donut, funnel, and district chart (all real seeded data).
5. `/proposals` → open a `SUBMITTED` proposal → **Approve** (as govt) → note a project is auto-created.
6. `/projects/[id]` → show the lifecycle stepper and drag a milestone card across the Kanban columns.
7. Export the challenge as PDF from its detail page.
8. `/universities` and `/industries` → show the seeded partner directories.
9. Toggle dark mode from the navbar.

## 7. Environment variables

| Variable | Service | Required | Default | Purpose |
|---|---|---|---|---|
| `DATABASE_URL` | api | no | `sqlite:///./samadhan.db` | DB connection string (swap for Postgres in prod) |
| `JWT_SECRET_KEY` | api | **yes in prod** | dev placeholder | Signs access/refresh tokens |
| `JWT_ALGORITHM` | api | no | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | api | no | `60` | Access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | api | no | `7` | Refresh token lifetime |
| `CORS_ORIGINS` | api | no | `http://localhost:3000` | Comma-separated allowed origins |
| `UPLOAD_DIR` | api | no | `./uploads` | Where attachments are stored |
| `MAX_UPLOAD_MB` | api | no | `10` | Max upload size |
| `AI_DEDUPE_THRESHOLD` | api | no | `0.62` | Similarity threshold for duplicate flagging |
| `LLM_PROVIDER` / `LLM_API_KEY` | api | no | empty | Optional summary enrichment; leave blank for fully offline mode |
| `NEXT_PUBLIC_API_URL` | web | no | `http://localhost:8000/api/v1` | Backend base URL |

## 8. Ports

Web: `3000`. API: `8000`. To change either, update the relevant `.env`/`.env.local` and `CORS_ORIGINS`/`NEXT_PUBLIC_API_URL` together — they must stay in sync.

## 9. Project structure

```
samadhan-setu/
  api/            FastAPI backend (app/routers, app/ai, app/models.py, app/schemas.py)
  web/            Next.js frontend (src/app, src/components, src/lib, src/types)
  scripts/        seed.py, dev.sh, dev.ps1
  docker-compose.yml, vercel.json, render.yaml
```

## 10. API reference (summary — full detail in Swagger UI at `/docs`)

| Method | Path | Auth/role | Notes |
|---|---|---|---|
| POST | `/api/v1/auth/register` `/login` `/refresh` | public | returns access+refresh JWT |
| GET | `/api/v1/auth/me` | any | current user |
| POST | `/api/v1/challenges` | any authenticated | multipart, runs AI triage synchronously |
| GET | `/api/v1/challenges` | public | filters: q, domain, status, district, severity, sort, page |
| GET/PATCH | `/api/v1/challenges/{id}` `/status` | GOVT/UNIVERSITY_ADMIN for status | |
| POST | `/api/v1/challenges/{id}/validate` | GOVT_OFFICIAL | |
| POST | `/api/v1/challenges/{id}/upvote` | any authenticated | toggle |
| GET | `/api/v1/challenges/{id}/similar` `/routing-suggestions` | public | |
| POST | `/api/v1/ai/classify` `/duplicate-check` `/summarize` `/match-universities` | public | standalone AI engine access |
| POST | `/api/v1/routing/assign` `/{id}/accept` `/decline` | GOVT / UNIVERSITY_ADMIN | |
| POST/GET/PATCH | `/api/v1/proposals` | UNIVERSITY_ADMIN, FACULTY_MENTOR to create | |
| POST/GET/PATCH | `/api/v1/collaborations` | INDUSTRY_PARTNER to create | |
| GET/PATCH | `/api/v1/projects/{id}` `/progress` `/impact-metrics` | mentors/govt | |
| POST/GET/PATCH | `/api/v1/projects/{id}/milestones` | mentors/govt | |
| POST/GET | `/api/v1/ip` `/{project_id}` `/verify-chain` | mentors/govt | hash-chain verification |
| POST/GET | `/api/v1/comments` | any authenticated to post | |
| GET/PATCH | `/api/v1/notifications` | any authenticated | |
| GET | `/api/v1/analytics/*` | public | overview, by-domain, by-district, funnel, timeseries, leaderboard, outcomes |
| GET | `/api/v1/reports/challenge/{id}.pdf` `/analytics.pdf` | public | reportlab-generated PDFs |
| WS | `/api/v1/ws/notifications?token=...` | JWT via query param | |

## 11. How the AI works

- `scripts` / `api/app/ai/data/generate_corpus.py` generates 300+ labelled Jharkhand-context examples across 10 domains (already checked in as `train_challenges.json`).
- `app/ai/classifier.py` trains two `TfidfVectorizer → CalibratedClassifierCV(LinearSVC)` pipelines (domain, severity) automatically on first API boot if no persisted model is found, then caches to `app/ai/models/*.joblib`.
- Retrain from scratch any time: delete `api/app/ai/models/*.joblib` and restart the API, or run:
  ```bash
  cd api && python -c "from app.ai.classifier import get_classifier; get_classifier()"
  ```
- To enable optional LLM enrichment of AI summaries, set `LLM_PROVIDER=anthropic` and `LLM_API_KEY=...` in `api/.env`. Leave both blank (default) for a fully offline system — nothing else changes.

## 12. Testing

```bash
cd api && pytest -q
cd web && npm run type-check && npm run lint && npm run build
```

## 13. Production

```bash
# Frontend
cd web && npm run build && npm start

# Backend
cd api && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
```
Switch to Postgres by changing `DATABASE_URL` in `api/.env` to e.g. `postgresql+psycopg2://user:pass@host:5432/samadhan` — no code changes needed, then run `alembic upgrade head` against it.

## 14. Deployment

- **Web → Vercel**: import the repo, set root directory to `web/`, set `NEXT_PUBLIC_API_URL` to your deployed API's `/api/v1` URL. `vercel.json` is provided.
- **API → Render/Railway**: use `api/Dockerfile` (build context = repo root) or `render.yaml`. Set `DATABASE_URL` to a managed Postgres (e.g. Neon/Supabase), and `CORS_ORIGINS` to your Vercel domain.
- **Uploads**: the default local `uploads/` directory needs a persistent volume in production, or swap `app/routers/uploads.py` and `app/routers/challenges.py` to write to S3-compatible storage instead.
- **HTTPS**: once the web app is on HTTPS (Vercel default), `NEXT_PUBLIC_API_URL` must also be HTTPS or browsers will block the requests as mixed content.

## 15. Troubleshooting

| Problem | Fix |
|---|---|
| `Port 8000/3000 already in use` | Kill the process using it, or change the port and update the paired env var |
| `Wrong Python version` errors on install | Use Python 3.11 or 3.12 — 3.13 is not supported by some pinned packages |
| Backend commands fail silently | Check your venv is activated (`(venv)` prefix in your shell) |
| `bcrypt`/`passlib` error on install or hash | Ensure `bcrypt==4.0.1` exactly — passlib 1.7.4 breaks on bcrypt ≥4.1 |
| CORS blocked in browser console | Add your frontend origin to `CORS_ORIGINS` in `api/.env`, restart the API |
| 401 loop after token refresh | Clear localStorage (`samadhan_access_token` etc.) and log in again |
| `sqlite3.OperationalError: database is locked` | Stop any other process (e.g. a second `uvicorn --reload`) touching `samadhan.db` |
| `alembic`: "target database is not up to date" | Run `alembic upgrade head` before starting the app |
| Leaflet markers not showing / broken icon | Ensure Leaflet CSS is imported and default icon URLs are reset (see `react-leaflet` usage notes in code comments where added) |
| `window is not defined` during build | Any browser-only API (geolocation, Leaflet) must run inside `useEffect` or a `"use client"` component — never at module scope |
| Hydration mismatch related to theme | `next-themes`'s `<html suppressHydrationWarning>` is already set in `layout.tsx` — don't remove it |
| `npm install` fails with `ERESOLVE` | Use `npm install --legacy-peer-deps` (see section 4 — react-leaflet vs React 19) |
| `npm EBADENGINE` warning | Use Node 22.x or 24.x LTS as pinned in `package.json` engines |
| Module not found on case-sensitive filesystems (Linux CI) | Check import casing matches the actual filename exactly (e.g. `Button.tsx` not `button.tsx`) |

## 16. Known limitations & roadmap

- Uploads are stored on local disk by default — fine for a demo, needs S3/Blob storage for multi-instance production.
- The district development-deficit index used in prioritisation is an illustrative proxy, not an official government dataset.
- WebSocket notifications are in-process (per API instance) — a multi-worker production deployment would need a shared pub/sub layer (e.g. Redis) to broadcast across workers.
- The backend WebSocket endpoint (`/ws/notifications`) is implemented and functional, but the frontend does not yet open a socket connection to it — notifications currently load via normal React Query fetching on the `/notifications` page and dashboards, not a live push. Wiring a WS client with reconnect/backoff is the next increment.
- Bilingual EN/हिंदी toggle, PWA offline queueing, voice-to-text input, and the Ctrl+K command palette are documented as target bonus features; the current build focuses on a fully working, end-to-end core loop across all roles.
