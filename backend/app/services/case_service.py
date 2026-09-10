from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.errors import NotFoundError
from app.db.base_class import utcnow
from app.models.animal import Animal
from app.models.case import Case, CaseUpdate
from app.models.enums import CaseStatus
from app.models.user import User
from app.schemas.case import CaseClinicalUpdate, CaseCreate, CaseUpdateCreate
from app.services import audit_service

TERMINAL_STATUSES = (CaseStatus.resolved, CaseStatus.ruled_out)


def get_case_or_404(db: Session, case_id: str) -> Case:
    case = db.get(Case, case_id)
    if case is None:
        raise NotFoundError("This case could not be found.")
    return case


def list_cases_for_animal(db: Session, animal_id: str) -> list:
    stmt = (
        select(Case)
        .where(Case.animal_id == animal_id)
        .options(selectinload(Case.updates))
        .order_by(Case.created_at.desc())
    )
    return list(db.execute(stmt).scalars().all())


def open_case(db: Session, *, animal: Animal, payload: CaseCreate, current_user: User) -> Case:
    case = Case(
        animal_id=animal.id,
        status=CaseStatus.open,
        suspected_condition=payload.suspected_condition,
        opened_by=current_user.id,
    )
    db.add(case)
    db.flush()
    audit_service.record(
        db,
        actor_id=current_user.id,
        entity_type="case",
        entity_id=case.id,
        action="create",
        metadata={"animal_id": animal.id},
    )
    db.commit()
    db.refresh(case)
    return case


def add_case_update(
    db: Session, *, case: Case, payload: CaseUpdateCreate, current_user: User
) -> CaseUpdate:
    update = CaseUpdate(
        case_id=case.id,
        author_id=current_user.id,
        note=payload.note,
        next_follow_up_at=payload.next_follow_up_at,
    )
    db.add(update)
    if payload.next_follow_up_at and case.status not in TERMINAL_STATUSES:
        case.status = CaseStatus.follow_up
        db.add(case)

    audit_service.record(
        db,
        actor_id=current_user.id,
        entity_type="case_update",
        entity_id=None,
        action="create",
        metadata={"case_id": case.id},
    )
    db.commit()
    db.refresh(update)
    return update


def update_case_clinical(
    db: Session, *, case: Case, payload: CaseClinicalUpdate, current_user: User
) -> Case:
    """Veterinarian/admin-only. The AI never calls this path."""
    changed: dict = {}
    if payload.status is not None:
        case.status = payload.status
        changed["status"] = payload.status.value
        if payload.status in TERMINAL_STATUSES:
            case.closed_at = utcnow()
    if payload.suspected_condition is not None:
        case.suspected_condition = payload.suspected_condition
        changed["suspected_condition"] = payload.suspected_condition
    if payload.confirmed_condition is not None:
        case.confirmed_condition = payload.confirmed_condition
        changed["confirmed_condition"] = payload.confirmed_condition
    if payload.confirmation_basis is not None:
        case.confirmation_basis = payload.confirmation_basis

    db.add(case)
    audit_service.record(
        db,
        actor_id=current_user.id,
        entity_type="case",
        entity_id=case.id,
        action="clinical_update",
        metadata=changed,
    )
    db.commit()
    db.refresh(case)
    return case
