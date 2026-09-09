from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.farm import FarmCreate, FarmRead
from app.schemas.vaccination import VaccinationDue, VaccinationRead
from app.services import farm_service, vaccination_service
from app.services.authz import assert_farm_access

router = APIRouter(prefix="/farms", tags=["farms"])


@router.get("", response_model=list[FarmRead])
def list_farms(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list:
    return farm_service.list_farms_for_user(db, current_user=current_user)


@router.post("", response_model=FarmRead, status_code=201)
def create_farm(
    payload: FarmCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FarmRead:
    farm = farm_service.create_farm(db, payload=payload, current_user=current_user)
    return FarmRead.model_validate(farm)


@router.get("/{farm_id}/vaccinations-due", response_model=list[VaccinationDue])
def list_vaccinations_due(
    farm_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list:
    assert_farm_access(db, user=current_user, farm_id=farm_id)
    records = vaccination_service.list_due_soon_for_farm(db, [farm_id])
    return [
        VaccinationDue(
            **VaccinationRead.model_validate(record).model_dump(),
            animal_tag_id=record.animal.tag_id,
        )
        for record in records
    ]
