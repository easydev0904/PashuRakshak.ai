# API Reference

Base URL: `{API_V1_PREFIX}` (default `/api/v1`). Interactive docs are
served by FastAPI itself at `/docs` (Swagger UI) and `/redoc` whenever
the backend is running — this file is a quick-reference companion, not
a replacement.

**Auth**: send `Authorization: Bearer <access_token>` on every route
except `/auth/login` and `/auth/refresh`. Tokens come from `/auth/login`.

**Errors**: every error response is `{"detail": "<friendly message>"}`,
optionally with an `"errors"` array for validation failures. Raw
exceptions, stack traces, and internal paths are never returned — see
[security.md](security.md).

## Auth

| Method | Path | Auth | Notes |
|---|---|---|---|
| POST | `/auth/login` | — (rate-limited 10/min) | `{email\|phone, password}` → tokens + user |
| POST | `/auth/refresh` | — | `{refresh_token}` → new access token |
| GET | `/auth/me` | any | current user |

## Farms

| Method | Path | Auth | Notes |
|---|---|---|---|
| GET | `/farms` | any | farmer: own farms; vet/admin: all farms |
| POST | `/farms` | any | creates a farm and a membership for the caller |

## Animals

| Method | Path | Auth | Notes |
|---|---|---|---|
| GET | `/animals` | any | optional `?farm_id=` filter; farm-scoped by role |
| POST | `/animals` | any | `409` on duplicate `(farm_id, tag_id)` |
| GET | `/animals/{id}` | any | includes derived `last_risk_band`, `needs_checkin_today` |
| GET | `/animals/{id}/observations` | any | newest first, each with its nested `risk_assessment` |
| POST | `/animals/{id}/observations` | any | runs the AI scoring contract; may create an `Alert` |
| GET | `/animals/{id}/vaccinations` | any | |
| POST | `/animals/{id}/vaccinations` | any | |
| GET | `/animals/{id}/cases` | any | |
| POST | `/animals/{id}/cases` | vet/admin | opens a case outside the alert-review flow |

## Alerts

| Method | Path | Auth | Notes |
|---|---|---|---|
| GET | `/alerts` | any | filters: `status`, `priority`, `farm_id`, `assigned_vet_id` |
| GET | `/alerts/{id}` | any | full context: animal, observation, risk assessment, farm name |
| PATCH | `/alerts/{id}` | vet/admin | same effect as `/review` below |
| POST | `/alerts/{id}/review` | vet/admin | `{action, assigned_vet_id?, note?, follow_up_at?}`; `action` ∈ `acknowledge, assign, request_follow_up, resolve` — `request_follow_up` opens/updates a case |

## Cases

| Method | Path | Auth | Notes |
|---|---|---|---|
| GET | `/cases/{id}` | any | includes `updates` |
| PATCH | `/cases/{id}` | vet/admin | the **only** path that can set `confirmed_condition` |
| POST | `/cases/{id}/updates` | vet/admin | adds a clinical note; setting `next_follow_up_at` moves status to `follow_up` |

## Education (Prevention library)

| Method | Path | Auth | Notes |
|---|---|---|---|
| GET | `/education` | — (public) | published only; filters: `language`, `category`, `audience` |
| GET | `/education/{id}` | — (public) | |
| GET | `/education/admin/all` | admin | includes unpublished drafts |
| POST | `/education` | admin | |
| PATCH | `/education/{id}` | admin | |

## Analytics

| Method | Path | Auth | Notes |
|---|---|---|---|
| GET | `/analytics/farm-trends?farm_id=` | any | stats + 30-day daily trend; response always includes a non-outbreak-claim `note` |

## Admin

| Method | Path | Auth | Notes |
|---|---|---|---|
| GET | `/users` | admin | optional `?role=` filter |
| POST | `/users` | admin | creates a user (role fixed at creation) |
| PATCH | `/users/{id}` | admin | `name`, `language`, `is_active` only — role is not editable post-creation |
| GET | `/audit-logs` | admin | filters: `entity_type`, `action`, `actor_id`, `limit` (max 200) |

## Uploads

| Method | Path | Auth | Notes |
|---|---|---|---|
| POST | `/uploads` | any | `multipart/form-data`, field `file`; JPEG/PNG/WEBP only, ≤5MB; returns `{"url": "/uploads/<generated-name>.<ext>"}` |

Uploaded files are served back from `/uploads/<filename>` (outside the
`/api/v1` prefix, mounted as static files) — that URL is relative to
the **backend's** origin, which matters in dev where the frontend runs
on a different port (see `resolveMediaUrl` in the frontend).

## System

| Method | Path | Auth |
|---|---|---|
| GET | `/health` | — |

## Risk assessment response shape

Every endpoint that returns a risk assessment (observation submission,
observation list, alert detail) uses the same shape:

```json
{
  "risk_score": 0.42,
  "risk_band": "medium",
  "top_factors": [
    {"rule": "appetite_reduction", "reason": "Reported appetite is below normal", "severity": "medium"}
  ],
  "model_version": "prototype-v1",
  "human_review_required": false,
  "clinical_disclaimer": "AI screening alert - veterinarian assessment required."
}
```

There is no `diagnosis`, `treatment`, or `prescription` field — see
[safety.md](safety.md).
