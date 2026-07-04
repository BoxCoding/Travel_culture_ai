# API & Auth Contract — travel-culture-ai

This is the single source of truth both the frontend (Next.js/Auth.js) and backend
(FastAPI/LangGraph) implementations must follow so they integrate without drift.

## Architecture

```
Browser
  │
  ▼
Next.js (React, App Router) ── Auth.js v5 (Credentials + Prisma/Turso libSQL) ── owns user accounts, sessions, UI
  │  server-side fetch, attaches short-lived bridge JWT
  ▼
FastAPI (Python) ── LangGraph agent graph ── Gemini API ── owns travel domain data (Firestore)
```

Two independent databases:
- `frontend`: Auth.js users, via Prisma + a libSQL driver adapter — a local SQLite file
  (`frontend/prisma/dev.db`) in dev, or a hosted Turso (libSQL) database in production when
  `TURSO_DATABASE_URL`/`TURSO_AUTH_TOKEN` are set.
- `backend`: all travel/cultural domain data lives in **Firestore** (Google Cloud), accessed via
  the Firebase Admin SDK. Collection layout:
  - `destinations/{slug}` — one doc per destination (slug id, e.g. `jaipur`)
    - `destinations/{slug}/hidden_gems/{autoId}`
    - `destinations/{slug}/stories/{autoId}` (heritage narrative uses `theme == "__heritage__"`; the
      storytelling endpoint uses arbitrary theme strings)
    - `destinations/{slug}/events/{autoId}`
    - `destinations/{slug}/experiences/{autoId}`
  - `saved_items/{autoId}` — top-level collection, filtered by `user_id` field per query

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
All IDs are Firestore document ID strings (destination IDs are human-readable slugs;
sub-entity IDs are Firestore auto-IDs).

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/health` | none | liveness check |
| GET | `/api/destinations` | optional | list destinations; query params `q`, `region` |
| GET | `/api/destinations/{id}` | optional | destination detail |
| GET | `/api/destinations/{id}/hidden-gems` | optional | AI-uncovered hidden gems (generated on first request, cached in Firestore) |
| GET | `/api/destinations/{id}/heritage` | optional | AI-generated heritage/cultural-significance narrative (cached) |
| GET | `/api/destinations/{id}/events` | optional | upcoming local events/festivals |
| GET | `/api/destinations/{id}/experiences` | optional | authentic cultural experiences (workshops, homestays, artisans, festivals) |
| POST | `/api/storytelling` | optional | body `{destination_id, theme?}` → generates immersive first-person storytelling narrative |
| POST | `/api/recommendations` | optional | body `{interests: string[], budget?, duration_days?, region?, travel_style?}` → LangGraph agent returns ranked attractions + hidden gems + reasoning |
| POST | `/api/chat` | required | body `{message, thread_id?}` → conversational concierge (multi-turn LangGraph graph, intent-routed) |
| POST | `/api/experiences/{item_id}/save` | required | body `{item_type: "hidden_gem"\|"experience"\|"event", destination_id}` → saves an item to the user's list |
| GET | `/api/me/saved` | required | list current user's saved items (joined with source entity) |

### Key response shapes

`Destination`:
```json
{ "id": "jaipur", "name": "Jaipur", "country": "India", "region": "Asia",
  "description": "...", "image_url": "...", "lat": 26.9, "lng": 75.8,
  "tags": ["heritage", "architecture", "food"] }
```

`HiddenGem` / `Experience` / `Event` all share the shape:
```json
{ "id": "aB3xY...", "destination_id": "jaipur", "name": "...", "description": "...",
  "category": "...", "ai_generated": true }
```

`Heritage` (`GET /api/destinations/{id}/heritage`):
```json
{ "id": "...", "destination_id": "jaipur", "title": "...", "narrative": "...",
  "theme": "__heritage__", "ai_generated": true, "created_at": "..." }
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
GEMINI_MODEL=gemini-3-flash-preview
AUTH_BRIDGE_SECRET=<shared secret>
FIREBASE_SERVICE_ACCOUNT_JSON=<full JSON contents of a Firebase Admin service account key>
CORS_ORIGINS=http://localhost:3000
```

Frontend (`frontend/.env.local`):
```
NEXTAUTH_SECRET=<auth.js session secret>
NEXTAUTH_URL=http://localhost:3000
AUTH_BRIDGE_SECRET=<same shared secret as backend>
BACKEND_API_URL=http://localhost:8000
# Local dev fallback; Prisma resolves this relative to prisma/schema.prisma
DATABASE_URL=file:./dev.db
# Set both to use a hosted Turso database instead of the local SQLite file (e.g. in production)
TURSO_DATABASE_URL=
TURSO_AUTH_TOKEN=
```
