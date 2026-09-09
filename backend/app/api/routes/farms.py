from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.farm import FarmCreate, FarmRead
from app.services import farm_service

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
