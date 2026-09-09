from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class VaccinationCreate(BaseModel):
    vaccine_name: str = Field(min_length=1, max_length=150)
    dose_date: Optional[date] = None
    due_date: Optional[date] = None
    evidence_url: Optional[str] = None


class VaccinationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    animal_id: str
    vaccine_name: str
    dose_date: Optional[date]
    due_date: Optional[date]
    administered_by: Optional[str]
    evidence_url: Optional[str]
    created_at: datetime
