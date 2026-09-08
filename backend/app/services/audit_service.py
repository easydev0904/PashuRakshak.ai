"""Audit log writer used by every state-changing service call."""

from typing import Optional

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def record(
    db: Session,
    *,
    actor_id: Optional[str],
    entity_type: str,
    entity_id: Optional[str],
    action: str,
    metadata: Optional[dict] = None,
) -> AuditLog:
    entry = AuditLog(
        actor_id=actor_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        metadata_json=metadata or {},
    )
    db.add(entry)
    db.flush()
    return entry
