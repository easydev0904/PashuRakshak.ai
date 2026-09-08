from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin, new_uuid, utcnow
from app.models.enums import (
    ActivityLevel,
    AppetiteLevel,
    DungSign,
    RespiratorySign,
    WaterIntakeLevel,
)


class Observation(Base, TimestampMixin):
    __tablename__ = "observations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    animal_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("animals.id", ondelete="CASCADE"), nullable=False, index=True
    )
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )

    appetite: Mapped[AppetiteLevel] = mapped_column(
        Enum(AppetiteLevel, name="appetite_level"), nullable=False
    )
    activity: Mapped[ActivityLevel] = mapped_column(
        Enum(ActivityLevel, name="activity_level"), nullable=False
    )
    water_intake: Mapped[WaterIntakeLevel] = mapped_column(
        Enum(WaterIntakeLevel, name="water_intake_level"), nullable=False
    )
    respiratory_sign: Mapped[RespiratorySign] = mapped_column(
        Enum(RespiratorySign, name="respiratory_sign"), nullable=False
    )
    dung_sign: Mapped[DungSign] = mapped_column(Enum(DungSign, name="dung_sign"), nullable=False)

    temperature_c: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    milk_yield_change_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    entered_by: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    animal = relationship("Animal", back_populates="observations")
    risk_assessment = relationship(
        "RiskAssessment", back_populates="observation", uselist=False, cascade="all, delete-orphan"
    )
