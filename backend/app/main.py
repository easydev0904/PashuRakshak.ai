from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.routes import (
    alerts,
    analytics,
    animals,
    audit_logs,
    auth,
    cases,
    education,
    farms,
    uploads,
    users,
)
from app.core.config import get_settings
from app.core.errors import AppError
from app.core.limiter import limiter
from app.db import base as _models  # noqa: F401  (registers all ORM models before first query)
from app.services.storage import LocalStorageBackend

settings = get_settings()

app = FastAPI(
    title="PashuRakshak AI",
    description=(
        "Livestock early-warning and case-management platform. "
        "This system provides AI screening support, not a medical diagnosis."
    ),
    version="0.1.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.UPLOAD_STORAGE_BACKEND == "local":
    _local_storage = LocalStorageBackend(settings.UPLOAD_DIR)
    app.mount("/uploads", StaticFiles(directory=_local_storage.base_dir), name="uploads")


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Some of the information provided is not valid.",
            "errors": jsonable_encoder(exc.errors()),
        },
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"detail": "Something went wrong on our end. Please try again shortly."},
    )


@app.get("/health", tags=["system"])
def health_check() -> dict:
    return {"status": "ok", "environment": settings.ENVIRONMENT}


app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(farms.router, prefix=settings.API_V1_PREFIX)
app.include_router(animals.router, prefix=settings.API_V1_PREFIX)
app.include_router(alerts.router, prefix=settings.API_V1_PREFIX)
app.include_router(cases.router, prefix=settings.API_V1_PREFIX)
app.include_router(education.router, prefix=settings.API_V1_PREFIX)
app.include_router(analytics.router, prefix=settings.API_V1_PREFIX)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(audit_logs.router, prefix=settings.API_V1_PREFIX)
app.include_router(uploads.router, prefix=settings.API_V1_PREFIX)
