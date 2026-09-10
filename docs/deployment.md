# Deployment

## Docker Compose (recommended)

```bash
cp .env.example .env   # adjust POSTGRES_PASSWORD / JWT_SECRET_KEY at minimum
docker compose up --build
```

This starts three containers:

- `postgres` (16-alpine) — healthchecked; the other services wait for it.
- `backend` — trains the baseline model at *image build time*
  (`python -m ml.src.train`, so the container is self-contained),
  then on every container start runs `alembic upgrade head` before
  starting `uvicorn` on port 8000.
- `frontend` — a static production build (`vite build`) served by
  nginx on port 8080. `VITE_API_BASE_URL` is baked in at build time
  (Vite env vars are compile-time, not runtime) via a build arg.

Once up: frontend at `http://localhost:8080`, backend at
`http://localhost:8000` (Swagger docs at `/docs`).

Seed demo data (destructive — see the script's docstring):

```bash
DATABASE_URL="postgresql+psycopg://pashurakshak:<your-password>@localhost:5432/pashurakshak" \
  python seed/seed_data.py
```

**This was actually run, not just written.** Docker wasn't available in
the sandbox this project was built in, so a real Docker daemon
(colima, via Homebrew) was installed specifically to verify `docker
compose up --build` end-to-end: both images built, all three
containers started healthy, migrations created all 13 tables, the
seed script populated the containerized Postgres, login and API calls
worked against the containerized backend, and the nginx-served
frontend loaded in a browser and correctly authenticated against it.

### ⚠️ Port 5432 conflict on a dev machine

If you also run PostgreSQL natively on the same machine (e.g. via
Homebrew, as this project's own dev environment does), it will likely
already be bound to `localhost:5432` — and macOS will let Docker's
port-forward bind to `5432` too without erroring, because Docker
Desktop/colima's forwarder binds `0.0.0.0` while a natively-running
Postgres often binds only the loopback interface specifically. The
result: `psql -h localhost -p 5432` (and anything else connecting to
`localhost:5432`) silently reaches your **native** Postgres, not the
container's — no error, just the wrong database. This is exactly what
happened once during this project's own Docker verification.

If your API calls or seed script behave unexpectedly against the
Docker stack, check for this first:

```bash
lsof -i :5432
```

If you see two processes, stop the native one for the duration of your
Docker testing (`brew services stop postgresql@16` on macOS/Homebrew),
or change `docker-compose.yml`'s postgres port mapping to something
else, e.g. `"5433:5432"`.

## Local development (without Docker)

Used for the majority of this project's own development.

```bash
# Postgres (Homebrew example)
brew install postgresql@16
brew services start postgresql@16
createuser pashurakshak --createdb
psql -d postgres -c "ALTER USER pashurakshak WITH PASSWORD 'pashurakshak_dev_pw';"
createdb -O pashurakshak pashurakshak
createdb -O pashurakshak pashurakshak_test

# Backend
cd backend
python3.11 -m venv .venv && source .venv/bin/activate   # 3.9+ also works, see note below
pip install -r requirements-dev.txt
cp ../.env.example .env   # then edit DATABASE_URL/JWT_SECRET_KEY for local values
alembic upgrade head
python -m ml.src.train    # from repo root: PYTHONPATH=. python -m ml.src.train
uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

> **Python version note**: this project's own dev environment ended up
> on Python 3.9 (the system Python) rather than a newer Homebrew
> Python, because the available Homebrew Python 3.11 bottle had a
> broken `pyexpat` linkage against the host OS's system `libexpat` at
> the time of building this (an environment-specific bottle/OS
> mismatch, not a project issue). The codebase avoids Python 3.10+-only
> syntax (e.g. `X | Y` union types) specifically so it runs on 3.9+.
> Use whatever Python 3.9+ interpreter works cleanly in your
> environment — newer is fine too.

## Environment variables

See `.env.example` at the repo root (shared reference) and
`backend/.env.example` / `frontend/.env.example` for the values each
service actually reads. Never commit a real `.env` — both are
gitignored.

## CI

`.github/workflows/ci.yml` runs on every push/PR: frontend install,
lint, typecheck, test, build; backend dependency install, ruff, mypy,
pytest (against a Postgres service container); ml/ pytest. See the
workflow file for the exact matrix.
