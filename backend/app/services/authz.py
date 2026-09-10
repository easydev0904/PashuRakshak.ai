"""Farm-scoped authorization helpers.

Farmers may only ever touch data belonging to a farm they are a member
of. Veterinarians and admins get broader (read/triage) access since a
vet in this prototype serves the whole referral network, not one farm.
This is the single choke point that prevents horizontal privilege
escalation (e.g. a farmer changing an animal_id in the URL to read a
different farm's data).
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import AuthorizationError, NotFoundError
from app.models.animal import Animal
from app.models.enums import UserRole
from app.models.farm import Farm, FarmMembership
from app.models.user import User


def is_farm_member(db: Session, *, user_id: str, farm_id: str) -> bool:
    stmt = select(FarmMembership).where(
        FarmMembership.user_id == user_id, FarmMembership.farm_id == farm_id
    )
    return db.execute(stmt).scalar_one_or_none() is not None


def assert_farm_access(db: Session, *, user: User, farm_id: str) -> None:
    if user.role in (UserRole.veterinarian, UserRole.admin):
        return
    if not is_farm_member(db, user_id=user.id, farm_id=farm_id):
        raise AuthorizationError("You do not have access to this farm.")


def get_farm_or_404(db: Session, farm_id: str) -> Farm:
    farm = db.get(Farm, farm_id)
    if farm is None:
        raise NotFoundError("This farm could not be found.")
    return farm


def get_animal_or_404(db: Session, animal_id: str) -> Animal:
    animal = db.get(Animal, animal_id)
    if animal is None:
        raise NotFoundError("This animal could not be found.")
    return animal


def assert_animal_access(db: Session, *, user: User, animal: Animal) -> None:
    assert_farm_access(db, user=user, farm_id=animal.farm_id)


def farm_ids_for_user(db: Session, *, user: User) -> list:
    if user.role in (UserRole.veterinarian, UserRole.admin):
        return [row[0] for row in db.execute(select(Farm.id)).all()]
    stmt = select(FarmMembership.farm_id).where(FarmMembership.user_id == user.id)
    return [row[0] for row in db.execute(stmt).all()]
