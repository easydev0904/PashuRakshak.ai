from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base_class import utcnow
from app.models.alert import Alert
from app.models.animal import Animal
from app.models.enums import AlertPriority, RiskBand
from app.models.observation import Observation
from app.models.risk_assessment import RiskAssessment
from app.models.user import User
from app.schemas.observation import ObservationCreate
from app.services import audit_service, risk_service

HISTORY_LOOKBACK = 30
ALERTABLE_BANDS = ("medium", "high")


def _get_history(db: Session, animal_id: str, exclude_id: Optional[str] = None) -> list:
    stmt = (
        select(Observation)
        .where(Observation.animal_id == animal_id)
        .order_by(Observation.observed_at.desc())
        .limit(HISTORY_LOOKBACK)
    )
    observations = list(db.execute(stmt).scalars().all())
    if exclude_id:
        observations = [o for o in observations if o.id != exclude_id]
    return observations


def create_observation(
    db: Session, *, animal: Animal, payload: ObservationCreate, current_user: User
) -> tuple:
    history = _get_history(db, animal.id)

    observation = Observation(
        animal_id=animal.id,
        observed_at=payload.observed_at or utcnow(),
        appetite=payload.appetite,
        activity=payload.activity,
        water_intake=payload.water_intake,
        respiratory_sign=payload.respiratory_sign,
        dung_sign=payload.dung_sign,
        temperature_c=payload.temperature_c,
        milk_yield_change_pct=payload.milk_yield_change_pct,
        notes=payload.notes,
        image_url=payload.image_url,
        entered_by=current_user.id,
    )
    db.add(observation)
    db.flush()

    score_result = risk_service.score_observation(observation, history, animal)
    risk_band = RiskBand(score_result["risk_band"])

    risk_assessment = RiskAssessment(
        observation_id=observation.id,
        model_version=score_result["model_version"],
        risk_score=score_result["risk_score"],
        risk_band=risk_band,
        top_factors_json=score_result["top_factors"],
        human_review_required=score_result["human_review_required"],
    )
    db.add(risk_assessment)
    db.flush()

    alert = None
    if score_result["risk_band"] in ALERTABLE_BANDS:
        alert = Alert(assessment_id=risk_assessment.id, priority=AlertPriority(risk_band.value))
        db.add(alert)
        db.flush()

    audit_service.record(
        db,
        actor_id=current_user.id,
        entity_type="observation",
        entity_id=observation.id,
        action="create",
        metadata={"animal_id": animal.id, "risk_band": score_result["risk_band"]},
    )
    audit_service.record(
        db,
        actor_id=current_user.id,
        entity_type="risk_assessment",
        entity_id=risk_assessment.id,
        action="create",
        metadata={
            "model_version": risk_assessment.model_version,
            "risk_band": score_result["risk_band"],
        },
    )
    if alert is not None:
        audit_service.record(
            db,
            actor_id=current_user.id,
            entity_type="alert",
            entity_id=alert.id,
            action="create",
            metadata={"priority": alert.priority.value},
        )

    db.commit()
    db.refresh(observation)
    db.refresh(risk_assessment)
    return observation, risk_assessment


def list_observations_for_animal(db: Session, animal_id: str) -> list:
    stmt = (
        select(Observation)
        .where(Observation.animal_id == animal_id)
        .order_by(Observation.observed_at.desc())
    )
    return list(db.execute(stmt).scalars().all())
