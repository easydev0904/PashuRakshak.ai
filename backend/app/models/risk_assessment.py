from sqlalchemy import Boolean, Enum, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin, new_uuid
from app.models.enums import RiskBand


class RiskAssessment(Base, TimestampMixin):
    __tablename__ = "risk_assessments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    observation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("observations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_band: Mapped[RiskBand] = mapped_column(
        Enum(RiskBand, name="risk_band"), nullable=False, index=True
    )
    top_factors_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    human_review_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    observation = relationship("Observation", back_populates="risk_assessment")
    alert = relationship(
        "Alert", back_populates="assessment", uselist=False, cascade="all, delete-orphan"
    )
