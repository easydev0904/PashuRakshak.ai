from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import EducationAudience, EducationCategory, Language


class EducationContentCreate(BaseModel):
    category: EducationCategory
    title: str = Field(min_length=1, max_length=200)
    language: Language
    body: str = Field(min_length=1)
    audience: EducationAudience = EducationAudience.all
    is_published: bool = True


class EducationContentUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    body: Optional[str] = None
    is_published: Optional[bool] = None


class EducationContentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    category: EducationCategory
    title: str
    language: Language
    body: str
    audience: EducationAudience
    is_published: bool
