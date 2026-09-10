# PashuRakshak AI

**Observe early. Act responsibly.**

SIH26128 — an early-warning, decision-support, and case-management
platform for livestock health, built for farmers and veterinarians.

## 1. Project overview

PashuRakshak AI helps a farmer notice potentially concerning patterns
in their animals earlier, and routes anything worth a closer look to
a veterinarian for review. It is a screening and workflow tool, not a
diagnostic device — see [docs/safety.md](docs/safety.md) for the
policy this is built around, and why "AI screening alert -
veterinarian assessment required" is the one sentence that appears
everywhere a HIGH-risk result does.

## 2. Problem statement (SIH26128)

Livestock disease often goes unnoticed until it's advanced, because
there's no lightweight way for a farmer to log daily observations,
have them screened for early warning signs, and get the right ones in
front of a veterinarian quickly. PashuRakshak AI is a software-only
prototype for that gap: farmer observation logging → AI early-warning
triage → veterinarian review and case management → prevention
education, with farm-level trend visibility for admins.

## 3. Architecture

See [docs/architecture.md](docs/architecture.md) for the full
breakdown. In short: a React frontend talks to a FastAPI backend over
REST; the backend imports the `ml/` package directly (no network hop)
for AI scoring; PostgreSQL is the only datastore. See
[docs/database.md](docs/database.md) and [docs/api.md](docs/api.md)
for the schema and endpoint reference.

## 4. Tech stack

**Frontend**: React 19, TypeScript, Vite, Tailwind CSS, shadcn-style
components, React Router, TanStack Query, React Hook Form + Zod,
react-i18next, lucide-react.

**Backend**: Python, FastAPI, SQLAlchemy, Alembic, Pydantic, PostgreSQL,
JWT auth, RBAC, slowapi (rate limiting).

**ML**: scikit-learn (logistic regression), pandas, numpy — a
calibrated statistical model combined with a transparent, documented
rule engine. See [docs/model-card.md](docs/model-card.md).

**Infra**: Docker, Docker Compose.

**Testing**: Vitest + React Testing Library (frontend), pytest
(backend + ml).

## 5. Folder structure

```
pashurakshak-ai/
├── docs/            architecture, database, api, security, safety, model-card, demo-flow, deployment,
│                    DEMO_GUIDE (handover walkthrough), SIH_PITCH (judge-facing story)
├── frontend/         React + TypeScript + Vite app
├── backend/           FastAPI app, Alembic migrations, pytest suite
├── ml/                 rule engine, feature engineering, training/eval, pytest suite
├── seed/               synthetic demo-data seed script
├── infra/docker/        nginx config for the frontend container
├── docker-compose.yml
└── .github/workflows/ci.yml
```

## 6. Setup

Two paths — pick one. Both are documented in full, with the exact
commands, in [docs/deployment.md](docs/deployment.md).

- **Docker Compose** (recommended, actually verified end-to-end — see
  §11 and the deployment doc for how): `cp .env.example .env`, then
  `docker compose up --build`.
- **Local dev without Docker**: Postgres via Homebrew (or any local
  Postgres 16), a Python 3.9+ venv for the backend, `npm install` for
  the frontend. Full commands in the deployment doc.

## 7. Environment variables

See `.env.example` (repo root, shared reference) and
`backend/.env.example` / `frontend/.env.example` for what each service
reads. Never commit a real `.env` file — copy the example and fill in
real values (especially `JWT_SECRET_KEY` and `POSTGRES_PASSWORD`)
locally.

## 8. Database migration

```bash
cd backend
alembic upgrade head
```

One migration today (`cc6d8af7c933_initial_schema.py`), creating all
13 tables plus the composite indexes the app's actual query patterns
need. See [docs/database.md](docs/database.md).

## 9. Seed data

```bash
python seed/seed_data.py
```

**Destructive** — resets and rebuilds a consistent synthetic demo
dataset (see the script's own docstring). Creates 5 demo users across
all three roles (password `Demo@1234` for all — see
[docs/demo-flow.md](docs/demo-flow.md) for the full list and the
walkthrough it's built to support), 2 farms, 11 animals with real
observation histories (submitted through the actual scoring service,
so every alert is genuinely AI-produced, not hand-inserted),
vaccination records, cases in all four workflow states (open, under
review, follow-up, resolved), and 12 bilingual education-content
entries.

## 10. Running locally

```bash
# backend (from backend/, with its venv active)
uvicorn app.main:app --reload

# frontend (from frontend/, separate terminal)
npm run dev
```

Frontend at `http://localhost:5173`, backend at
`http://localhost:8000` (`/docs` for interactive API docs).

## 11. Running with Docker

```bash
cp .env.example .env
docker compose up --build
```

Frontend at `http://localhost:8080`, backend at
`http://localhost:8000`. This was run for real during development,
not just written and assumed to work — see
[docs/deployment.md](docs/deployment.md) for what was verified and one
real gotcha (a native-Postgres port conflict) it caught.

## 12. Demo accounts

| Role | Email | Password |
|---|---|---|
| Farmer | `farmer.demo@pashurakshak.ai` | `Demo@1234` |
| Farmer (2nd farm) | `farmer2.demo@pashurakshak.ai` | `Demo@1234` |
| Veterinarian | `vet.demo@pashurakshak.ai` | `Demo@1234` |
| Veterinarian (2nd) | `vet2.demo@pashurakshak.ai` | `Demo@1234` |
| Admin | `admin.demo@pashurakshak.ai` | `Demo@1234` |

Created by `seed/seed_data.py`; the login page also shows these and
fills the form in on click.

## 13. API documentation

Interactive docs (Swagger UI) at `/docs` on the running backend; a
quick-reference table of every endpoint, its auth requirement, and
notes is in [docs/api.md](docs/api.md).

## 14. Safety disclaimer

This system is a screening and decision-support tool, **not** a
diagnostic device. It never presents an AI prediction as a confirmed
disease — every HIGH-risk result displays exactly: *"AI screening
alert - veterinarian assessment required."* A veterinarian, not the
software, confirms any diagnosis. Full policy: [docs/safety.md](docs/safety.md).

## 15. ML limitations

The shipped model is trained **entirely on synthetic data** and is
explicitly a prototype — not validated for clinical or field
deployment, and no accuracy number in this repo should be quoted as a
real-world performance claim. Full details, methodology, and honest
evaluation numbers (including where subgroup performance differs): [docs/model-card.md](docs/model-card.md).

## 16. Testing

```bash
# frontend
cd frontend && npm run test

# backend
cd backend && pytest tests/ -q

# ml
PYTHONPATH=. pytest ml/tests -q   # from repo root
```

All three suites pass as of this writing — 67 backend, 31 ml, 17
frontend (115 total). Coverage spans RBAC/farm-isolation boundaries, validation
edge cases (impossible temperature/milk-yield values, expired/
mistyped JWTs, missing model artifact, duplicate tags, unauthorized
cross-farm access), the full scoring contract, offline-draft sync, and
component-level UI behavior. See [docs/security.md](docs/security.md)
for which security properties are backed by a specific test versus a
live manual check.

## 17. Deployment

[docs/deployment.md](docs/deployment.md) — Docker Compose (verified)
and local-dev-without-Docker paths, environment variables, and CI.

## SIH showcase handover

Handing this project to someone else to present? Two docs are written
specifically for that:

- [docs/DEMO_GUIDE.md](docs/DEMO_GUIDE.md) — a complete, no-code-
  required walkthrough: how to start the app, exactly what to click,
  which seeded animals to use, a backup plan if the live demo breaks,
  and answers to likely judge questions.
- [docs/SIH_PITCH.md](docs/SIH_PITCH.md) — the problem/solution story
  in plain language, for framing the pitch itself.

## 18. Future improvements

- Real, ethically-collected labeled training data reviewed by
  veterinary domain experts, replacing the synthetic dataset.
- A proper consent-capture flow for `Farm.consent_version` (currently
  a stored flag, not an enforced workflow — see
  [docs/security.md](docs/security.md#known-limitations-prototype-scope)).
- S3-compatible upload storage (the `StorageBackend` interface exists
  specifically so this is a one-class addition, not a rewrite).
- Region/location-aware analytics, once real location data exists to
  analyze responsibly.
- A shared (Redis-backed) rate limiter for multi-instance deployment.
