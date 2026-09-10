from datetime import date
from typing import Optional

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin, new_uuid


class VaccinationRecord(Base, TimestampMixin):
    __tablename__ = "vaccination_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    animal_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("animals.id", ondelete="CASCADE"), nullable=False, index=True
    )
    vaccine_name: Mapped[str] = mapped_column(String(150), nullable=False)
    dose_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    administered_by: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    evidence_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    animal = relationship("Animal", back_populates="vaccination_records")
