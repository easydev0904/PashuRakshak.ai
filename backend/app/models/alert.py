from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin, new_uuid
from app.models.enums import AlertPriority, AlertStatus


class Alert(Base, TimestampMixin):
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    assessment_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("risk_assessments.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    priority: Mapped[AlertPriority] = mapped_column(
        Enum(AlertPriority, name="alert_priority"), nullable=False, index=True
    )
    status: Mapped[AlertStatus] = mapped_column(
        Enum(AlertStatus, name="alert_status"), nullable=False, default=AlertStatus.open, index=True
    )
    assigned_vet_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    assessment = relationship("RiskAssessment", back_populates="alert")
    assigned_vet = relationship("User", foreign_keys=[assigned_vet_id])
    case = relationship("Case", back_populates="alert", uselist=False)
