from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_admin
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserRead])
def list_users(
    role: Optional[UserRole] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> list:
    return user_service.list_users(db, role=role)


@router.post("", response_model=UserRead, status_code=201)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> UserRead:
    user = user_service.create_user(db, payload=payload, current_user=current_user)
    return UserRead.model_validate(user)


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: str,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> UserRead:
    user = user_service.get_user_or_404(db, user_id)
    updated = user_service.update_user(db, user=user, payload=payload, current_user=current_user)
    return UserRead.model_validate(updated)
