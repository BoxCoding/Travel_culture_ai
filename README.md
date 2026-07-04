# Wayfare — AI-Powered Travel & Culture Discovery Platform

An AI-powered platform that helps travelers discover destinations and engage with
local culture in meaningful ways: personalized attraction recommendations, AI-uncovered
hidden gems, immersive heritage storytelling, local event suggestions, and authentic
cultural experience connections.

## Architecture

```
Browser
  │
  ▼
Next.js 14 (App Router, TypeScript, Tailwind)  ──  Auth.js v5 (Credentials + Prisma/Turso libSQL)
  │  Server Components / Route Handlers mint a short-lived bridge JWT server-side
  ▼
FastAPI (Python)  ──  LangGraph agent graph  ──  Gemini API (gemini-3-flash)
  │
  ▼
Firestore — destinations, hidden gems, heritage stories, events, experiences, saved items
```

Two independent databases:
- `frontend` — user accounts (Auth.js / Prisma), via a libSQL driver adapter: a local SQLite
  file in dev, or a hosted Turso database in production.
- `backend` — all travel/cultural domain data lives in Firestore (Firebase Admin SDK).

Next.js is the only thing end users talk to and owns authentication. It never exposes the
shared `AUTH_BRIDGE_SECRET` to client-side JS — only server code (Server Components, Route
Handlers, Server Actions) mints the bridge JWT and calls FastAPI. See
[`docs/CONTRACT.md`](docs/CONTRACT.md) for the full API contract and auth-bridge spec.

## AI features (LangGraph + Gemini)

The backend runs a real `langgraph.StateGraph` (`backend/app/agents/graph.py`) with nodes for:

- **Recommendations** — ranked attractions matched to interests/budget/duration/travel style
- **Hidden gems** — lesser-known local spots invented and described by Gemini
- **Heritage storytelling** — immersive narrative pieces about a destination's culture/history
- **Local events** — plausible upcoming festivals/events for a destination
- **Cultural experiences** — authentic workshops, homestays, artisans, culinary experiences
- **Conversational concierge** (`/api/chat`) — a full graph run: `classify_intent` routes a
  free-text message to the right node(s), then `synthesize` composes the reply, with
  lightweight multi-turn memory keyed by `thread_id`

AI-generated content is cached in Firestore after first generation (so only the first request
per destination is slow) and every API response includes an `ai_generated` flag so the UI can
show a **"AI-generated — verify before travel"** disclaimer. This is deliberate: the platform
has no live events/facts feed, so generated events/heritage details are illustrative
suggestions, not verified real-time facts.

## Project layout

```
backend/            FastAPI + LangGraph + Firestore
  app/main.py        app entrypoint, CORS, router mounting, startup seed
  app/agents/        LangGraph state, graph wiring, Gemini client, per-feature nodes
  app/routers/       REST endpoints (destinations, recommendations, storytelling, chat, saved)
  app/firestore_client.py   Firebase Admin SDK init (service account or ADC)
  app/auth.py        bridge-JWT verification dependencies
  app/seed.py        seeds 8 real destinations on first run
  requirements.txt
  render.yaml        Render blueprint (build/start commands, health check, env var slots)
  Dockerfile         alternative container-based deploy path
  .env               GEMINI_API_KEY, AUTH_BRIDGE_SECRET, FIREBASE_SERVICE_ACCOUNT_JSON, CORS_ORIGINS (gitignored)

frontend/            Next.js 14 + Auth.js v5 + Prisma + Tailwind
  app/               pages: /, /login, /register, /dashboard, /destinations/[id]
  app/api/           route handlers: auth, register, chat proxy, recommendations proxy, saved proxy
  components/        Navbar, DestinationCard, Tabs, ChatWidget, RecommendationForm, etc.
  lib/auth.ts        Auth.js config (Credentials provider, JWT sessions)
  lib/backend.ts     server-only FastAPI client + bridge-JWT minting
  lib/prisma.ts      Prisma client wired to a libSQL adapter (local file or Turso)
  prisma/schema.prisma
  .env.local         NEXTAUTH_SECRET, AUTH_BRIDGE_SECRET, BACKEND_API_URL, TURSO_* (gitignored)

docs/
  CONTRACT.md        binding API/auth contract shared by both sides
```

## Running it locally

### Backend
```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# backend/.env needs FIREBASE_SERVICE_ACCOUNT_JSON set (full JSON of a service account key)
uvicorn app.main:app --port 8010   # port 8000 was occupied by another local app on this machine
```
`GET http://localhost:8010/api/health` should return `{"status":"ok"}`. Destinations are
auto-seeded into Firestore on first startup.

### Frontend
```bash
cd frontend
npm install
npx prisma generate
DATABASE_URL="file:./dev.db" npx prisma migrate deploy   # first time only, local SQLite file
npm run dev
```
Visit `http://localhost:3000`. `frontend/.env.local` must have `AUTH_BRIDGE_SECRET` set to the
exact same value as `backend/.env`, and `BACKEND_API_URL` pointing at wherever the backend is
running (`http://localhost:8010` in this setup). Leave `TURSO_DATABASE_URL`/`TURSO_AUTH_TOKEN`
unset locally to use the local SQLite file instead of Turso.

## Deployment

- **Backend → Render**: connect this repo, use the `backend/render.yaml` blueprint (build:
  `pip install -r requirements.txt`, start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`,
  health check `/api/health`). Set `GEMINI_API_KEY`, `AUTH_BRIDGE_SECRET`,
  `FIREBASE_SERVICE_ACCOUNT_JSON`, and `CORS_ORIGINS` (the deployed frontend URL) in the
  Render dashboard — they're marked `sync: false` so they're never committed.
- **Frontend → Vercel**: `vercel --prod` from `frontend/`. Set `NEXTAUTH_SECRET`,
  `NEXTAUTH_URL` (the Vercel URL), `AUTH_BRIDGE_SECRET` (same value as the backend),
  `BACKEND_API_URL` (the Render URL), and `TURSO_DATABASE_URL`/`TURSO_AUTH_TOKEN` as Vercel
  project environment variables.

## Known issues

- **Gemini model**: set to `gemini-3-flash` per request. If this model id isn't available on
  your API key's project, AI-backed endpoints will return a clean `502` with the exact
  upstream error rather than crashing — swap `GEMINI_MODEL` in `backend/.env` if so.
- **Security**: `npm audit` flags known advisories in Next.js 14.2.35 (mostly Image
  Optimizer / rewrites / middleware DoS and cache-poisoning issues) that are only fully
  fixed by upgrading to Next 15/16 — a bigger, riskier change deferred for now. This app
  doesn't use `next/image` remote optimization, rewrites, middleware, or i18n, which
  covers most of the actual exposure, but the upgrade is worth doing when there's time to
  regression-test it.

## Tech stack

| Layer | Choice |
|---|---|
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind CSS |
| Auth | Auth.js v5, Credentials provider, JWT sessions, Prisma + libSQL (Turso in prod) |
| Backend | FastAPI, Python |
| Agents | LangGraph (`StateGraph`) |
| LLM | Gemini (`gemini-3-flash` via `langchain-google-genai`) |
| Database | Firestore (backend domain data), libSQL/Turso (frontend auth) |
