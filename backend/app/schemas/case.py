from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import CaseStatus


class CaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    animal_id: str
    alert_id: Optional[str]
    status: CaseStatus
    suspected_condition: Optional[str]
    confirmed_condition: Optional[str]
    confirmation_basis: Optional[str]
    opened_by: Optional[str]
    closed_at: Optional[datetime]
    created_at: datetime


class CaseUpdateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    case_id: str
    author_id: Optional[str]
    note: str
    next_follow_up_at: Optional[datetime]
    created_at: datetime


class CaseDetail(CaseRead):
    updates: list[CaseUpdateRead] = []


class CaseCreate(BaseModel):
    suspected_condition: Optional[str] = Field(default=None, max_length=200)


class CaseUpdateCreate(BaseModel):
    note: str = Field(min_length=1, max_length=2000)
    next_follow_up_at: Optional[datetime] = None


class CaseClinicalUpdate(BaseModel):
    """Veterinarian-only fields. The AI must never populate these."""

    status: Optional[CaseStatus] = None
    suspected_condition: Optional[str] = Field(default=None, max_length=200)
    confirmed_condition: Optional[str] = Field(default=None, max_length=200)
    confirmation_basis: Optional[str] = Field(default=None, max_length=2000)
