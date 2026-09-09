from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.animal import AnimalCreate, AnimalRead, AnimalSummary
from app.schemas.observation import (
    ObservationCreate,
    ObservationRead,
    ObservationResult,
    RiskAssessmentRead,
)
from app.schemas.vaccination import VaccinationCreate, VaccinationRead
from app.services import animal_service, observation_service, vaccination_service
from app.services.authz import assert_animal_access, get_animal_or_404
from app.services.risk_service import CLINICAL_DISCLAIMER

router = APIRouter(prefix="/animals", tags=["animals"])


@router.get("", response_model=list[AnimalSummary])
def list_animals(
    farm_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list:
    return animal_service.list_animals_for_user(db, current_user=current_user, farm_id=farm_id)


@router.post("", response_model=AnimalRead, status_code=201)
def create_animal(
    payload: AnimalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AnimalRead:
    animal = animal_service.create_animal(db, payload=payload, current_user=current_user)
    return AnimalRead.model_validate(animal)


@router.get("/{animal_id}", response_model=AnimalSummary)
def get_animal(
    animal_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AnimalSummary:
    animal = get_animal_or_404(db, animal_id)
    assert_animal_access(db, user=current_user, animal=animal)
    return animal_service.get_animal_summary(db, animal)


@router.get("/{animal_id}/observations", response_model=list[ObservationRead])
def list_observations(
    animal_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list:
    animal = get_animal_or_404(db, animal_id)
    assert_animal_access(db, user=current_user, animal=animal)
    return observation_service.list_observations_for_animal(db, animal_id)


@router.post("/{animal_id}/observations", response_model=ObservationResult, status_code=201)
def create_observation(
    animal_id: str,
    payload: ObservationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ObservationResult:
    animal = get_animal_or_404(db, animal_id)
    assert_animal_access(db, user=current_user, animal=animal)
    observation, risk_assessment = observation_service.create_observation(
        db, animal=animal, payload=payload, current_user=current_user
    )
    risk_read = RiskAssessmentRead(
        id=risk_assessment.id,
        observation_id=risk_assessment.observation_id,
        model_version=risk_assessment.model_version,
        risk_score=risk_assessment.risk_score,
        risk_band=risk_assessment.risk_band,
        top_factors=risk_assessment.top_factors_json,
        human_review_required=risk_assessment.human_review_required,
        clinical_disclaimer=CLINICAL_DISCLAIMER,
        created_at=risk_assessment.created_at,
    )
    return ObservationResult(
        observation=ObservationRead.model_validate(observation),
        risk_assessment=risk_read,
    )


@router.get("/{animal_id}/vaccinations", response_model=list[VaccinationRead])
def list_vaccinations(
    animal_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list:
    animal = get_animal_or_404(db, animal_id)
    assert_animal_access(db, user=current_user, animal=animal)
    return vaccination_service.list_vaccinations_for_animal(db, animal_id)


@router.post("/{animal_id}/vaccinations", response_model=VaccinationRead, status_code=201)
def create_vaccination(
    animal_id: str,
    payload: VaccinationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> VaccinationRead:
    animal = get_animal_or_404(db, animal_id)
    assert_animal_access(db, user=current_user, animal=animal)
    record = vaccination_service.create_vaccination_record(
        db, animal=animal, payload=payload, current_user=current_user
    )
    return VaccinationRead.model_validate(record)
