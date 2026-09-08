from typing import Optional

from sqlalchemy import Enum, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin, new_uuid
from app.models.enums import UserRole


class Farm(Base, TimestampMixin):
    __tablename__ = "farms"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    village: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    district: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    consent_version: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    memberships = relationship(
        "FarmMembership", back_populates="farm", cascade="all, delete-orphan"
    )
    animals = relationship("Animal", back_populates="farm", cascade="all, delete-orphan")


class FarmMembership(Base, TimestampMixin):
    __tablename__ = "farm_memberships"
    __table_args__ = (UniqueConstraint("farm_id", "user_id", name="uq_farm_membership"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    farm_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), nullable=False)

    farm = relationship("Farm", back_populates="memberships")
    user = relationship("User", back_populates="farm_memberships")
