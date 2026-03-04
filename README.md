## Statsmec – Counter-Strike Analytics Dashboard

**Statsmec** is a full‑stack Counter‑Strike analytics dashboard built with **FastAPI**, **React + TypeScript**, **PostgreSQL**, and **Redis**. It aggregates match data from Steam and FACEIT, computes advanced analytics, and presents them in an interactive dashboard.

### Stack

- **Backend**: FastAPI (Python 3.11), SQLAlchemy, PostgreSQL, Redis, httpx
- **Frontend**: React 18, TypeScript, Vite, Recharts
- **Data**: PostgreSQL (normalized schema for users, matches, rounds, weapon stats)
- **Infra**: Docker, docker‑compose

---

### Project Structure

- **backend/**
  - `app/main.py` – FastAPI application factory and health check
  - `app/core/config.py` – settings via environment variables
  - `app/db/session.py` – async SQLAlchemy session factory
  - `app/models/` – SQLAlchemy models (`User`, `Match`, `Round`, `WeaponStat`)
  - `app/schemas/` – Pydantic schemas for API responses and analytics
  - `app/services/` – analytics, caching, and external API clients (Steam / FACEIT)
  - `app/api/v1/` – versioned API routers and routes
  - `tests/` – backend unit tests (pytest)
- **frontend/**
  - Vite React app with TypeScript
  - `src/components/` – dashboard panels and charts
  - `src/api/client.ts` – Axios client with simple in‑memory caching
- **docker-compose.yml** – PostgreSQL, Redis, backend, frontend
- **.env.example** – sample environment variables

---

### Environment Variables

Copy the example file and edit as needed:

```bash
cp .env.example .env
```

Key variables:

- **Database**
  - `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB`
- **External APIs**
  - `STEAM_API_KEY` – Steam Web API key
  - `FACEIT_API_KEY` – FACEIT API key
- **CORS**
  - `BACKEND_CORS_ORIGINS` – e.g. `["http://localhost:5173"]`

---

### Running Locally with Docker Compose

```bash
docker compose up --build
```

Services:

- **Backend API**: `http://localhost:8000` (docs at `/docs`)
- **Frontend**: `http://localhost:5173`
- **PostgreSQL**: `localhost:5432`
- **Redis**: `localhost:6379`

---

### Backend – Development (without Docker)

```bash
cd backend
pip install "poetry>=1.8.0"
poetry install
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Run tests:

```bash
cd backend
poetry run pytest
```

---

### Frontend – Development (without Docker)

```bash
cd frontend
npm install
npm run dev
```

Run lint and tests:

```bash
cd frontend
npm run lint
npm test
```

Ensure `VITE_API_BASE_URL` in your frontend environment (or the docker‑compose service) points at the FastAPI backend, e.g. `http://localhost:8000/api/v1`.

---

### API Overview

- **User & Match Data**
  - `POST /api/v1/users/` – create a user with Steam / FACEIT IDs
  - `GET /api/v1/users/{user_id}` – fetch user profile
  - `GET /api/v1/users/{user_id}/matches` – match history (from PostgreSQL)
  - `POST /api/v1/users/{user_id}/sync` – sample sync from Steam / FACEIT (cached)
- **Analytics**
  - `GET /api/v1/analytics/users/{user_id}` – combined analytics:
    - Kill/death ratio per map and weapon
    - Win rate trend over time
    - Weapon “heatmaps” (sample grid data)
    - Comparison vs. rank averages (sample FACEIT integration)

External API calls are implemented in `backend/app/services/external_clients.py` and cached short‑term via Redis using `backend/app/services/cache.py`.

---

### Data sources (accurate stats)

Statsmec uses **official APIs** so the numbers match what you see on the platforms:

- **FACEIT (primary, accurate)**  
  Sync pulls from the [FACEIT Data API](https://docs.faceit.com/docs/data-api):
  - `GET /players/{id}/history?game=cs2` – match list
  - `GET /matches/{match_id}` – match details (map, score, result, timestamps)
  - `GET /matches/{match_id}/stats` – round‑by‑round and per‑player stats (kills, deaths, headshots, weapon)
  Data is mapped into `Match`, `Round`, and `WeaponStat` in `app/services/faceit_ingestor.py`, so dashboards use the same source as FACEIT (and tools like Repeek that read FACEIT).

- **Steam**  
  Optional; Steam does not expose rich CS2 match/round stats via a simple API, so only basic match list data is used when a Steam API key is set.

---

### Notes & Next Steps

- FACEIT sync is full: match details and per‑round, per‑player stats are fetched and stored. Steam sync remains minimal unless you add demo parsing or another source.
- Analytics calculations in `backend/app/services/analytics.py` are written for clarity and can be optimized or enriched as you refine your schema and data volume.
- Add migrations (e.g. Alembic) before deploying to production.

