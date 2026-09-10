"""Bridges the backend to the ml/ package's scoring contract.

The ml/ package lives at the repo root (sibling of backend/) so it can
be trained and tested independently of the API. This module is the
ONLY place in the backend that imports `ml.*` directly; every route or
service that needs model output or the disclaimer text goes through
here, never through `ml.*` itself. The sys.path bootstrap below is
self-contained (not dependent on import order elsewhere) so this
module works correctly no matter what imports it first.
"""

import sys
from datetime import date
from pathlib import Path
from typing import Optional

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from ml.src.constants import CLINICAL_DISCLAIMER  # noqa: E402
from ml.src.predict import assess as ml_assess  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.models.animal import Animal  # noqa: E402
from app.models.observation import Observation  # noqa: E402

settings = get_settings()

__all__ = ["score_observation", "CLINICAL_DISCLAIMER"]


def _observation_to_dict(observation: Observation) -> dict:
    return {
        "appetite": observation.appetite.value,
        "activity": observation.activity.value,
        "water_intake": observation.water_intake.value,
        "respiratory_sign": observation.respiratory_sign.value,
        "dung_sign": observation.dung_sign.value,
        "temperature_c": observation.temperature_c,
        "milk_yield_change_pct": observation.milk_yield_change_pct,
    }


def _history_to_dicts(history: list) -> list:
    result = []
    for obs in history:
        entry = _observation_to_dict(obs)
        entry["observed_at"] = obs.observed_at.replace(tzinfo=None)
        result.append(entry)
    return result


def score_observation(observation: Observation, history: list, animal: Animal) -> dict:
    """Run the AI early-warning scoring contract for one observation.

    Args:
        observation: the just-created Observation row.
        history: prior Observation rows for the same animal, most
            recent first (not including `observation` itself).
        animal: the Animal the observation belongs to (for species/dob).
    """
    context = {
        "species": animal.species.value,
        "dob": animal.dob,
        "observed_at": observation.observed_at.replace(tzinfo=None),
        "vaccination_overdue": _has_overdue_vaccination(animal),
    }
    model_path = _resolve_model_path()
    return ml_assess(
        _observation_to_dict(observation),
        history=_history_to_dicts(history),
        context=context,
        model_path=model_path,
    )


def _has_overdue_vaccination(animal: Animal) -> bool:
    today = date.today()
    for record in getattr(animal, "vaccination_records", []) or []:
        if record.due_date and record.due_date < today and not record.dose_date:
            return True
    return False


def _resolve_model_path() -> Optional[Path]:
    configured = Path(settings.MODEL_ARTIFACT_PATH)
    if configured.is_absolute():
        return configured
    return (_REPO_ROOT / "backend" / configured).resolve()
