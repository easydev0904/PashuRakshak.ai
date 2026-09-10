from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.farm import Farm, FarmMembership
from app.models.user import User
from app.schemas.farm import FarmCreate
from app.services import audit_service
from app.services.authz import farm_ids_for_user


def create_farm(db: Session, *, payload: FarmCreate, current_user: User) -> Farm:
    farm = Farm(
        name=payload.name,
        village=payload.village,
        district=payload.district,
        state=payload.state,
        latitude=payload.latitude,
        longitude=payload.longitude,
        consent_version=payload.consent_version,
    )
    db.add(farm)
    db.flush()

    membership = FarmMembership(farm_id=farm.id, user_id=current_user.id, role=current_user.role)
    db.add(membership)

    audit_service.record(
        db,
        actor_id=current_user.id,
        entity_type="farm",
        entity_id=farm.id,
        action="create",
        metadata={"name": farm.name},
    )
    db.commit()
    db.refresh(farm)
    return farm


def list_farms_for_user(db: Session, *, current_user: User) -> list:
    farm_ids = farm_ids_for_user(db, user=current_user)
    if not farm_ids:
        return []
    stmt = select(Farm).where(Farm.id.in_(farm_ids)).order_by(Farm.name)
    return list(db.execute(stmt).scalars().all())
