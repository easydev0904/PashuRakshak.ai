from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.errors import AuthenticationError
from app.core.limiter import limiter
from app.core.security import TOKEN_TYPE_REFRESH, TokenError, create_access_token, decode_token
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse
from app.schemas.user import UserRead
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
def login(request: Request, payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = auth_service.authenticate(
        db, email=payload.email, phone=payload.phone, password=payload.password
    )
    access_token, refresh_token = auth_service.issue_tokens(user)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserRead.model_validate(user),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    try:
        decoded = decode_token(payload.refresh_token, expected_type=TOKEN_TYPE_REFRESH)
    except TokenError as exc:
        raise AuthenticationError("Your session has expired. Please log in again.") from exc

    user = db.get(User, decoded.get("sub"))
    if user is None or not user.is_active:
        raise AuthenticationError("Your account is not available. Please contact an administrator.")

    access_token = create_access_token(user.id, user.role.value)
    return TokenResponse(
        access_token=access_token,
        refresh_token=payload.refresh_token,
        user=UserRead.model_validate(user),
    )


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)
