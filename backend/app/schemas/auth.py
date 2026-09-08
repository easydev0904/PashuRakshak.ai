from typing import Optional

from pydantic import BaseModel, Field, model_validator

from app.schemas.user import UserRead


class LoginRequest(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    password: str = Field(min_length=1)

    @model_validator(mode="after")
    def _require_identifier(self) -> "LoginRequest":
        if not self.email and not self.phone:
            raise ValueError("Either email or phone is required")
        return self


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserRead


class RefreshRequest(BaseModel):
    refresh_token: str
