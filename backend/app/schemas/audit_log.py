from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    actor_id: Optional[str]
    entity_type: str
    entity_id: Optional[str]
    action: str
    metadata_json: dict
    created_at: datetime
