from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_admin
from app.models.enums import EducationAudience, EducationCategory, Language
from app.models.user import User
from app.schemas.education import (
    EducationContentCreate,
    EducationContentRead,
    EducationContentUpdate,
)
from app.services import education_service

router = APIRouter(prefix="/education", tags=["education"])


@router.get("", response_model=list[EducationContentRead])
def list_education_content(
    language: Optional[Language] = Query(default=None),
    category: Optional[EducationCategory] = Query(default=None),
    audience: Optional[EducationAudience] = Query(default=None),
    db: Session = Depends(get_db),
) -> list:
    return education_service.list_published_content(
        db, language=language, category=category, audience=audience
    )


@router.get("/{content_id}", response_model=EducationContentRead)
def get_education_content(content_id: str, db: Session = Depends(get_db)) -> EducationContentRead:
    content = education_service.get_content_or_404(db, content_id)
    return EducationContentRead.model_validate(content)


@router.post("", response_model=EducationContentRead, status_code=201)
def create_education_content(
    payload: EducationContentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> EducationContentRead:
    content = education_service.create_content(db, payload=payload, current_user=current_user)
    return EducationContentRead.model_validate(content)


@router.patch("/{content_id}", response_model=EducationContentRead)
def update_education_content(
    content_id: str,
    payload: EducationContentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> EducationContentRead:
    content = education_service.get_content_or_404(db, content_id)
    updated = education_service.update_content(
        db, content=content, payload=payload, current_user=current_user
    )
    return EducationContentRead.model_validate(updated)
