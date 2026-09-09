from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.animal import Animal
from app.models.user import User
from app.models.vaccination import VaccinationRecord
from app.schemas.vaccination import VaccinationCreate
from app.services import audit_service

DUE_SOON_WINDOW = timedelta(days=14)


def create_vaccination_record(
    db: Session, *, animal: Animal, payload: VaccinationCreate, current_user: User
) -> VaccinationRecord:
    record = VaccinationRecord(
        animal_id=animal.id,
        vaccine_name=payload.vaccine_name,
        dose_date=payload.dose_date,
        due_date=payload.due_date,
        evidence_url=payload.evidence_url,
        administered_by=current_user.id if payload.dose_date else None,
    )
    db.add(record)
    db.flush()
    audit_service.record(
        db,
        actor_id=current_user.id,
        entity_type="vaccination_record",
        entity_id=record.id,
        action="create",
        metadata={"animal_id": animal.id, "vaccine_name": record.vaccine_name},
    )
    db.commit()
    db.refresh(record)
    return record


def list_vaccinations_for_animal(db: Session, animal_id: str) -> list:
    stmt = (
        select(VaccinationRecord)
        .where(VaccinationRecord.animal_id == animal_id)
        .order_by(VaccinationRecord.due_date.asc().nullslast())
    )
    return list(db.execute(stmt).scalars().all())


def list_due_soon_for_farm(
    db: Session, farm_ids: list, within: timedelta = DUE_SOON_WINDOW
) -> list:
    today = date.today()
    # due_date is "when the next dose is due" regardless of whether a
    # prior dose was already given -- a record can have both a past
    # dose_date (the last shot) and an upcoming due_date (the booster),
    # and that booster is exactly the kind of reminder a farmer needs.
    # Only due_date matters here; dose_date is irrelevant to "is this due".
    stmt = (
        select(VaccinationRecord)
        .join(Animal, Animal.id == VaccinationRecord.animal_id)
        .options(joinedload(VaccinationRecord.animal))
        .where(
            Animal.farm_id.in_(farm_ids),
            VaccinationRecord.due_date.is_not(None),
            VaccinationRecord.due_date <= today + within,
        )
        .order_by(VaccinationRecord.due_date.asc())
    )
    return list(db.execute(stmt).scalars().all())
