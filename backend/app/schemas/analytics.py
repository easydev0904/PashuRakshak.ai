from typing import Optional

from pydantic import BaseModel


class RiskBandCount(BaseModel):
    risk_band: str
    count: int


class FarmTrendPoint(BaseModel):
    date: str
    observation_count: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int


class FarmTrendsResponse(BaseModel):
    farm_id: str
    farm_name: str
    total_animals: int
    total_observations: int
    risk_band_counts: list[RiskBandCount]
    open_alerts: int
    vaccinations_due: int
    daily_trend: list[FarmTrendPoint]
    note: str = (
        "These are aggregated early-warning observations for this farm, not a "
        "confirmed outbreak or diagnosis."
    )


class SystemHealthResponse(BaseModel):
    status: str
    environment: str
    total_users: Optional[int] = None
    total_farms: Optional[int] = None
    total_animals: Optional[int] = None
