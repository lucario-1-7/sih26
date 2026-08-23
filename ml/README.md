# SocioSolve (sih26)

Citizen challenge reporting → clustering → theme → project → solution platform,
with ML-assisted (never automatic) duplicate detection and university/industry
matching for consortium formation.

## Architecture

```
Client / Mobile
      |
      v
FastAPI Server  --------HTTP------->  ML Service
      |                                (embeddings, scoring, matching —
      v                                 database-independent)
PostgreSQL + pgvector

Redis
      |
      v
ARQ Worker (shares server code, runs background jobs)
```

- The **server** owns all database access. The **ML service** never touches
  PostgreSQL — it's a stateless HTTP API over pure Python scoring/embedding
  functions.
- Duplicate detection is **human-in-the-loop**: the ML engine only returns
  ranked candidate matches with a similarity score; a human reviewer
  (`officer`/`admin`) records the final `DUPLICATE` / `NOT_DUPLICATE`
  decision, which is persisted as an auditable, append-only record. Nothing
  is ever auto-merged or deleted. A reviewer *can* correct an earlier
  decision on the same candidate pair — see "Duplicate decisions" below.
- Domain model: `Challenge` (citizen report) → `Cluster` (systemic problem)
  → `Theme` (broader pattern); `Cluster` → `Project` (execution) → `Solution`
  (result). Matching/consortium formation connects `Cluster`/`Project` to
  `Organization` (university/industry) candidates.
- A `Cluster`'s embedding is computed by the `generate_cluster_embedding` ARQ
  job after create/update — never lazily inside a `GET`. Until that job has
  run, `GET /matching/clusters/{id}` simply returns an empty ranking; reads
  never write.

## Directory Structure

```
server/     FastAPI backend — routers, services, repositories, models, workers
ml/         ML service — embeddings, duplicate detection, scoring, matching
database/   Alembic migrations (source of truth for schema)
client/     Web frontend (scaffold only — not yet built; see Known Limitations)
mobile/     Flutter app (scaffold only — not yet built; see Known Limitations)
docker-compose.yml
```

## Prerequisites

- Docker + Docker Compose
- Python 3.11 (3.12/3.13 also work; avoid very new releases — some ML
  dependencies lag behind on wheel availability)
- Node/Flutter — only once client/mobile implementation begins

## Environment Setup

1. Copy `.env.example` to `.env` and fill in real local values (a random
   `SECRET_KEY` in particular — generate with
   `python -c "import secrets; print(secrets.token_urlsafe(48))"`).
2. `.env` is gitignored and must never contain production secrets committed
   to source control.

> **Note:** `POSTGRES_PORT` defaults to `5433`, not `5432`. On this
> development machine, a native (non-Docker) PostgreSQL service was already
> using port 5432, which silently intercepted connections meant for the
> Docker container. If your machine has no such conflict, `5432` works fine
> — just make sure `POSTGRES_PORT` and `DATABASE_URL` agree with each other.

## Running with Docker Compose (full stack)

```
docker compose up --build
```

Starts `postgres`, `redis`, `ml`, `server`, `worker` — `server` and `worker`
wait for `postgres`, `redis`, and `ml` to report healthy first. The `ml`
service has no network path to `postgres` (separate `ml_net` network) —
database independence is enforced at the network level, not just in code.

Then, in another shell, apply migrations (see below) before using the API —
Compose does not run migrations automatically.

- Server: http://localhost:8000/api/v1/health, docs at `/api/v1/docs`
- ML service: http://localhost:8001/health

## Running locally without Docker (development)

Each service has its own virtualenv (Python 3.11 recommended) and
`requirements.txt`.

```
# Postgres + Redis only, via Docker
docker compose up -d postgres redis

# Server
cd server
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt      # .venv/bin/pip on macOS/Linux
.venv/Scripts/python -m uvicorn app.main:app --reload --port 8000

# Worker (separate terminal)
cd server
.venv/Scripts/python -m arq app.workers.settings.WorkerSettings

# ML service (separate terminal, separate venv)
cd ml
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu
.venv/Scripts/python -m uvicorn app.main:app --reload --port 8001
```

## Database Migrations

Alembic lives in `database/alembic/`, using the server's virtualenv (it has
`alembic`, `sqlalchemy`, and `psycopg2` for the sync migration driver):

```
cd database
../server/.venv/Scripts/python -m alembic -c alembic.ini upgrade head
```

The first migration enables the `vector` extension and creates all domain
tables plus HNSW indexes on every `Vector(384)` column. See
`database/README.md` for details on creating new migrations.

## Testing

```
# ML unit + integration tests (pure Python, real model — no DB, no server)
cd ml && .venv/Scripts/python -m pytest -q

# Server unit + integration tests (needs postgres, redis, and the ml
# service reachable at ML_SERVICE_URL — start them first)
cd server && .venv/Scripts/python -m pytest -q
```

Server integration tests run against `TEST_DATABASE_URL` (a separate
database on the same Postgres server, e.g. `sih26_test`), never against
`sih26_dev` — `server/tests/conftest.py` redirects `DATABASE_URL` before the
app is imported, so this applies transparently to both the `db` fixture and
the in-process `client`. One-time setup:

```
psql ... -c "CREATE DATABASE sih26_test"
cd database
DATABASE_URL=postgresql+asyncpg://<user>:<password>@localhost:5433/sih26_test \
  ../server/.venv/Scripts/python -m alembic -c alembic.ini upgrade head
```

If `TEST_DATABASE_URL` isn't set, tests fall back to `DATABASE_URL` (the dev
database) — set it to keep test runs from leaving data there. There's still
no per-test transaction-rollback fixture — tests use unique data (UUIDs) to
avoid collisions instead, which is enough at the current test volume.

## API Documentation

OpenAPI docs: `GET /api/v1/docs` (Swagger UI), raw schema at
`GET /api/v1/openapi.json`.

### Pagination

Every list endpoint (`GET /challenges`, `/clusters`, `/themes`, `/projects`,
`/solutions`, `/users`, `/matching/organizations`) uses **cursor (keyset)
pagination** — there is no `offset` parameter anywhere.

```
GET /api/v1/clusters?limit=20
GET /api/v1/clusters?limit=20&cursor=<opaque token from the previous page>
```

Response shape:

```json
{
  "items": [ ... ],
  "next_cursor": "<opaque token, or null on the last page>",
  "total": null
}
```

- Ordering is `(created_at DESC, id DESC)` — a fixed, stable, deterministic
  order. `id` breaks ties when two rows share a `created_at`.
- The cursor is an opaque, base64-encoded token carrying the last item's
  `(created_at, id)`. Treat it as an opaque string — do not decode or
  construct one client-side; its internal format may change.
- The first page is requested by omitting `cursor` entirely.
- The last page is signaled by `next_cursor: null`.
- A malformed or tampered cursor returns `422` with
  `{"code": "INVALID_CURSOR", ...}`, never a `500`.
- This scales to large tables because it never uses `OFFSET` — every page
  costs the same regardless of how deep into the collection it is.

### Duplicate decisions

`POST /api/v1/duplicate/decisions` is **append-only and reversible**:
recording a second `DUPLICATE`/`NOT_DUPLICATE` decision on the same
`(challenge_id, candidate_challenge_id)` pair does not fail with `409` — it
is a *correction*. The original row is never updated or deleted (the
database rejects `UPDATE`/`DELETE` on `duplicate_decisions` with a trigger —
see `database/alembic/versions/c64f1440c539_*.py`); a new row is appended
and becomes the current effective decision. The challenge's status is
always recomputed from the *latest* decision per candidate pair, so a
correction can reopen a challenge a prior decision had marked `duplicate`,
or re-mark one a prior decision had cleared. Every correction writes an
audit log entry (`duplicate.decision.corrected`) that references the
decision it corrects. RBAC (`officer`/`admin`) applies identically to the
initial decision and to any correction.

### ML service unavailability

If the ML service (embeddings, duplicate ranking, matching, consortium
suggestion) cannot be reached — connection refused, timeout, or a
non-2xx response — the server returns `503` with
`{"code": "ML_SERVICE_UNAVAILABLE", ...}` rather than a generic `500`.
Internal connection details are logged server-side only, never returned to
the client.

## Development Workflow

- All schema changes go through Alembic migrations — never hand-edit the
  database or use `create_all()`.
- Routers → services → repositories. Routers hold no business logic;
  repositories hold no business logic, only queries; transactions
  (`commit`) happen in the service layer.
- The server never imports ML engine code directly — it only calls the ML
  service over HTTP (`app/services/ml_client.py`).
- Every state-changing mutation on Challenge/Cluster/Project/Solution/
  Consortium and every auth event writes an append-only `audit_logs` row.
  `audit_logs` and `duplicate_decisions` reject `UPDATE`/`DELETE` at the
  database level (a trigger, not just application convention) — see
  `database/alembic/versions/c64f1440c539_*.py`.

## Known Limitations

- **Client/mobile**: only directory scaffolding exists (`client/src`,
  `mobile/lib`) — no application code yet, per the instruction to hold off
  until backend API contracts are stable.
- **SMS/OTP delivery**: no SMS gateway is integrated. `ConsoleOtpSender`
  only logs that a code was dispatched — it never logs or returns the code
  itself ("No plaintext OTPs" per CLAUDE.md applies in development too).
  Tests inject a fake `OtpSender` to capture the code instead. Swap in a
  real provider (e.g. MSG91/Twilio) behind the same `OtpSender` interface
  before production use.
- **Administrative area seeding**: there's no CRUD API for
  `administrative_areas` yet (STATE/DISTRICT/BLOCK/GP/VILLAGE hierarchy) —
  rows must be seeded directly (e.g. via a script) before challenges can
  reference a `administrative_area_id`. Not exposed as an endpoint since no
  reviewer/admin workflow for managing it was specified.
- **Scoring endpoints** (field intensity / priority / tractability) are
  fully implemented and tested in the ML service but are not yet wired to a
  server-side API route — no business requirement/UI consumes them yet.
- **RBAC role set**: uses exactly the four roles from the security skill
  (`citizen`, `officer`, `analyst`, `admin`). `officer` covers both
  "government administrator" and "duplicate reviewer" responsibilities
  from the prompt — no separate external government-validator service
  exists, matching the explicit instruction not to build one.
