from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.animal import Animal
from app.models.observation import Observation
from app.models.risk_assessment import RiskAssessment
from app.schemas.analytics import FarmTrendPoint, FarmTrendsResponse, RiskBandCount
from app.services.authz import get_farm_or_404
from app.services.vaccination_service import list_due_soon_for_farm

TREND_WINDOW_DAYS = 30


def build_farm_trends(db: Session, farm_id: str) -> FarmTrendsResponse:
    farm = get_farm_or_404(db, farm_id)

    total_animals = db.execute(
        select(func.count(Animal.id)).where(Animal.farm_id == farm_id)
    ).scalar_one()

    total_observations = db.execute(
        select(func.count(Observation.id))
        .join(Animal, Animal.id == Observation.animal_id)
        .where(Animal.farm_id == farm_id)
    ).scalar_one()

    band_rows = db.execute(
        select(RiskAssessment.risk_band, func.count(RiskAssessment.id))
        .join(Observation, Observation.id == RiskAssessment.observation_id)
        .join(Animal, Animal.id == Observation.animal_id)
        .where(Animal.farm_id == farm_id)
        .group_by(RiskAssessment.risk_band)
    ).all()
    risk_band_counts = [
        RiskBandCount(risk_band=band.value, count=count) for band, count in band_rows
    ]

    open_alerts = db.execute(
        select(func.count(Alert.id))
        .join(RiskAssessment, RiskAssessment.id == Alert.assessment_id)
        .join(Observation, Observation.id == RiskAssessment.observation_id)
        .join(Animal, Animal.id == Observation.animal_id)
        .where(
            Animal.farm_id == farm_id,
            Alert.status.in_(["open", "acknowledged", "assigned", "in_review"]),
        )
    ).scalar_one()

    vaccinations_due = len(list_due_soon_for_farm(db, [farm_id]))

    daily_trend = _daily_trend(db, farm_id)

    return FarmTrendsResponse(
        farm_id=farm.id,
        farm_name=farm.name,
        total_animals=total_animals,
        total_observations=total_observations,
        risk_band_counts=risk_band_counts,
        open_alerts=open_alerts,
        vaccinations_due=vaccinations_due,
        daily_trend=daily_trend,
    )


def _daily_trend(db: Session, farm_id: str) -> list:
    since = date.today() - timedelta(days=TREND_WINDOW_DAYS)
    rows = db.execute(
        select(
            func.date(Observation.observed_at),
            RiskAssessment.risk_band,
            func.count(Observation.id),
        )
        .join(Animal, Animal.id == Observation.animal_id)
        .outerjoin(RiskAssessment, RiskAssessment.observation_id == Observation.id)
        .where(Animal.farm_id == farm_id, Observation.observed_at >= since)
        .group_by(func.date(Observation.observed_at), RiskAssessment.risk_band)
        .order_by(func.date(Observation.observed_at))
    ).all()

    by_date: dict = {}
    for obs_date, band, count in rows:
        key = str(obs_date)
        by_date.setdefault(key, {"observation_count": 0, "high": 0, "medium": 0, "low": 0})
        by_date[key]["observation_count"] += count
        if band is not None:
            by_date[key][band.value] += count

    return [
        FarmTrendPoint(
            date=day,
            observation_count=values["observation_count"],
            high_risk_count=values["high"],
            medium_risk_count=values["medium"],
            low_risk_count=values["low"],
        )
        for day, values in sorted(by_date.items())
    ]
