from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.errors import NotFoundError, ValidationAppError
from app.db.base_class import utcnow
from app.models.alert import Alert
from app.models.animal import Animal
from app.models.case import Case, CaseUpdate
from app.models.enums import AlertStatus, CaseStatus
from app.models.observation import Observation
from app.models.risk_assessment import RiskAssessment
from app.models.user import User
from app.schemas.alert import AlertReviewAction
from app.services import audit_service
from app.services.authz import farm_ids_for_user

VALID_ACTIONS = {"acknowledge", "assign", "request_follow_up", "resolve"}


def get_alert_or_404(db: Session, alert_id: str) -> Alert:
    alert = db.get(Alert, alert_id)
    if alert is None:
        raise NotFoundError("This alert could not be found.")
    return alert


def list_alerts_for_user(
    db: Session,
    *,
    current_user: User,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    farm_id: Optional[str] = None,
    assigned_vet_id: Optional[str] = None,
) -> list:
    accessible_farm_ids = farm_ids_for_user(db, user=current_user)
    if not accessible_farm_ids:
        return []

    stmt = (
        select(Alert)
        .join(RiskAssessment, RiskAssessment.id == Alert.assessment_id)
        .join(Observation, Observation.id == RiskAssessment.observation_id)
        .join(Animal, Animal.id == Observation.animal_id)
        .where(Animal.farm_id.in_(accessible_farm_ids))
        .options(
            selectinload(Alert.assessment)
            .selectinload(RiskAssessment.observation)
            .selectinload(Observation.animal)
        )
    )
    if status:
        stmt = stmt.where(Alert.status == status)
    if priority:
        stmt = stmt.where(Alert.priority == priority)
    if farm_id:
        stmt = stmt.where(Animal.farm_id == farm_id)
    if assigned_vet_id:
        stmt = stmt.where(Alert.assigned_vet_id == assigned_vet_id)

    stmt = stmt.order_by(Alert.priority.desc(), Alert.created_at.asc())
    return list(db.execute(stmt).scalars().all())


def get_alert_detail_context(db: Session, alert: Alert) -> dict:
    assessment = db.get(RiskAssessment, alert.assessment_id)
    if assessment is None:
        raise NotFoundError("This alert's risk assessment could not be found.")
    observation = db.get(Observation, assessment.observation_id)
    if observation is None:
        raise NotFoundError("This alert's observation could not be found.")
    animal = db.get(Animal, observation.animal_id)
    if animal is None:
        raise NotFoundError("This alert's animal could not be found.")
    return {"assessment": assessment, "observation": observation, "animal": animal}


def apply_review_action(
    db: Session, *, alert: Alert, action: AlertReviewAction, current_user: User
) -> Alert:
    if action.action not in VALID_ACTIONS:
        raise ValidationAppError(
            "That action is not recognized. Use acknowledge, assign, request_follow_up, or resolve."
        )

    if action.action == "acknowledge":
        alert.status = AlertStatus.acknowledged
        alert.acknowledged_at = utcnow()
    elif action.action == "assign":
        if not action.assigned_vet_id:
            raise ValidationAppError("A veterinarian must be specified to assign this alert.")
        alert.assigned_vet_id = action.assigned_vet_id
        alert.status = AlertStatus.assigned
    elif action.action == "request_follow_up":
        alert.status = AlertStatus.in_review
        _ensure_case_with_update(db, alert, action, current_user)
    elif action.action == "resolve":
        alert.status = AlertStatus.resolved
        alert.resolution = action.note or alert.resolution

    db.add(alert)
    audit_service.record(
        db,
        actor_id=current_user.id,
        entity_type="alert",
        entity_id=alert.id,
        action=action.action,
        metadata={"status": alert.status.value},
    )
    db.commit()
    db.refresh(alert)
    return alert


def _ensure_case_with_update(
    db: Session, alert: Alert, action: AlertReviewAction, current_user: User
) -> Case:
    case = db.execute(select(Case).where(Case.alert_id == alert.id)).scalar_one_or_none()
    if case is None:
        context = get_alert_detail_context(db, alert)
        case = Case(
            animal_id=context["observation"].animal_id,
            alert_id=alert.id,
            status=CaseStatus.follow_up,
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
            metadata={"alert_id": alert.id},
        )
    else:
        case.status = CaseStatus.follow_up

    update = CaseUpdate(
        case_id=case.id,
        author_id=current_user.id,
        note=action.note or "Clinical review requested.",
        next_follow_up_at=action.follow_up_at,
    )
    db.add(update)
    return case
