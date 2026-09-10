from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_admin
from app.models.user import User
from app.schemas.audit_log import AuditLogRead
from app.services import audit_log_service

router = APIRouter(prefix="/audit-logs", tags=["audit-logs"])


@router.get("", response_model=list[AuditLogRead])
def list_audit_logs(
    entity_type: Optional[str] = Query(default=None),
    action: Optional[str] = Query(default=None),
    actor_id: Optional[str] = Query(default=None),
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> list:
    return audit_log_service.list_audit_logs(
        db, entity_type=entity_type, action=action, actor_id=actor_id, limit=limit
    )
