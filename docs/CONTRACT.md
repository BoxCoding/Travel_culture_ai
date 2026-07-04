# API & Auth Contract — travel-culture-ai

This is the single source of truth both the frontend (Next.js/Auth.js) and backend
(FastAPI/LangGraph) implementations must follow so they integrate without drift.

## Architecture

```
Browser
  │
  ▼
Next.js (React, App Router) ── Auth.js v5 (Credentials + Prisma/SQLite) ── owns user accounts, sessions, UI
  │  server-side fetch, attaches short-lived bridge JWT
  ▼
FastAPI (Python) ── LangGraph agent graph ── Gemini API ── owns travel domain data (SQLite via SQLAlchemy)
```

Two separate SQLite files:
- `frontend/prisma/dev.db` — Auth.js users (managed by Prisma).
- `backend/app.db` — destinations, hidden gems, stories, events, experiences, saved items (managed by SQLAlchemy).

## Auth bridge

- Next.js is the only thing that talks to end users. It authenticates them via Auth.js
  (email + password, bcrypt hash, JWT session strategy — no server-side session table needed).
- When the Next.js server needs to call FastAPI on behalf of a signed-in user, it mints a
  **short-lived bridge JWT** (HS256, 5 min expiry) with claims `{ sub: userId, email }`,
  signed with `AUTH_BRIDGE_SECRET` (shared via env on both sides, same value in
  `backend/.env` and `frontend/.env.local`).
- It sends this as `Authorization: Bearer <token>` to FastAPI.
- FastAPI verifies the signature + expiry via a `get_current_user` dependency. Anonymous
  requests (no header) are allowed on read-only/browse endpoints; endpoints that
  personalize or write data require a valid bridge JWT and return 401 otherwise.
- FastAPI never issues its own login/password endpoints — it only trusts the bridge JWT.

## REST API (FastAPI, prefix `/api`)

All responses are JSON. Errors: `{"detail": "message"}` with appropriate HTTP status.

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/health` | none | liveness check |
| GET | `/api/destinations` | optional | list destinations; query params `q`, `region` |
| GET | `/api/destinations/{id}` | optional | destination detail |
| GET | `/api/destinations/{id}/hidden-gems` | optional | AI-uncovered hidden gems (generated on first request, cached in DB) |
| GET | `/api/destinations/{id}/heritage` | optional | AI-generated heritage/cultural-significance narrative (cached) |
| GET | `/api/destinations/{id}/events` | optional | upcoming local events/festivals |
| GET | `/api/destinations/{id}/experiences` | optional | authentic cultural experiences (workshops, homestays, artisans, festivals) |
| POST | `/api/storytelling` | optional | body `{destination_id, theme?}` → generates immersive first-person storytelling narrative |
| POST | `/api/recommendations` | optional | body `{interests: string[], budget?, duration_days?, region?, travel_style?}` → LangGraph agent returns ranked attractions + hidden gems + reasoning |
| POST | `/api/chat` | required | body `{message, thread_id?}` → conversational concierge (multi-turn LangGraph graph, intent-routed) |
| POST | `/api/experiences/{id}/save` | required | saves an experience/gem/event to the user's list |
| GET | `/api/me/saved` | required | list current user's saved items (joined with source entity) |

### Key response shapes

`Destination`:
```json
{ "id": 1, "name": "Jaipur", "country": "India", "region": "Asia",
  "description": "...", "image_url": "...", "lat": 26.9, "lng": 75.8,
  "tags": ["heritage", "architecture", "food"] }
```

`HiddenGem` / `Experience` / `Event` all share the shape:
```json
{ "id": 1, "destination_id": 1, "name": "...", "description": "...",
  "category": "...", "ai_generated": true }
```

`POST /api/recommendations` response:
```json
{ "summary": "...", "attractions": [{"name": "...", "reason": "..."}],
  "hidden_gems": [{"name": "...", "reason": "..."}] }
```

`POST /api/chat` response:
```json
{ "reply": "...", "thread_id": "..." }
```

## Environment variables

Backend (`backend/.env`):
```
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-2.0-flash
AUTH_BRIDGE_SECRET=<shared secret>
DATABASE_URL=sqlite:///./app.db
CORS_ORIGINS=http://localhost:3000
```

Frontend (`frontend/.env.local`):
```
NEXTAUTH_SECRET=<auth.js session secret>
NEXTAUTH_URL=http://localhost:3000
AUTH_BRIDGE_SECRET=<same shared secret as backend>
BACKEND_API_URL=http://localhost:8000
DATABASE_URL=file:./prisma/dev.db
```
