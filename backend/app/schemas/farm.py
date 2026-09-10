from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class FarmCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    village: Optional[str] = Field(default=None, max_length=150)
    district: Optional[str] = Field(default=None, max_length=150)
    state: Optional[str] = Field(default=None, max_length=150)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    consent_version: Optional[str] = Field(default=None, max_length=20)


class FarmRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    village: Optional[str]
    district: Optional[str]
    state: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    consent_version: Optional[str]
