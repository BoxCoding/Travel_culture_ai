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
Next.js 16 (App Router, TypeScript, Tailwind)  ──  Auth.js v5 (Credentials provider)
  │  Server Components / Route Handlers mint a short-lived bridge JWT server-side
  ▼
FastAPI (Python)  ──  LangGraph agent graph  ──  Gemini API (gemini-3-flash-preview)
  │
  ▼
Firestore — single database for both sides: users, destinations, hidden gems, heritage
stories, events, experiences, saved items
```

**One Firestore project, no SQL/SQLite anywhere.** The frontend (Node `firebase-admin`) and
backend (Python Firebase Admin SDK) each hold their own copy of the same service account
credential and talk to Firestore independently. Next.js is the only thing end users talk to
and owns authentication; it never exposes the shared `AUTH_BRIDGE_SECRET` to client-side JS —
only server code (Server Components, Route Handlers) mints the bridge JWT and calls FastAPI.
See [`docs/CONTRACT.md`](docs/CONTRACT.md) for the full API contract and auth-bridge spec.

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
  tests/             pytest suite (42 tests) — fake Firestore + mocked Gemini, runs offline
  requirements.txt
  render.yaml        Render blueprint (build/start commands, health check, env var slots)
  Dockerfile         alternative container-based deploy path
  .env               GEMINI_API_KEY, AUTH_BRIDGE_SECRET, FIREBASE_SERVICE_ACCOUNT_JSON, CORS_ORIGINS (gitignored)

frontend/            Next.js 16 + Auth.js v5 + Tailwind
  app/               pages: /, /login, /register, /dashboard, /destinations/[id]
  app/api/           route handlers: auth, register, chat proxy, recommendations proxy, saved proxy
  components/        Navbar, DestinationCard, Tabs, ChatWidget, RecommendationForm, etc.
  lib/auth.ts        Auth.js config (Credentials provider, JWT sessions)
  lib/backend.ts     server-only FastAPI client + bridge-JWT minting
  lib/firebase-admin.ts   Firebase Admin SDK init (Firestore for user accounts)
  lib/users.ts       user CRUD against the `users` Firestore collection
  .env.local         NEXTAUTH_SECRET, AUTH_BRIDGE_SECRET, BACKEND_API_URL, FIREBASE_SERVICE_ACCOUNT_JSON (gitignored)

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
npm run dev
```
Visit `http://localhost:3000`. `frontend/.env.local` needs:
- `AUTH_BRIDGE_SECRET` set to the exact same value as `backend/.env`
- `BACKEND_API_URL` pointing at wherever the backend is running (`http://localhost:8010` here)
- `FIREBASE_SERVICE_ACCOUNT_JSON` — the same Firebase project as the backend (can be the same
  service account key)

## Testing

```bash
cd backend
source venv/bin/activate
python -m pytest -v
```

42 tests in `backend/tests/` cover every router (health, destinations, recommendations,
storytelling, chat, saved items) and the auth dependency (expired/invalid/missing tokens,
optional vs. required auth). They run fully offline: `tests/fake_firestore.py` is an in-memory
double for the Firestore client (wired in via FastAPI's `dependency_overrides`, no real GCP
project needed), and every Gemini-calling function is mocked at the LLM boundary
(`tests/conftest.py`'s `mock_gemini` fixture) so the suite is fast, deterministic, and free —
no API quota consumed. Tests also assert the AI-generation-cache behavior (first request
generates and persists, second request reuses the cached copy) and that Gemini failures
surface as clean `502`s rather than crashing.

## Deployment

- **Backend → Render**: connect this repo, use the `backend/render.yaml` blueprint (build:
  `pip install -r requirements.txt`, start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`,
  health check `/api/health`). Set `GEMINI_API_KEY`, `AUTH_BRIDGE_SECRET`,
  `FIREBASE_SERVICE_ACCOUNT_JSON`, and `CORS_ORIGINS` (the deployed frontend URL) in the
  Render dashboard — they're marked `sync: false` so they're never committed.
- **Frontend → Vercel**: connect this repo or run `vercel --prod` from `frontend/`. Set
  `NEXTAUTH_SECRET`, `NEXTAUTH_URL` (the Vercel URL), `AUTH_BRIDGE_SECRET` (same value as the
  backend), `BACKEND_API_URL` (the Render URL), and `FIREBASE_SERVICE_ACCOUNT_JSON` as Vercel
  project environment variables. No database provisioning needed on Vercel's side — Firestore
  is external and network-accessible, unlike a local SQLite file (which is why the original
  SQLite/Turso setup couldn't work on Vercel's ephemeral filesystem and was replaced).

## Known issues

- **Gemini quota**: `gemini-3-flash-preview` is a valid, recognized model id on this API key,
  confirmed by a live call — but the key's Google AI Studio project has no prepayment credits,
  so live calls return `429 RESOURCE_EXHAUSTED`. Every AI-backed endpoint handles this as a
  clean `502` with the upstream error message rather than crashing. Add billing at
  [ai.studio/projects](https://ai.studio/projects) to unblock live generation.

## Tech stack

| Layer | Choice |
|---|---|
| Frontend | Next.js 16 (App Router), TypeScript, Tailwind CSS |
| Auth | Auth.js v5, Credentials provider, JWT sessions |
| Backend | FastAPI, Python |
| Agents | LangGraph (`StateGraph`) |
| LLM | Gemini (`gemini-3-flash-preview` via `langchain-google-genai`) |
| Database | Firestore (single database for both frontend and backend) |
| Testing | pytest, 42 tests, offline (fake Firestore + mocked Gemini) |
