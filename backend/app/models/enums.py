"""Shared enum types used across ORM models and Pydantic schemas.

Member names are intentionally lowercase and identical to their string
values. SQLAlchemy's Enum column type persists the Python member *name*
by default; keeping name == value avoids a silent mismatch between what
the API sends/receives (the value) and what lands in Postgres.
"""

import enum


class UserRole(str, enum.Enum):
    farmer = "farmer"
    veterinarian = "veterinarian"
    admin = "admin"


class Language(str, enum.Enum):
    en = "en"
    hi = "hi"


class Species(str, enum.Enum):
    cattle = "cattle"
    buffalo = "buffalo"


class Sex(str, enum.Enum):
    male = "male"
    female = "female"


class AnimalStatus(str, enum.Enum):
    active = "active"
    sold = "sold"
    deceased = "deceased"


class AppetiteLevel(str, enum.Enum):
    normal = "normal"
    reduced = "reduced"
    none = "none"


class ActivityLevel(str, enum.Enum):
    normal = "normal"
    reduced = "reduced"
    lethargic = "lethargic"


class WaterIntakeLevel(str, enum.Enum):
    normal = "normal"
    reduced = "reduced"
    increased = "increased"


class RespiratorySign(str, enum.Enum):
    none = "none"
    mild = "mild"
    labored = "labored"
    coughing = "coughing"


class DungSign(str, enum.Enum):
    normal = "normal"
    loose = "loose"
    diarrhea = "diarrhea"
    bloody = "bloody"


class RiskBand(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class AlertPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class AlertStatus(str, enum.Enum):
    open = "open"
    acknowledged = "acknowledged"
    assigned = "assigned"
    in_review = "in_review"
    resolved = "resolved"


class CaseStatus(str, enum.Enum):
    open = "open"
    under_review = "under_review"
    follow_up = "follow_up"
    resolved = "resolved"
    ruled_out = "ruled_out"


class EducationAudience(str, enum.Enum):
    farmer = "farmer"
    veterinarian = "veterinarian"
    all = "all"


class EducationCategory(str, enum.Enum):
    vaccination = "vaccination"
    hygiene = "hygiene"
    quarantine = "quarantine"
    nutrition = "nutrition"
    biosecurity = "biosecurity"
    general_observation = "general_observation"
