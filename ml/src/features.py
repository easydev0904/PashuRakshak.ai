"""Feature engineering shared by training and inference.

Keeping this in one module guarantees `train.py` and `predict.py` build
the exact same feature vector, in the exact same order, from the exact
same raw fields — the #1 source of silent train/serve skew bugs.
"""

from datetime import date, datetime
from typing import Optional

FEATURE_NAMES = [
    "appetite_score",
    "activity_score",
    "water_intake_abnormal",
    "respiratory_score",
    "dung_score",
    "temperature_deviation",
    "temperature_missing",
    "milk_yield_change_pct",
    "milk_yield_missing",
    "concern_score",
    "baseline_7d_concern_score",
    "baseline_14d_concern_score",
    "concern_change_from_baseline",
    "repeated_abnormal_count",
    "species_cattle",
    "species_buffalo",
    "age_band",
    "vaccination_overdue",
    "season_code",
]

_APPETITE_SCORE = {"normal": 0, "reduced": 1, "none": 2}
_ACTIVITY_SCORE = {"normal": 0, "reduced": 1, "lethargic": 2}
_RESPIRATORY_SCORE = {"none": 0, "mild": 1, "coughing": 2, "labored": 3}
_DUNG_SCORE = {"normal": 0, "loose": 1, "diarrhea": 2, "bloody": 3}

NORMAL_TEMPERATURE_MIDPOINT_C = 38.5  # documented prototype assumption


def _concern_score(observation: dict) -> float:
    score = 0.0
    score += _APPETITE_SCORE.get(observation.get("appetite"), 0)
    score += _ACTIVITY_SCORE.get(observation.get("activity"), 0)
    score += _RESPIRATORY_SCORE.get(observation.get("respiratory_sign"), 0)
    score += _DUNG_SCORE.get(observation.get("dung_sign"), 0)
    temp = observation.get("temperature_c")
    if temp is not None:
        score += min(abs(temp - NORMAL_TEMPERATURE_MIDPOINT_C), 5.0) / 2.5
    milk_change = observation.get("milk_yield_change_pct")
    if milk_change is not None and milk_change < 0:
        score += min(abs(milk_change), 60.0) / 20.0
    return score


def _age_band(dob: Optional[date], observed_at: datetime) -> int:
    if dob is None:
        return 1  # unknown -> assume young-adult, the most common band
    age_years = (observed_at.date() - dob).days / 365.25
    if age_years < 1:
        return 0
    if age_years < 3:
        return 1
    if age_years < 8:
        return 2
    return 3


def _season_code(observed_at: datetime) -> int:
    month = observed_at.month
    if month in (6, 7, 8, 9):
        return 0  # monsoon
    if month in (11, 12, 1, 2):
        return 1  # winter
    return 2  # summer


def build_feature_vector(
    observation: dict,
    history: Optional[list] = None,
    context: Optional[dict] = None,
) -> dict:
    """Build a named feature dict for one observation.

    Args:
        observation: current observation fields.
        history: prior observations for the same animal, most-recent
            first, each carrying an `observed_at` datetime alongside
            the same fields as `observation`.
        context: optional dict with `species`, `dob`, `observed_at`,
            `vaccination_overdue`.
    """
    history = history or []
    context = context or {}
    observed_at = context.get("observed_at") or datetime.utcnow()

    within_7d = [h for h in history if (observed_at - h["observed_at"]).days <= 7]
    within_14d = [h for h in history if (observed_at - h["observed_at"]).days <= 14]

    baseline_7d = sum(_concern_score(h) for h in within_7d) / len(within_7d) if within_7d else 0.0
    baseline_14d = (
        sum(_concern_score(h) for h in within_14d) / len(within_14d) if within_14d else 0.0
    )
    current_concern = _concern_score(observation)

    recent_3 = history[:3]
    repeated_abnormal_count = sum(1 for h in recent_3 if _concern_score(h) >= 2.0)

    species = context.get("species", "cattle")
    temp = observation.get("temperature_c")
    milk_change = observation.get("milk_yield_change_pct")

    return {
        "appetite_score": _APPETITE_SCORE.get(observation.get("appetite"), 0),
        "activity_score": _ACTIVITY_SCORE.get(observation.get("activity"), 0),
        "water_intake_abnormal": 0 if observation.get("water_intake") == "normal" else 1,
        "respiratory_score": _RESPIRATORY_SCORE.get(observation.get("respiratory_sign"), 0),
        "dung_score": _DUNG_SCORE.get(observation.get("dung_sign"), 0),
        "temperature_deviation": (
            abs(temp - NORMAL_TEMPERATURE_MIDPOINT_C) if temp is not None else 0.0
        ),
        "temperature_missing": 1 if temp is None else 0,
        "milk_yield_change_pct": milk_change if milk_change is not None else 0.0,
        "milk_yield_missing": 1 if milk_change is None else 0,
        "concern_score": current_concern,
        "baseline_7d_concern_score": baseline_7d,
        "baseline_14d_concern_score": baseline_14d,
        "concern_change_from_baseline": current_concern - baseline_14d,
        "repeated_abnormal_count": repeated_abnormal_count,
        "species_cattle": 1 if species == "cattle" else 0,
        "species_buffalo": 1 if species == "buffalo" else 0,
        "age_band": _age_band(context.get("dob"), observed_at),
        "vaccination_overdue": 1 if context.get("vaccination_overdue") else 0,
        "season_code": _season_code(observed_at),
    }


def feature_dict_to_vector(feature_dict: dict) -> list:
    return [feature_dict[name] for name in FEATURE_NAMES]
