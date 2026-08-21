# RailSphere Backend

A railway data backend inspired by the Indian Railways network: stations, trains, routes, route-station sequencing, and schedules, backed by a real dataset of ~9,000 stations, ~5,200 trains/routes, ~416,000 route-station entries, and ~5,200 schedules.

---

## What's actually here

- JWT authentication (register / login / current user), Argon2 password hashing via `pwdlib`
- Full CRUD for stations, trains, and routes
- Route-station relationships (ordered station sequencing per route, with duplicate-station and duplicate-sequence-number protection)
- Schedule records and a `/journeys` listing endpoint joining train + route + schedule
- A batch import pipeline (`app/importers/`) that populated the real dataset above, idempotent on rerun (every importer checks for existing rows before inserting)
- A pytest suite (15 tests) covering health, auth, stations, and route-station duplicate handling, with true per-test isolation (each test runs in a rolled-back transaction)
- CI on GitHub Actions running that suite against a real Postgres service container
- A working AWS deployment: EC2 (Ubuntu) running the app under systemd + gunicorn/uvicorn workers, behind nginx, with PostgreSQL running natively on the same instance

**Not built**: ticket booking, seat allocation, waitlist, payments, Redis, Celery, Docker, HTTPS/domain. These were mentioned in earlier drafts of this README as aspirational; removed here to keep this file honest about current state.

---

## Tech Stack

- **API**: FastAPI, Pydantic v2
- **Data**: PostgreSQL, SQLAlchemy 2.0 (async, via `psycopg`), Alembic migrations
- **Auth**: JWT (`PyJWT`), Argon2 hashing (`pwdlib`)
- **Testing**: pytest, pytest-asyncio, httpx (ASGI in-process client)
- **CI**: GitHub Actions
- **Deployment**: gunicorn (uvicorn workers) under systemd, nginx as reverse proxy, PostgreSQL native on the same EC2 instance

---

## Project Structure

```text
RailSphere/
├── .github/workflows/ci.yml    # test suite on push/PR
├── backend/
│   ├── alembic/                # migrations (single verified baseline + incremental changes)
│   ├── app/
│   │   ├── api/                # routers + dependency injection wiring
│   │   ├── core/                # config, JWT, password hashing, logging
│   │   ├── db/                  # engine/session
│   │   ├── importers/           # dataset import pipeline
│   │   ├── models/              # SQLAlchemy models
│   │   ├── repositories/        # DB access layer
│   │   ├── schemas/             # Pydantic request/response models
│   │   └── services/            # business logic layer
│   ├── deploy/                  # systemd unit + nginx config used on EC2
│   ├── scripts/                 # standalone per-dataset import entry points
│   ├── tests/                   # pytest suite
│   ├── datasets/                # raw import data (gitignored, not versioned -- large per-environment files)
│   ├── requirements.txt         # production dependencies
│   ├── requirements-dev.txt     # + test tooling
│   └── run.py                   # Windows-safe local dev launcher (see note below)
└── docs/architecture.md
```

---

## Architecture

```
                Client
                   │
                   ▼
            FastAPI Routers
                   │
                   ▼
            Service Layer
                   │
                   ▼
          Repository Layer
                   │
                   ▼
     SQLAlchemy Async ORM
                   │
                   ▼
             PostgreSQL
```

Every domain (auth, stations, trains, routes, route-stations, journeys) follows this same layering, wired through `app/api/dependencies.py`.

---

## Getting Started (Docker)

The fastest way to get the full stack running — API, Postgres, Redis, Jaeger,
and the background worker — with nothing installed but Docker:

```bash
git clone https://github.com/rohantiwari9573/railsphere-backend.git
cd railsphere-backend
docker compose up --build
```

This builds the image, starts Postgres, Redis, and Jaeger, applies all
migrations automatically on startup, then starts the API (`localhost:8000`)
and the arq worker. Postgres and Redis are exposed on `5433` and `6380` on
the host (not their usual `5432`/`6379`) specifically so they don't collide
with a native Postgres/Redis you might already have running for local dev.
Open `http://localhost:16686` for the Jaeger UI to see live request traces.

The database starts empty — the real dataset (`backend/datasets/*.json`,
~95MB) isn't in this repo. To populate it:

```bash
docker compose exec backend python -m app.importers.import_all
```

`docker compose down` stops everything; add `-v` to also drop the Postgres
volume and start fresh next time.

---

## Getting Started (local development, no Docker)

### Clone and set up a virtual environment

```bash
git clone https://github.com/rohantiwari9573/railsphere-backend.git
cd railsphere-backend/backend
python -m venv .venv
```

Activate it — Windows: `.venv\Scripts\activate`, Linux/macOS: `source .venv/bin/activate`

### Install dependencies

```bash
pip install -r requirements.txt
# or, for running tests too:
pip install -r requirements-dev.txt
```

### Configure environment

Copy `.env.example` to `.env` and fill in `DATABASE_URL` and `SECRET_KEY` at minimum. `CORS_ORIGINS` is optional (comma-separated; leave empty to disable CORS entirely).

### Run migrations

```bash
alembic upgrade head
```

### Start the server

**Windows:** use `python run.py`, not `uvicorn app.main:app --reload` directly. psycopg's async driver can't run on Windows' default ProactorEventLoop, and `uvicorn`'s own CLI creates its event loop *before* importing the app module — too late to apply the fix. `run.py` sets the correct event loop policy before starting uvicorn.

**Linux/macOS:** either works —

```bash
uvicorn app.main:app --reload
# or
python run.py
```

### Import the dataset (optional)

Populates stations/trains/routes/route-stations/schedules from `backend/datasets/*.json` (not included in this repo — large per-environment files):

```bash
python -m app.importers.import_all
```

---

## Testing

```bash
pip install -r requirements-dev.txt
createdb railsphere_test          # one-time
DATABASE_URL=postgresql+psycopg://postgres:<password>@localhost:5432/railsphere_test alembic upgrade head
pytest -v
```

Each test runs inside a database transaction that's rolled back afterward, so the test DB stays empty between runs regardless of test order. CI runs this same suite automatically against a fresh Postgres container on every push/PR to `main`.

---

## Deployment

Currently deployed on a single AWS EC2 instance (Ubuntu, t3.micro):

- **App**: `backend/deploy/railsphere.service` — a systemd unit running `gunicorn` with 2 `uvicorn.workers.UvicornWorker` processes, bound to `127.0.0.1:8000`
- **Reverse proxy**: `backend/deploy/nginx.conf` — nginx on port 80 forwarding to the app, with standard `X-Forwarded-*` headers
- **Database**: PostgreSQL running natively on the same instance (not in a container), bound to `127.0.0.1` only — not exposed to the internet
- **Swap**: a 2GB swap file is configured (the instance only has ~900MB RAM; importing the full dataset needs headroom beyond that)

Served over HTTPS via a free nip.io wildcard domain + Let's Encrypt (`backend/deploy/nginx.conf`), so the API and any consumer of it get a valid certificate with no purchased domain required.

---

## API Documentation

- Swagger UI: `https://<host>/docs`
- ReDoc: `https://<host>/redoc`

---

## Roadmap

### Done

- [x] FastAPI project setup, async SQLAlchemy, Alembic (single verified migration baseline)
- [x] JWT authentication (register/login/current user)
- [x] Stations, trains, routes, route-stations, schedules — full CRUD where applicable
- [x] Data import pipeline, idempotent, populated with the real dataset
- [x] CORS, structured logging, global unhandled-exception handler
- [x] Test suite + CI
- [x] EC2 deployment: systemd + gunicorn + nginx
- [x] HTTPS via nip.io + Let's Encrypt
- [x] Request-id tracing + per-IP rate limiting
- [x] Trigram search (`pg_trgm`) with similarity-ranked results
- [x] Materialized views for analytics, refreshed by a scheduled background job
- [x] Redis cache-aside layer for hot read paths (station/train lookups, analytics)
- [x] WebSocket live updates + Prometheus metrics
- [x] Docker + docker-compose (API, Postgres, Redis, Jaeger, worker)
- [x] Load-tested with Locust (baseline in `backend/loadtest/README.md`)
- [x] CI/CD auto-deploy to EC2 on push to `main`
- [x] Circuit breaker around Redis cache calls
- [x] Read-only GraphQL API alongside REST (`/graphql`)
- [x] OpenTelemetry distributed tracing (Jaeger in local dev, opt-in via `OTEL_EXPORTER_OTLP_ENDPOINT`)

---

## Author

**Rohan Tiwari**

- GitHub: https://github.com/rohantiwari9573
- LinkedIn: https://www.linkedin.com/in/rohan-tiwari-012106283/
