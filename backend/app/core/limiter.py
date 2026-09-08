"""Shared slowapi limiter instance.

Kept in its own module (rather than app.main) so route modules can apply
per-endpoint limits without a circular import.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import get_settings

settings = get_settings()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.RATE_LIMIT_DEFAULT],
    enabled=settings.ENVIRONMENT != "test",
)
