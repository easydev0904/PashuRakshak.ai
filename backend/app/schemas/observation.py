from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import (
    ActivityLevel,
    AppetiteLevel,
    DungSign,
    RespiratorySign,
    RiskBand,
    WaterIntakeLevel,
)
from app.models.risk_assessment import RiskAssessment

# Prototype validation bounds — not clinical thresholds, just guards
# against physically impossible thermometer/measurement input. See
# ml/src/rules.py for the separate, documented clinical-concern
# thresholds used by the risk engine.
MIN_PLAUSIBLE_TEMPERATURE_C = 30.0
MAX_PLAUSIBLE_TEMPERATURE_C = 45.0
MIN_PLAUSIBLE_MILK_YIELD_CHANGE_PCT = -100.0
MAX_PLAUSIBLE_MILK_YIELD_CHANGE_PCT = 200.0


class ObservationCreate(BaseModel):
    observed_at: Optional[datetime] = None
    appetite: AppetiteLevel
    activity: ActivityLevel
    water_intake: WaterIntakeLevel
    respiratory_sign: RespiratorySign
    dung_sign: DungSign
    temperature_c: Optional[float] = Field(
        default=None, ge=MIN_PLAUSIBLE_TEMPERATURE_C, le=MAX_PLAUSIBLE_TEMPERATURE_C
    )
    milk_yield_change_pct: Optional[float] = Field(
        default=None,
        ge=MIN_PLAUSIBLE_MILK_YIELD_CHANGE_PCT,
        le=MAX_PLAUSIBLE_MILK_YIELD_CHANGE_PCT,
    )
    notes: Optional[str] = Field(default=None, max_length=2000)
    image_url: Optional[str] = None


class ObservationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    animal_id: str
    observed_at: datetime
    appetite: AppetiteLevel
    activity: ActivityLevel
    water_intake: WaterIntakeLevel
    respiratory_sign: RespiratorySign
    dung_sign: DungSign
    temperature_c: Optional[float]
    milk_yield_change_pct: Optional[float]
    notes: Optional[str]
    image_url: Optional[str]
    entered_by: Optional[str]
    created_at: datetime


class RiskFactor(BaseModel):
    rule: str
    reason: str
    severity: str


class RiskAssessmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    observation_id: str
    model_version: str
    risk_score: float
    risk_band: RiskBand
    top_factors: list[RiskFactor]
    human_review_required: bool
    clinical_disclaimer: str
    created_at: datetime

    @classmethod
    def from_orm_with_disclaimer(cls, risk_assessment: RiskAssessment) -> "RiskAssessmentRead":
        from app.services.risk_service import CLINICAL_DISCLAIMER

        return cls(
            id=risk_assessment.id,
            observation_id=risk_assessment.observation_id,
            model_version=risk_assessment.model_version,
            risk_score=risk_assessment.risk_score,
            risk_band=risk_assessment.risk_band,
            top_factors=risk_assessment.top_factors_json,
            human_review_required=risk_assessment.human_review_required,
            clinical_disclaimer=CLINICAL_DISCLAIMER,
            created_at=risk_assessment.created_at,
        )


class ObservationResult(BaseModel):
    """What the farmer sees right after submitting an observation."""

    observation: ObservationRead
    risk_assessment: RiskAssessmentRead


class ObservationWithRisk(ObservationRead):
    """Used by the animal timeline, which needs each past observation's risk band."""

    risk_assessment: Optional[RiskAssessmentRead] = None
