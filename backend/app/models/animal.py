from datetime import date
from typing import Optional

from sqlalchemy import Date, Enum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin, new_uuid
from app.models.enums import AnimalStatus, Sex, Species


class Animal(Base, TimestampMixin):
    __tablename__ = "animals"
    __table_args__ = (UniqueConstraint("farm_id", "tag_id", name="uq_animal_farm_tag"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    farm_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tag_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    species: Mapped[Species] = mapped_column(Enum(Species, name="species"), nullable=False)
    breed: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    sex: Mapped[Sex] = mapped_column(Enum(Sex, name="sex"), nullable=False)
    dob: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[AnimalStatus] = mapped_column(
        Enum(AnimalStatus, name="animal_status"), nullable=False, default=AnimalStatus.active
    )
    photo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    farm = relationship("Farm", back_populates="animals")
    observations = relationship(
        "Observation", back_populates="animal", cascade="all, delete-orphan"
    )
    vaccination_records = relationship(
        "VaccinationRecord", back_populates="animal", cascade="all, delete-orphan"
    )
    cases = relationship("Case", back_populates="animal", cascade="all, delete-orphan")
