from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin, new_uuid
from app.models.enums import CaseStatus


class Case(Base, TimestampMixin):
    __tablename__ = "cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    animal_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("animals.id", ondelete="CASCADE"), nullable=False, index=True
    )
    alert_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("alerts.id", ondelete="SET NULL"), nullable=True, unique=True
    )
    status: Mapped[CaseStatus] = mapped_column(
        Enum(CaseStatus, name="case_status"), nullable=False, default=CaseStatus.open, index=True
    )
    suspected_condition: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    confirmed_condition: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    confirmation_basis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    opened_by: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    animal = relationship("Animal", back_populates="cases")
    alert = relationship("Alert", back_populates="case")
    updates = relationship("CaseUpdate", back_populates="case", cascade="all, delete-orphan")


class CaseUpdate(Base, TimestampMixin):
    __tablename__ = "case_updates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    case_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    note: Mapped[str] = mapped_column(Text, nullable=False)
    next_follow_up_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    case = relationship("Case", back_populates="updates")
