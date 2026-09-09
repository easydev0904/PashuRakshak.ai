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


class ObservationResult(BaseModel):
    """What the farmer sees right after submitting an observation."""

    observation: ObservationRead
    risk_assessment: RiskAssessmentRead
