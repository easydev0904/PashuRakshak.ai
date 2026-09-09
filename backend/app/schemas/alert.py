from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AlertPriority, AlertStatus
from app.schemas.animal import AnimalRead
from app.schemas.observation import ObservationRead, RiskAssessmentRead


class AlertRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    assessment_id: str
    priority: AlertPriority
    status: AlertStatus
    assigned_vet_id: Optional[str]
    acknowledged_at: Optional[datetime]
    resolution: Optional[str]
    created_at: datetime


class AlertDetail(AlertRead):
    animal: AnimalRead
    observation: ObservationRead
    risk_assessment: RiskAssessmentRead
    farm_name: str


class AlertUpdate(BaseModel):
    status: Optional[AlertStatus] = None
    assigned_vet_id: Optional[str] = None
    resolution: Optional[str] = Field(default=None, max_length=2000)


class AlertReviewAction(BaseModel):
    action: str = Field(description="acknowledge | assign | request_follow_up | resolve")
    assigned_vet_id: Optional[str] = None
    note: Optional[str] = Field(default=None, max_length=2000)
    follow_up_at: Optional[datetime] = None
