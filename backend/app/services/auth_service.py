from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import AuthenticationError
from app.core.security import create_access_token, create_refresh_token, verify_password
from app.models.user import User
from app.services import audit_service


def get_user_by_identifier(
    db: Session, *, email: Optional[str], phone: Optional[str]
) -> Optional[User]:
    stmt = select(User)
    if email:
        stmt = stmt.where(User.email == email)
    elif phone:
        stmt = stmt.where(User.phone == phone)
    else:
        return None
    return db.execute(stmt).scalar_one_or_none()


def authenticate(db: Session, *, email: Optional[str], phone: Optional[str], password: str) -> User:
    user = get_user_by_identifier(db, email=email, phone=phone)
    if user is None or not verify_password(password, user.password_hash):
        raise AuthenticationError("Incorrect credentials. Please check and try again.")
    if not user.is_active:
        raise AuthenticationError("This account has been deactivated.")

    audit_service.record(
        db,
        actor_id=user.id,
        entity_type="user",
        entity_id=user.id,
        action="login",
        metadata={"method": "password"},
    )
    db.commit()
    return user


def issue_tokens(user: User) -> tuple[str, str]:
    access_token = create_access_token(user.id, user.role.value)
    refresh_token = create_refresh_token(user.id, user.role.value)
    return access_token, refresh_token
