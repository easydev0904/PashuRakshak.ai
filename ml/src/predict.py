"""Scoring contract: combines the learned model with the transparent
rule engine to produce a LOW / MEDIUM / HIGH early-warning risk band.

This module is intentionally the *only* place that turns model output
into a risk band, so the safety behavior (rules can force HIGH; the
disclaimer text; never emitting a "diagnosis") lives in one place.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

import joblib

from ml.src.constants import CLINICAL_DISCLAIMER, HIGH_THRESHOLD, MEDIUM_THRESHOLD, MODEL_VERSION
from ml.src.features import FEATURE_NAMES, build_feature_vector
from ml.src.rules import evaluate_rules

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_PATH = REPO_ROOT / "ml" / "models" / "risk_model.joblib"

_FEATURE_EXPLANATIONS = {
    "concern_change_from_baseline": (
        "Reported signs have worsened compared to this animal's recent baseline"
    ),
    "baseline_14d_concern_score": "Signs have been elevated across recent observations",
    "milk_yield_change_pct": "Milk yield has decreased compared to usual",
    "temperature_deviation": "Recorded temperature is different from the usual range",
    "repeated_abnormal_count": "Multiple recent observations have also shown concerning signs",
}

_model_cache: dict = {}


class ModelNotAvailableError(Exception):
    """Raised when the trained model artifact cannot be loaded."""


def load_model(path: Optional[Path] = None) -> dict:
    path = Path(path) if path else DEFAULT_MODEL_PATH
    cache_key = str(path)
    if cache_key in _model_cache:
        return _model_cache[cache_key]
    if not path.exists():
        raise ModelNotAvailableError(
            f"Model artifact not found at {path}. Run `python -m ml.src.train` first."
        )
    bundle = joblib.load(path)
    _model_cache[cache_key] = bundle
    return bundle


def _explain(feature_dict: dict, rule_factors: list, max_factors: int = 4) -> list:
    factors = list(rule_factors)
    if len(factors) >= max_factors:
        return factors[:max_factors]

    for name, text in _FEATURE_EXPLANATIONS.items():
        if len(factors) >= max_factors:
            break
        value = feature_dict.get(name, 0)
        already_present = any(text == f.get("reason") for f in factors)
        if already_present:
            continue
        if name == "milk_yield_change_pct" and value < -10:
            factors.append({"rule": name, "reason": text, "severity": "medium"})
        elif name != "milk_yield_change_pct" and isinstance(value, (int, float)) and value >= 1.5:
            factors.append({"rule": name, "reason": text, "severity": "low"})

    return factors[:max_factors]


def assess(
    observation: dict,
    history: Optional[list] = None,
    context: Optional[dict] = None,
    model_path: Optional[Path] = None,
) -> dict:
    """Score one observation. Returns the API-safe risk assessment payload.

    Never returns a diagnosis, treatment, or prescription — only a risk
    band, score, contributing factors, and the mandatory disclaimer.
    """
    history = history or []
    context = context or {}
    context.setdefault("observed_at", datetime.utcnow())

    flags = evaluate_rules(observation, history)

    feature_dict = build_feature_vector(observation, history, context)
    feature_vector = [[feature_dict[name] for name in FEATURE_NAMES]]

    bundle = load_model(model_path)
    pipeline = bundle["pipeline"]
    probability = float(pipeline.predict_proba(feature_vector)[0][1])

    score = max(probability, flags.minimum_risk_score)

    if flags.urgent:
        band = "high"
    elif score >= HIGH_THRESHOLD:
        band = "high"
    elif score >= MEDIUM_THRESHOLD:
        band = "medium"
    else:
        band = "low"

    factors = _explain(feature_dict, flags.as_factor_dicts())

    return {
        "risk_score": round(score, 4),
        "risk_band": band,
        "top_factors": factors,
        "model_version": bundle.get("model_version", MODEL_VERSION),
        "human_review_required": band == "high",
        "clinical_disclaimer": CLINICAL_DISCLAIMER,
    }
