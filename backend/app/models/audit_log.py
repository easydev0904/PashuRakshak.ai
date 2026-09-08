from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base, TimestampMixin, new_uuid


class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    actor_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entity_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
