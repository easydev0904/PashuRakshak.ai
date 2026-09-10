from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.errors import ConflictError
from app.models.animal import Animal
from app.models.observation import Observation
from app.models.risk_assessment import RiskAssessment
from app.models.user import User
from app.schemas.animal import AnimalCreate, AnimalRead, AnimalSummary
from app.services import audit_service
from app.services.authz import assert_farm_access, farm_ids_for_user

CHECKIN_STALE_AFTER = timedelta(hours=24)


def create_animal(db: Session, *, payload: AnimalCreate, current_user: User) -> Animal:
    assert_farm_access(db, user=current_user, farm_id=payload.farm_id)

    animal = Animal(
        farm_id=payload.farm_id,
        tag_id=payload.tag_id,
        species=payload.species,
        breed=payload.breed,
        sex=payload.sex,
        dob=payload.dob,
        notes=payload.notes,
        photo_url=payload.photo_url,
    )
    db.add(animal)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("An animal with this tag ID already exists on this farm.") from exc

    audit_service.record(
        db,
        actor_id=current_user.id,
        entity_type="animal",
        entity_id=animal.id,
        action="create",
        metadata={"tag_id": animal.tag_id, "farm_id": animal.farm_id},
    )
    db.commit()
    db.refresh(animal)
    return animal


def list_animals_for_user(
    db: Session, *, current_user: User, farm_id: Optional[str] = None
) -> list:
    farm_ids = farm_ids_for_user(db, user=current_user)
    if farm_id:
        assert_farm_access(db, user=current_user, farm_id=farm_id)
        farm_ids = [farm_id]
    if not farm_ids:
        return []

    stmt = select(Animal).where(Animal.farm_id.in_(farm_ids)).order_by(Animal.created_at.desc())
    animals = list(db.execute(stmt).scalars().all())
    return _build_summaries(db, animals)


def _build_summaries(db: Session, animals: list) -> list:
    """Build AnimalSummary view models (never mutates the ORM instances)."""
    if not animals:
        return []
    animal_ids = [a.id for a in animals]
    stmt = (
        select(Observation)
        .options(selectinload(Observation.risk_assessment))
        .where(Observation.animal_id.in_(animal_ids))
        .order_by(Observation.observed_at.desc())
    )
    latest_by_animal: dict = {}
    for obs in db.execute(stmt).scalars().all():
        if obs.animal_id not in latest_by_animal:
            latest_by_animal[obs.animal_id] = obs

    now = datetime.now(timezone.utc)
    summaries = []
    for animal in animals:
        latest = latest_by_animal.get(animal.id)
        last_observation_at = latest.observed_at if latest else None
        last_risk_band = (
            latest.risk_assessment.risk_band if latest and latest.risk_assessment else None
        )
        needs_checkin_today = (
            last_observation_at is None or (now - last_observation_at) > CHECKIN_STALE_AFTER
        )
        summaries.append(
            AnimalSummary(
                **AnimalRead.model_validate(animal).model_dump(),
                last_observation_at=last_observation_at,
                last_risk_band=last_risk_band,
                needs_checkin_today=needs_checkin_today,
            )
        )
    return summaries


def get_animal_summary(db: Session, animal: Animal) -> AnimalSummary:
    return _build_summaries(db, [animal])[0]


def get_risk_assessments_for_animal(db: Session, animal_id: str) -> list:
    stmt = (
        select(RiskAssessment)
        .join(Observation, RiskAssessment.observation_id == Observation.id)
        .where(Observation.animal_id == animal_id)
        .order_by(RiskAssessment.created_at.desc())
    )
    return list(db.execute(stmt).scalars().all())
