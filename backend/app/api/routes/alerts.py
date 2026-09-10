from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_vet_or_admin
from app.models.user import User
from app.schemas.alert import AlertDetail, AlertRead, AlertReviewAction
from app.schemas.animal import AnimalRead
from app.schemas.observation import ObservationRead, RiskAssessmentRead
from app.services import alert_service
from app.services.authz import assert_farm_access

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertRead])
def list_alerts(
    status: Optional[str] = Query(default=None),
    priority: Optional[str] = Query(default=None),
    farm_id: Optional[str] = Query(default=None),
    assigned_vet_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list:
    return alert_service.list_alerts_for_user(
        db,
        current_user=current_user,
        status=status,
        priority=priority,
        farm_id=farm_id,
        assigned_vet_id=assigned_vet_id,
    )


@router.get("/{alert_id}", response_model=AlertDetail)
def get_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AlertDetail:
    alert = alert_service.get_alert_or_404(db, alert_id)
    context = alert_service.get_alert_detail_context(db, alert)
    assert_farm_access(db, user=current_user, farm_id=context["animal"].farm_id)

    risk_read = RiskAssessmentRead.from_orm_with_disclaimer(context["assessment"])
    return AlertDetail(
        **AlertRead.model_validate(alert).model_dump(),
        animal=AnimalRead.model_validate(context["animal"]),
        observation=ObservationRead.model_validate(context["observation"]),
        risk_assessment=risk_read,
        farm_name=context["animal"].farm.name,
    )


@router.patch("/{alert_id}", response_model=AlertRead)
def update_alert(
    alert_id: str,
    payload: AlertReviewAction,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_vet_or_admin),
) -> AlertRead:
    alert = alert_service.get_alert_or_404(db, alert_id)
    context = alert_service.get_alert_detail_context(db, alert)
    assert_farm_access(db, user=current_user, farm_id=context["animal"].farm_id)
    updated = alert_service.apply_review_action(
        db, alert=alert, action=payload, current_user=current_user
    )
    return AlertRead.model_validate(updated)


@router.post("/{alert_id}/review", response_model=AlertRead)
def review_alert(
    alert_id: str,
    payload: AlertReviewAction,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_vet_or_admin),
) -> AlertRead:
    alert = alert_service.get_alert_or_404(db, alert_id)
    context = alert_service.get_alert_detail_context(db, alert)
    assert_farm_access(db, user=current_user, farm_id=context["animal"].farm_id)
    updated = alert_service.apply_review_action(
        db, alert=alert, action=payload, current_user=current_user
    )
    return AlertRead.model_validate(updated)
