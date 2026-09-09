# Security

PashuRakshak AI is a prototype, but the security controls below are real
and verified, not aspirational. Everything marked ✅ was exercised
either by an automated test or a live manual check during development
(both are cited).

## Authentication

- **Password hashing**: bcrypt (`app/core/security.py`), via the
  standalone `bcrypt` package (not `passlib`, which has known
  incompatibilities with recent `bcrypt` releases).
- **JWT**: HS256, signed with `JWT_SECRET_KEY`. Access tokens
  (60 min default) and refresh tokens (7 days default) are separate
  token *types* (`"type": "access" | "refresh"` claim) — a refresh
  token cannot be used to call any API route, and an access token
  cannot be used to mint a new one. ✅ `tests/test_auth.py::test_refresh_token_cannot_be_used_as_access_token`
- **Expiry is enforced**, not just set. ✅
  `test_expired_access_token_rejected`, `test_expired_refresh_token_rejected`
- **Rate limiting** on `/auth/login` (10/minute per IP, via `slowapi`).
  Verified live: 11th login attempt within a minute returns `429`.

## Authorization (RBAC + farm isolation)

- Every route depends on `get_current_user` or a role-scoped variant
  (`require_admin`, `require_vet_or_admin`, ...) from `app/api/deps.py`.
  Role checks happen **server-side only** — the frontend hiding a button
  is a UX nicety, never the enforcement boundary.
- **Farm isolation** is centralized in `app/services/authz.py`
  (`assert_farm_access`, `assert_animal_access`) — the single choke
  point every animal/observation/alert/case/vaccination route calls
  before touching data. A farmer can never read or write another
  farm's data by changing an ID in the URL; veterinarians and admins
  get intentional cross-farm read access (they triage across the
  referral network), scoped by role, not by trusting client input.
  ✅ Exercised in `test_animals.py`, `test_observations.py`,
  `test_vaccinations.py`, `test_analytics.py` (farmer → 403 on another
  farm's resources).
- Case `confirmed_condition` / `confirmation_basis` can only be set via
  vet/admin-gated endpoints; the AI scoring path never writes them. ✅
  `test_alerts_and_cases.py::test_farmer_cannot_set_confirmed_condition`

## Data validation

- All request bodies are validated by Pydantic schemas.
- Observation `temperature_c` and `milk_yield_change_pct` are bounded to
  physically plausible ranges (not clinical thresholds — see
  `app/schemas/observation.py` for the documented distinction), rejecting
  impossible sensor input rather than silently accepting it.
- No raw SQL string interpolation anywhere in the codebase — every
  query goes through SQLAlchemy's ORM/Core query builder, which
  parameterizes values automatically.

## File uploads

- MIME whitelist (`image/jpeg`, `image/png`, `image/webp`) — checked
  against the browser-reported `Content-Type`, not the filename.
- Size capped at `MAX_UPLOAD_SIZE_MB` (default 5MB), enforced while
  *streaming* the body (never buffers an unbounded upload into memory).
- **Filenames are always server-generated** (`uuid4().hex` + an
  extension chosen from the validated content type) — the client's
  filename is never used to build a filesystem path. This is what
  actually prevents path traversal, not string-matching for `".."`.
  ✅ `test_uploads.py::test_upload_filename_never_uses_client_supplied_name`
  sends a `../../etc/passwd.png` filename and confirms it never reaches
  the stored path.
- Served back from a dedicated `/uploads` static mount, isolated from
  application code and the database.

## Error handling

- Three global exception handlers in `app/main.py` guarantee no raw
  exception, stack trace, or internal path ever reaches a client:
  domain errors (`AppError` subclasses) return their own friendly
  message; Pydantic validation errors are reformatted; anything else
  falls through to a generic "something went wrong" 500. ✅
  `test_observations.py::test_missing_model_artifact_returns_friendly_error_not_stack_trace`
  simulates a missing model file and confirms the response contains
  neither the file path nor `"joblib"`.

## CORS

- Configured via `BACKEND_CORS_ORIGINS` (defaults to the local dev
  frontend origins only). Verified live: a cross-origin OPTIONS
  preflight from an unlisted origin is rejected with
  `"Disallowed CORS origin"`.

## Audit logging

- Every state-changing service call writes an `AuditLog` row
  (`app/services/audit_service.py`) — actor, entity type/id, action,
  and a small metadata blob. Covers logins, farm/animal/observation
  creation, risk assessments, alert lifecycle, case updates,
  vaccination records, and admin actions. Readable only by admins via
  `GET /audit-logs`. Verified live by seeding data and reviewing the
  resulting trail through the admin UI.

## AI-specific safety boundaries

See [safety.md](safety.md) for the full policy; the security-relevant
summary is that the risk-scoring response schema
(`RiskAssessmentRead`) has no field for a diagnosis, treatment, or
prescription — it structurally cannot leak one, not just "is told not
to." ✅ `test_never_returns_diagnosis_or_treatment_fields`

## Known limitations (prototype scope)

- `Farm.consent_version` is stored but not yet enforced by a consent
  capture flow — acceptable for the SIH demo's synthetic data, called
  out here so it isn't mistaken for a finished consent system.
- No email/SMS-based account recovery flow exists; demo accounts have
  fixed credentials documented in the README.
- Rate limiting is a single in-memory limiter (per `slowapi` defaults)
  — fine for a single-instance prototype, would need a shared backend
  (Redis) behind a load balancer in production.
- Local disk is the only implemented storage backend for uploads; the
  `StorageBackend` interface exists specifically so S3 can be added
  without touching callers, but no S3 implementation exists yet.
