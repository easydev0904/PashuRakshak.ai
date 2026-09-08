"""Import every ORM model so Alembic's autogenerate can discover them.

This module has no runtime purpose beyond side-effect imports; keep it in
sync whenever a new model module is added under app/models/.
"""

from app.db.base_class import Base  # noqa: F401
from app.models.alert import Alert  # noqa: F401
from app.models.animal import Animal  # noqa: F401
from app.models.audit_log import AuditLog  # noqa: F401
from app.models.case import Case, CaseUpdate  # noqa: F401
from app.models.education import EducationContent  # noqa: F401
from app.models.farm import Farm, FarmMembership  # noqa: F401
from app.models.observation import Observation  # noqa: F401
from app.models.risk_assessment import RiskAssessment  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.vaccination import VaccinationRecord  # noqa: F401
