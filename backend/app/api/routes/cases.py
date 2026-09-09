from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_vet_or_admin
from app.models.user import User
from app.schemas.case import CaseClinicalUpdate, CaseCreate, CaseDetail, CaseRead, CaseUpdateCreate
from app.services import case_service
from app.services.authz import assert_animal_access, get_animal_or_404
from app.services.case_service import get_case_or_404

router = APIRouter(tags=["cases"])


def _assert_case_access(db: Session, current_user: User, case) -> None:
    animal = get_animal_or_404(db, case.animal_id)
    assert_animal_access(db, user=current_user, animal=animal)


@router.get("/animals/{animal_id}/cases", response_model=list[CaseDetail])
def list_cases_for_animal(
    animal_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list:
    animal = get_animal_or_404(db, animal_id)
    assert_animal_access(db, user=current_user, animal=animal)
    return case_service.list_cases_for_animal(db, animal_id)


@router.post("/animals/{animal_id}/cases", response_model=CaseRead, status_code=201)
def open_case(
    animal_id: str,
    payload: CaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_vet_or_admin),
) -> CaseRead:
    animal = get_animal_or_404(db, animal_id)
    assert_animal_access(db, user=current_user, animal=animal)
    case = case_service.open_case(db, animal=animal, payload=payload, current_user=current_user)
    return CaseRead.model_validate(case)


@router.get("/cases/{case_id}", response_model=CaseDetail)
def get_case(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CaseDetail:
    case = get_case_or_404(db, case_id)
    _assert_case_access(db, current_user, case)
    return CaseDetail.model_validate(case)


@router.patch("/cases/{case_id}", response_model=CaseRead)
def update_case(
    case_id: str,
    payload: CaseClinicalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_vet_or_admin),
) -> CaseRead:
    case = get_case_or_404(db, case_id)
    _assert_case_access(db, current_user, case)
    updated = case_service.update_case_clinical(
        db, case=case, payload=payload, current_user=current_user
    )
    return CaseRead.model_validate(updated)


@router.post("/cases/{case_id}/updates", response_model=CaseRead)
def add_case_update(
    case_id: str,
    payload: CaseUpdateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_vet_or_admin),
) -> CaseRead:
    case = get_case_or_404(db, case_id)
    _assert_case_access(db, current_user, case)
    case_service.add_case_update(db, case=case, payload=payload, current_user=current_user)
    db.refresh(case)
    return CaseRead.model_validate(case)
