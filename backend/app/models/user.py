from typing import Optional

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin, new_uuid
from app.models.enums import Language, UserRole


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True, index=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), nullable=False)
    language: Mapped[Language] = mapped_column(
        Enum(Language, name="language"), nullable=False, default=Language.en
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    farm_memberships = relationship(
        "FarmMembership", back_populates="user", cascade="all, delete-orphan"
    )
