from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from app.models.enums import Language, UserRole


class UserBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, min_length=6, max_length=20)
    language: Language = Language.en


class UserCreate(UserBase):
    role: UserRole
    password: str = Field(min_length=8, max_length=128)

    @model_validator(mode="after")
    def _require_identifier(self) -> "UserCreate":
        if not self.email and not self.phone:
            raise ValueError("Either email or phone is required")
        return self


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    role: UserRole
    is_active: bool


class UserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    language: Optional[Language] = None
    is_active: Optional[bool] = None
