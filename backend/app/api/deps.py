"""Shared FastAPI dependencies: DB session, current user, RBAC guards."""

from collections.abc import Generator

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.errors import AuthenticationError, AuthorizationError
from app.core.security import TOKEN_TYPE_ACCESS, TokenError, decode_token
from app.db.session import SessionLocal
from app.models.enums import UserRole
from app.models.user import User


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _extract_bearer_token(authorization: str) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise AuthenticationError("Please log in to continue.")
    return authorization.split(" ", 1)[1].strip()


def get_current_user(
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
) -> User:
    token = _extract_bearer_token(authorization)
    try:
        payload = decode_token(token, expected_type=TOKEN_TYPE_ACCESS)
    except TokenError as exc:
        raise AuthenticationError("Your session has expired. Please log in again.") from exc

    user = db.get(User, payload.get("sub"))
    if user is None or not user.is_active:
        raise AuthenticationError("Your account is not available. Please contact an administrator.")
    return user


def require_roles(*roles: UserRole):
    def _dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise AuthorizationError("You do not have permission to do that.")
        return current_user

    return _dependency


require_farmer = require_roles(UserRole.farmer)
require_veterinarian = require_roles(UserRole.veterinarian)
require_admin = require_roles(UserRole.admin)
require_vet_or_admin = require_roles(UserRole.veterinarian, UserRole.admin)
