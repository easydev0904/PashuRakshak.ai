from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.models.education import EducationContent
from app.models.enums import EducationAudience, EducationCategory, Language
from app.models.user import User
from app.schemas.education import EducationContentCreate, EducationContentUpdate
from app.services import audit_service


def list_published_content(
    db: Session,
    *,
    language: Optional[Language] = None,
    category: Optional[EducationCategory] = None,
    audience: Optional[EducationAudience] = None,
) -> list:
    stmt = select(EducationContent).where(EducationContent.is_published.is_(True))
    if language:
        stmt = stmt.where(EducationContent.language == language)
    if category:
        stmt = stmt.where(EducationContent.category == category)
    if audience:
        stmt = stmt.where(
            (EducationContent.audience == audience)
            | (EducationContent.audience == EducationAudience.all)
        )
    stmt = stmt.order_by(EducationContent.category, EducationContent.title)
    return list(db.execute(stmt).scalars().all())


def get_content_or_404(db: Session, content_id: str) -> EducationContent:
    content = db.get(EducationContent, content_id)
    if content is None:
        raise NotFoundError("This education content could not be found.")
    return content


def create_content(
    db: Session, *, payload: EducationContentCreate, current_user: User
) -> EducationContent:
    content = EducationContent(**payload.model_dump())
    db.add(content)
    db.flush()
    audit_service.record(
        db,
        actor_id=current_user.id,
        entity_type="education_content",
        entity_id=content.id,
        action="create",
        metadata={"title": content.title},
    )
    db.commit()
    db.refresh(content)
    return content


def update_content(
    db: Session,
    *,
    content: EducationContent,
    payload: EducationContentUpdate,
    current_user: User,
) -> EducationContent:
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(content, key, value)
    db.add(content)
    audit_service.record(
        db,
        actor_id=current_user.id,
        entity_type="education_content",
        entity_id=content.id,
        action="update",
        metadata=updates,
    )
    db.commit()
    db.refresh(content)
    return content


def list_all_content_for_admin(db: Session) -> list:
    stmt = select(EducationContent).order_by(EducationContent.category, EducationContent.title)
    return list(db.execute(stmt).scalars().all())
