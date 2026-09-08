"""Password hashing and JWT token utilities."""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import bcrypt
import jwt

from app.core.config import get_settings

settings = get_settings()

TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def _create_token(subject: str, role: str, token_type: str, expires_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(user_id: str, role: str) -> str:
    return _create_token(
        user_id,
        role,
        TOKEN_TYPE_ACCESS,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(user_id: str, role: str) -> str:
    return _create_token(
        user_id,
        role,
        TOKEN_TYPE_REFRESH,
        timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
    )


class TokenError(Exception):
    pass


def decode_token(token: str, expected_type: Optional[str] = None) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        raise TokenError("Token has expired") from exc
    except jwt.InvalidTokenError as exc:
        raise TokenError("Token is invalid") from exc

    if expected_type and payload.get("type") != expected_type:
        raise TokenError("Unexpected token type")

    return payload
