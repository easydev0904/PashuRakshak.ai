from sqlalchemy import Boolean, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base, TimestampMixin, new_uuid
from app.models.enums import EducationAudience, EducationCategory, Language


class EducationContent(Base, TimestampMixin):
    __tablename__ = "education_content"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    category: Mapped[EducationCategory] = mapped_column(
        Enum(EducationCategory, name="education_category"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    language: Mapped[Language] = mapped_column(
        Enum(Language, name="language"), nullable=False, index=True
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    audience: Mapped[EducationAudience] = mapped_column(
        Enum(EducationAudience, name="education_audience"),
        nullable=False,
        default=EducationAudience.all,
    )
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
