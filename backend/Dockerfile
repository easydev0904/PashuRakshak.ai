# Build context is the REPO ROOT (not backend/), because the backend
# imports the sibling ml/ package directly at runtime (see
# app/services/risk_service.py) -- both directories need to be copied
# into the image. See docker-compose.yml's `build.context`.

FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /repo

# System deps needed to build psycopg's C extension.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt backend/requirements.txt
RUN pip install -r backend/requirements.txt

COPY ml/ ml/
COPY backend/ backend/

WORKDIR /repo/backend

# Train the baseline model at image build time so the container is
# self-contained and reproducible -- the artifact is a build product
# (gitignored), never checked into source control.
RUN PYTHONPATH=/repo python -m ml.src.train

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
