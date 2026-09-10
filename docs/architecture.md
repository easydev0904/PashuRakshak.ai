# Architecture

## System overview

```
┌─────────────────┐        ┌──────────────────────┐        ┌─────────────────┐
│  React frontend  │ HTTPS │   FastAPI backend     │        │   ml/ package    │
│  (Vite, TS, TW)   │◄─────►│   (JWT auth, RBAC)    │◄──────►│  rules + model   │
└─────────────────┘  REST  └──────────┬────────────┘  in-   └─────────────────┘
                                       │            process
                                       │ SQLAlchemy   call
                                       ▼
                              ┌─────────────────┐
                              │   PostgreSQL     │
                              └─────────────────┘
```

`ml/` is not a network service — the backend imports it directly as a
Python package (see `backend/app/services/risk_service.py`, the only
module in the backend that touches `ml.*`). This keeps the demo simple
(no extra service to deploy or that can fail independently) while
still letting `ml/` be trained, tested, and evaluated in complete
isolation from the API — `python -m ml.src.train` and
`pytest ml/tests` never import anything from `backend/`.

## Backend layering

```
app/api/routes/*      thin route handlers: parse request, call a service, shape the response
app/services/*        business logic, authorization checks, ORM writes
app/models/*           SQLAlchemy ORM models
app/schemas/*           Pydantic request/response schemas
app/core/*               config, security (JWT/bcrypt), error types, rate limiter
```

Routes are deliberately thin. All authorization lives in
`app/services/authz.py`, which every animal/observation/alert/case/
vaccination service function calls before touching data — this is the
single choke point for farm-isolation, not something re-implemented
per route.

### Request flow: submitting an observation

1. `POST /animals/{id}/observations` (`app/api/routes/animals.py`)
   authenticates the caller and calls `assert_animal_access`.
2. `app/services/observation_service.create_observation` fetches the
   animal's recent history, creates the `Observation` row, and calls
   `risk_service.score_observation`.
3. `risk_service` translates the ORM objects into the plain dicts
   `ml.src.predict.assess` expects, and translates its result back into
   an ORM-ready `RiskAssessment`.
4. `ml.src.predict.assess` runs the rule engine and the trained model,
   combines them (a rule can only push risk *up*), and returns a
   band/score/factors/disclaimer.
5. If the band is MEDIUM or HIGH, `observation_service` also creates an
   `Alert` row.
6. Every step writes an `AuditLog` entry.

## Frontend structure

```
src/api/          axios client, token storage, auto-refresh interceptor
src/services/      one file per backend resource, thin fetch wrappers
src/hooks/          TanStack Query hooks wrapping services (caching, invalidation)
src/pages/           route-level components, organized by role (farmer/vet/admin/shared)
src/components/ui/   shadcn-style primitives (Button, Card, Input, ...)
src/components/shared/  cross-role composed components (RiskBadge, AnimalCard, ...)
src/store/            AuthContext (JWT session state)
src/i18n/              react-i18next setup + en/hi translation JSON
```

Routing (`App.tsx`) wraps every authenticated route in `ProtectedRoute`
with an explicit `roles` allowlist — the frontend route guard is a UX
convenience; the backend RBAC checks are the actual enforcement
boundary (see [security.md](security.md)).

## Data flow: farm isolation

A farmer's queries are scoped to farms they have a `FarmMembership`
row for. Veterinarians and admins get broader read access (a vet
triages across farms, not just one) — this is a role-based design
choice made explicit in `app/services/authz.py::assert_farm_access`,
not an oversight. See [security.md](security.md) for how this is
tested.

## Why no microservices

Everything (backend, frontend, database) runs as three containers via
one `docker-compose.yml`. `ml/` is a Python package, not a service.
This is deliberate: the spec explicitly asks for reliability and easy
local setup over premature infrastructure complexity for what is a
hackathon prototype, not a production system with independent scaling
needs per component.
