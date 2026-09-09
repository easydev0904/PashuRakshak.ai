from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog

MAX_PAGE_SIZE = 200


def list_audit_logs(
    db: Session,
    *,
    entity_type: Optional[str] = None,
    action: Optional[str] = None,
    actor_id: Optional[str] = None,
    limit: int = 50,
) -> list:
    limit = min(limit, MAX_PAGE_SIZE)
    stmt = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
    if entity_type:
        stmt = stmt.where(AuditLog.entity_type == entity_type)
    if action:
        stmt = stmt.where(AuditLog.action == action)
    if actor_id:
        stmt = stmt.where(AuditLog.actor_id == actor_id)
    return list(db.execute(stmt).scalars().all())
