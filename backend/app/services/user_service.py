from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.core.security import hash_password
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services import audit_service


def list_users(db: Session, *, role: Optional[UserRole] = None) -> list:
    stmt = select(User).order_by(User.created_at.desc())
    if role:
        stmt = stmt.where(User.role == role)
    return list(db.execute(stmt).scalars().all())


def get_user_or_404(db: Session, user_id: str) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise NotFoundError("This user could not be found.")
    return user


def create_user(db: Session, *, payload: UserCreate, current_user: User) -> User:
    user = User(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        role=payload.role,
        language=payload.language,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("A user with this email or phone already exists.") from exc

    audit_service.record(
        db,
        actor_id=current_user.id,
        entity_type="user",
        entity_id=user.id,
        action="create",
        metadata={"role": user.role.value},
    )
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, *, user: User, payload: UserUpdate, current_user: User) -> User:
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(user, key, value)
    db.add(user)
    audit_service.record(
        db,
        actor_id=current_user.id,
        entity_type="user",
        entity_id=user.id,
        action="update",
        metadata=updates,
    )
    db.commit()
    db.refresh(user)
    return user
