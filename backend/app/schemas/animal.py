from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AnimalStatus, RiskBand, Sex, Species


class AnimalCreate(BaseModel):
    farm_id: str
    tag_id: str = Field(min_length=1, max_length=50)
    species: Species
    breed: Optional[str] = Field(default=None, max_length=100)
    sex: Sex
    dob: Optional[date] = None
    notes: Optional[str] = Field(default=None, max_length=2000)
    photo_url: Optional[str] = None


class AnimalUpdate(BaseModel):
    breed: Optional[str] = Field(default=None, max_length=100)
    status: Optional[AnimalStatus] = None
    notes: Optional[str] = Field(default=None, max_length=2000)
    photo_url: Optional[str] = None


class AnimalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    farm_id: str
    tag_id: str
    species: Species
    breed: Optional[str]
    sex: Sex
    dob: Optional[date]
    status: AnimalStatus
    photo_url: Optional[str]
    notes: Optional[str]
    created_at: datetime


class AnimalSummary(AnimalRead):
    """Adds dashboard-friendly derived fields without new DB columns."""

    last_observation_at: Optional[datetime] = None
    last_risk_band: Optional[RiskBand] = None
    needs_checkin_today: bool = True
