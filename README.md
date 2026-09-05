# SocioSolve

> Civic challenge reporting, clustering, validation, project execution, and university/industry consortium formation platform.

[![Branch: astifo](https://img.shields.io/badge/branch-astifo-blue.svg)](#)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](#)
[![FastAPI](https://img.shields.io/badge/backend-FastAPI-009688.svg)](#)
[![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL%2016%20%2B%20pgvector-336791.svg)](#)
[![Next.js](https://img.shields.io/badge/web-Next.js%2016-black.svg)](#)
[![Flutter](https://img.shields.io/badge/mobile-Flutter-02569B.svg)](#)

---

## 1. Overview

**SocioSolve** bridges the gap between citizens reporting grassroots civic challenges (potholes, water sanitation, electrical grid hazards, public health issues) and the institutions capable of solving them. It organizes individual citizen reports into systemic problem statements, validates them through government authorities, detects duplicates using human-in-the-loop AI, and matches academic researchers and industry partners into execution consortiums.

---

## 2. System Architecture

```
                  +----------------------------------------------+
                  |               Client Tier                    |
                  |  - citizen-portal (Next.js 16 / React 19)    |
                  |  - Customer_App   (Flutter iOS / Android)    |
                  |  - client         (Next.js 14 Org Portal)    |
                  +----------------------+-----------------------+
                                         |
                                         | HTTP / REST (/api/v1)
                                         v
                         +-------------------------------+
                         |   FastAPI Server (:8000)      |
                         |   (Routers, Services, RBAC)   |
                         +---------------+---------------+
                                 |               |
             +-------------------+               +--------------------+
             | (asyncpg)                         | (HTTP / JSON)      |
             v                                   v                    v
+--------------------------+           +-------------------+   +-------------+
| PostgreSQL 16 + pgvector |           |   Redis 7 Cache   |   |  ML Service |
| - HNSW Cosine Indexing   |           +---------+---------+   |   (:8001)   |
| - Append-only Triggers   |                     |             | (Stateless) |
+--------------------------+                     v             +-------------+
                                       +-------------------+
                                       |    ARQ Worker     |
                                       |  (Async Embeddings|
                                       |  & Clustering)    |
                                       +-------------------+
```

### Core Architectural Principles
- **ML Database Independence**: The ML engine is database-independent and runs on an isolated network (`ml_net`). It has zero access to PostgreSQL. All persistence is strictly owned by the FastAPI server.
- **Human-in-the-Loop AI**: Machine learning generates candidate rankings and similarity metrics; it **never** automatically merges, mutates, or deletes citizen reports. Government validators review candidate pairs, and all duplicate decisions are append-only and auditable.
- **Strict Keyset (Cursor) Pagination**: All collection listing endpoints (`/challenges`, `/clusters`, `/themes`, `/projects`, `/solutions`, `/matching/organizations`) use deterministic keyset pagination `(created_at DESC, id DESC)`. No slow SQL `OFFSET` queries are used.
- **Immutable Audit Trail**: State changes on challenges, clusters, projects, solutions, and consortiums append records to `audit_logs`. Database-level triggers prevent `UPDATE` and `DELETE` queries on audit and duplicate decision tables.

---

## 3. Repository Structure

```
SocioSolve/
├── citizen-portal/      # Citizen-facing Web Application (Next.js 16, React 19, Tailwind CSS v4)
├── Customer_App/        # Citizen-facing Mobile App (Flutter for Android & iOS)
├── client/              # Institutional & Admin Web Portal (Next.js 14, React 18, React Query)
├── server/              # Core API Server & Background Workers (FastAPI, SQLAlchemy 2 async, ARQ)
├── ml/                  # Machine Learning Service (Sentence-Transformers, PyTorch, Scikit-learn)
├── database/            # Database schema migrations & pgvector extensions (Alembic)
├── mobile/              # Mobile API specifications & scaffold
├── tests/               # End-to-end integration test suite
├── docker-compose.yml   # Multi-service local and deployment orchestration
└── .env.example         # Environment template with service and MSG91 configs
```

---

## 4. Subsystems Detail

### A. Core API Server (`server/`)
- **Stack**: FastAPI, SQLAlchemy 2.0 (async via `asyncpg`), Pydantic v2, ARQ worker.
- **Authentication**:
  - MSG91 OTP Widget support (client-side access tokens verified server-side).
  - Native server-driven OTP delivery with development fallbacks.
  - Presentation demo persona login bypass (`POST /auth/demo/login`) for evaluation.
- **Role-Based Access Control (RBAC)**:
  - `CITIZEN`: Submit challenges, track submissions, view public solutions.
  - `GOVERNMENT`: Roles `validator` and `field_assistant` (triage challenges, review duplicates, verify deliverables).
  - `UNIVERSITY`: Roles `coordinator` and `faculty` (claim problem clusters, propose research projects, form consortiums).
  - `INDUSTRY`: Role `industry` (sponsor, fund, pilot, and provide equipment for projects).
  - `SUPERADMIN`: Role `superadmin` (system-wide configuration, organization management).

### B. Machine Learning Service (`ml/`)
- **Stack**: FastAPI, Sentence-Transformers (`all-MiniLM-L6-v2`), PyTorch, Scikit-learn.
- **Capabilities**:
  - **Vector Embeddings** (`POST /api/v1/embeddings`): 384-dimensional dense text vectors.
  - **Duplicate Detection** (`POST /api/v1/duplicate-candidates`): Semantic similarity scoring against candidate corpuses.
  - **Domain Classification** (`POST /api/v1/classify-domain`): Automated routing across civic categories.
  - **Field Intensity Scoring** (`POST /api/v1/classify-field-intensity`): Predicts physical on-site fieldwork vs. remote analytical requirements.
  - **Consortium Matching** (`POST /api/v1/matching/rank` & `/matching/consortium`): Recommends university faculty and industry partners based on capability taxonomies.

### C. Citizen Applications
- **Citizen Web Portal (`citizen-portal/`)**:
  - Bilingual interface (English & Hindi) with Zustand-managed localization.
  - Step-by-step issue filing wizard with geolocation and media attachments.
  - Direct issue tracking by tracking code or mobile number.
- **Customer Mobile App (`Customer_App/`)**:
  - Production-ready Flutter app with animated onboarding, secure token storage, and phone OTP login.
  - Camera/gallery integration for photo attachments.
  - Real-time status cards for citizen issue progress.

### D. Institutional Web Portal (`client/`)
- Modular dashboard interfaces tailored to each domain:
  - `/organization/government`: Issue validation and duplicate candidate triage queue.
  - `/organization/university`: Problem cluster exploration and proposal creation.
  - `/organization/industry`: Project sponsorship, funding pledges, and CSR tracking.
  - `/organization/superadmin`: System analytics and user role assignments.

---

## 5. Getting Started

### Prerequisites
- [Docker](https://www.docker.com/) and Docker Compose
- Python 3.11+
- Node.js 20+ (for web frontends)
- Flutter SDK 3.11+ (for mobile app)

### 1. Configure Environment
Copy the sample environment file:
```bash
cp .env.example .env
```
Generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```
Paste this value into `SECRET_KEY` in `.env`.

### 2. Start Services via Docker Compose
Run the core platform (PostgreSQL with pgvector, Redis, ML Engine, FastAPI Server, and ARQ Worker):
```bash
docker compose up --build
```

Container endpoints:
- **FastAPI Server**: http://localhost:8000
- **Interactive Swagger Docs**: http://localhost:8000/api/v1/docs
- **ML Service**: http://localhost:8001
- **ML Service Health**: http://localhost:8001/health

### 3. Run Database Migrations
In a separate terminal, apply Alembic migrations:
```bash
cd database
../server/.venv/Scripts/python -m alembic -c alembic.ini upgrade head
```
*(On Linux/macOS, use `../server/.venv/bin/python`)*

---

## 6. Running Frontends

### Citizen Web Portal
```bash
cd citizen-portal
npm install
npm run dev
# Running on http://localhost:3000
```

### Institutional Web Portal
```bash
cd client
npm install
npm run dev
# Running on http://localhost:3001
```

### Flutter Mobile App
```bash
cd Customer_App
flutter pub get
flutter run
```
*Note: To connect to localhost from an Android device or emulator over USB, run `adb reverse tcp:8000 tcp:8000`.*

---

## 7. Testing

### ML Engine Tests
```bash
cd ml
python -m pytest -q
```

### Server Unit & Integration Tests
```bash
cd server
python -m pytest -q
```

### End-to-End Live Stack Tests
With the full Docker stack running:
```bash
SERVER_BASE_URL=http://localhost:8000/api/v1 python -m pytest tests/e2e -q
```

---

## 8. Git & Branching

This repository is maintained on the **`astifo`** branch for active feature delivery and verification. Ensure all pull requests and branch updates target `astifo`.
