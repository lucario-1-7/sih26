<div align="center">

# 🏛️ SocioSolve

### A Next-Generation Collaborative Civic Problem Solving & Consortium Platform

[![Smart India Hackathon](https://img.shields.io/badge/Smart%20India%20Hackathon-2024%20%2F%202026-orange.svg?style=for-the-badge)](#)
[![Organization: Govt of Jharkhand](https://img.shields.io/badge/Organization-Govt.%20of%20Jharkhand-138808.svg?style=for-the-badge)](#)
[![Branch: astifo](https://img.shields.io/badge/Branch-astifo-blue.svg?style=for-the-badge)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](#)

<p align="center">
  <b>Bridging the gap between 35+ million citizens and premier academic institutions & industries across all 24 districts of Jharkhand.</b>
</p>

</div>

---

## 📋 Problem Statement Reference

| Field | Detail |
|:---|:---|
| **S.No.** | **43** |
| **Organization** | **Government of Jharkhand** *(Department of Higher & Technical Education)* |
| **Problem Statement Title** | **A digital platform to crowdsource societal challenges and facilitate collaborative problem solving through universities and industry partnerships** |
| **Category** | **Software / Civic Tech / Smart Governance & AI** |
| **Theme** | **Citizen Engagement, Academic-Industry Collaboration & Public Innovation** |

---

## 🌟 The Vision & Core Differentiators

In traditional grievance systems, citizen complaints hit bureaucratic bottlenecks, duplicate reports waste manpower, and root systemic issues remain unsolved. 

**SocioSolve** transforms passive grievances into active community R&D and solution engineering:

1. 👥 **Multilingual Citizen Crowdsourcing**: Low-friction issue filing with voice/text (English, Hindi, and Hinglish), geolocation, photo evidence, and tracking codes.
2. 🤖 **Human-in-the-Loop AI Intelligence**: Real-time 384-dimensional semantic embeddings (`sentence-transformers`), automated domain clustering, field-intensity scoring, and **auditable duplicate detection** where AI recommends and officers decide.
3. 🏫 **University & Academic Research Integration**: Clustered challenges are converted into funded academic problem statements, student capstone projects, and faculty research grants across Jharkhand universities.
4. 🏭 **Industry & CSR Consortium Matching**: Intelligent capability-matching engine pairs universities with corporate partners for CSR funding, technical mentorship, equipment, and pilot rollouts.
5. 🛡️ **Zero-Tamper Auditability**: Complete state transitions, duplicate resolutions, and milestone verifications are enforced by database-level triggers into an append-only ledger.

---

## 🏛️ End-to-End Civic Life Cycle

```
[ Citizen Report ] ──> [ Geotag & Photo ] ──> [ AI Embedding & Domain Routing ]
                                                            │
                                                            ▼
                                           [ AI Duplicate Scoring Queue ]
                                                            │
                                             (Government Validator Decision)
                                            ┌───────────────┴───────────────┐
                                      [ DUPLICATE ]                   [ VALIDATED ]
                                     (Linked to Parent)                     │
                                                                            ▼
                                                                  [ Problem Cluster ]
                                                                            │
                                                       ┌────────────────────┴────────────────────┐
                                                       ▼                                         ▼
                                             [ Academic Consortium ]                   [ Industry Sponsorship ]
                                          (Faculty & Student Projects)              (CSR Capital & Pilot Testing)
                                                       │                                         │
                                                       └────────────────────┬────────────────────┘
                                                                            ▼
                                                               [ Verified Civic Solution ]
                                                              (Published & Field Deployed)
```

---

## 🏗️ System Architecture

The SocioSolve ecosystem is structured with strict network boundaries, stateless machine learning services, and asynchronous worker queues:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                      CLIENT TIER                                       │
│                                                                                        │
│   📱 Customer_App           🌐 citizen-portal                      🏢 client           │
│   (Flutter Mobile App)      (Next.js 16 / React 19)                (Next.js 14 Web)    │
│   Citizen Android/iOS       Public Reporting & Tracking            Govt / Univ / Ind   │
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │
                                           │ HTTPS / REST (Opaque Keyset Pagination)
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              FASTAPI CORE SERVER (:8000)                               │
│  - JWT Authentication & MSG91 OTP Widget Gateway                                       │
│  - Strict 5-Domain RBAC (Citizen, Government, University, Industry, Superadmin)        │
│  - Keyset Pagination (created_at DESC, id DESC) · Zero SQL OFFSET bottlenecks          │
│  - Transactional Service Layer & Immutable Audit Logger                                │
└──────────────────────┬───────────────────────────────────────────┬─────────────────────┘
                       │ (SQLAlchemy 2.0 Async / asyncpg)          │ (Internal HTTP)
                       ▼                                           ▼
┌──────────────────────────────────────────────┐       ┌─────────────────────────────────┐
│          PostgreSQL 16 + pgvector            │       │      ML INFERENCE SERVICE       │
│  - 384-dim HNSW Vector Cosine Indexes        │       │             (:8001)             │
│  - Hierarchical Administrative Areas         │       │  - all-MiniLM-L6-v2 Embeddings  │
│  - Database-enforced Append-only Triggers    │       │  - Duplicate Candidate Ranker   │
└──────────────────────────────────────────────┘       │  - Domain & Field Classifiers   │
                       ▲                               │  - Consortium Matcher Engine    │
                       │                               └─────────────────────────────────┘
┌──────────────────────┴───────────────────────┐
│             REDIS 7 + ARQ WORKER             │
│  - Async Cluster Centroid Computation        │
│  - Background Matching Notifications         │
└──────────────────────────────────────────────┘
```

---

## 📦 Directory Map

```text
SocioSolve/
├── citizen-portal/       # Next.js 16 + React 19 + Tailwind CSS v4 Citizen Web Application
├── Customer_App/         # Flutter Mobile App for Android & iOS (Dart 3.11+, Secure Storage)
├── client/               # Next.js 14 Institutional Web Portal (Govt, Univ, Industry, Admin)
├── server/               # FastAPI Async Backend, SQLAlchemy 2, ARQ Worker, Domain RBAC
│   ├── app/
│   │   ├── api/v1/       # Modular API routers (auth, challenges, clusters, matching...)
│   │   ├── models/       # Relational models with pgvector fields & immutable triggers
│   │   ├── services/     # Business logic, OTP provider integrations & audit logging
│   │   └── workers/      # ARQ Redis background jobs
│   └── tests/            # Unit and async integration test suites
├── ml/                   # Stateless Machine Learning Microservice (Sentence-Transformers)
│   ├── ai/               # Model weights, datasets, training scripts & evaluation benchmarks
│   ├── app/              # FastAPI endpoints for embeddings, classification & ranking
│   └── seed/             # Capability taxonomies & Jharkhand institution registries
├── database/             # Alembic migration source of truth & pgvector schema evolution
├── tests/                # Full-stack end-to-end live container test suite
├── docker-compose.yml    # Complete stack deployment orchestration
└── .env.example          # Environment blueprint with MSG91 DLT configuration notes
```

---

## 👥 Multi-Domain Roles & Permissions

Every account belongs to a designated **Domain** governed by strict database constraints:

| Domain | Allowed Roles | Primary Responsibilities |
|:---|:---|:---|
| **Citizen** | `citizen` | Submit geo-tagged challenges, receive SMS progress updates, view local solutions. |
| **Government** | `validator`<br>`field_assistant` | Validate challenges, review AI duplicate proposals, verify field deliverables across Jharkhand blocks & panchayats. |
| **University** | `coordinator`<br>`faculty` | Review civic clusters, assemble student teams, request research grants, submit deliverables. |
| **Industry** | `industry` | Allocate CSR funding, provide specialized lab equipment, sponsor technical mentors, pilot prototypes. |
| **Superadmin** | `superadmin` | Onboard verified institutions, configure administrative boundaries, monitor state-level analytics. |

---

## ⚡ Quick Start Guide

### 1. Prerequisites
- **Docker & Docker Compose** (v20+)
- **Node.js** (v20+) & `npm.cmd` (or `pnpm`)
- **Python** (3.11 or 3.12)
- **Flutter SDK** (3.11+ for mobile)

### 2. Environment Configuration
Copy the template and generate a local secret:
```powershell
cp .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(48))"
```
Set the generated key in `.env` under `SECRET_KEY`.

### 3. Launch Full Backend Stack via Docker
```powershell
docker compose up --build
```
This starts:
- **FastAPI Core**: `http://localhost:8000` (API Docs at `/api/v1/docs`)
- **ML Engine**: `http://localhost:8001` (Health check at `/health`)
- **PostgreSQL 16 + pgvector**: port `5433` (isolated network)
- **Redis 7 & ARQ Worker**: background job processing

### 4. Apply Database Migrations
In a second terminal:
```powershell
cd database
..\server\.venv\Scripts\python -m alembic -c alembic.ini upgrade head
```

---

## 💻 Running the Frontends

### Option A: Citizen Web Portal (Port 3000)
```powershell
cd citizen-portal
npm.cmd install
npm.cmd run dev
```
👉 Open **[http://localhost:3000](http://localhost:3000)** in your browser.

### Option B: Institutional Web Portal (Port 3001)
```powershell
cd client
npm.cmd install
npm.cmd run dev -- -p 3001
```
👉 Open **[http://localhost:3001](http://localhost:3001)** in your browser.

### Option C: Customer Mobile App (Android / iOS)
```powershell
cd Customer_App
flutter pub get
flutter run
```
*(On physical Android devices, bridge localhost port via `adb reverse tcp:8000 tcp:8000`)*

---

## 🧪 Comprehensive Verification Suite

```powershell
# 1. ML Microservice unit & integration tests
cd ml
python -m pytest -q

# 2. Server API, RBAC & Worker tests
cd ../server
python -m pytest -q

# 3. Full-stack end-to-end live testing
cd ..
SERVER_BASE_URL=http://localhost:8000/api/v1 python -m pytest tests/e2e -q
```

---

## 🔒 Security & Data Privacy Compliance

- **No Plaintext Passwords / OTPs**: Strict OTP verification using MSG91 Indian DLT compliant gateways with zero plaintext credential exposure.
- **Append-Only Immutability**: All civic state changes and duplicate review resolutions produce audit entries protected by PostgreSQL database triggers that reject `UPDATE` and `DELETE`.
- **Zero Leaks Standard**: Clean `.gitignore` guarantees local `.env.local` files, certificates, private keys, and temporary tokens are never committed.

---

<div align="center">
  <b>SocioSolve — Empowering Jharkhand Through Technology, Transparency & Collaboration</b><br>
  <i>Built for Smart India Hackathon · Maintained on branch <code>astifo</code></i>
</div>
