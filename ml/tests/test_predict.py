from datetime import datetime

import pytest

from ml.src.constants import CLINICAL_DISCLAIMER
from ml.src.predict import ModelNotAvailableError, assess, load_model

NORMAL_OBSERVATION = {
    "appetite": "normal",
    "activity": "normal",
    "water_intake": "normal",
    "respiratory_sign": "none",
    "dung_sign": "normal",
    "temperature_c": 38.3,
    "milk_yield_change_pct": 0.0,
}

SEVERE_OBSERVATION = {
    "appetite": "none",
    "activity": "lethargic",
    "water_intake": "reduced",
    "respiratory_sign": "labored",
    "dung_sign": "bloody",
    "temperature_c": 41.2,
    "milk_yield_change_pct": -50.0,
}


def test_model_loads():
    bundle = load_model()
    assert "pipeline" in bundle
    assert bundle["model_version"]


def test_missing_model_raises_clear_error(tmp_path):
    with pytest.raises(ModelNotAvailableError):
        load_model(tmp_path / "does-not-exist.joblib")


def test_assess_returns_required_contract_fields():
    result = assess(NORMAL_OBSERVATION, context={"observed_at": datetime(2026, 1, 1)})
    for key in (
        "risk_score",
        "risk_band",
        "top_factors",
        "model_version",
        "human_review_required",
        "clinical_disclaimer",
    ):
        assert key in result


def test_assess_never_leaks_diagnosis_or_treatment_keys():
    result = assess(SEVERE_OBSERVATION, context={"observed_at": datetime(2026, 1, 1)})
    forbidden = {"diagnosis", "treatment", "prescription", "medication", "confirmed_condition"}
    assert forbidden.isdisjoint(result.keys())


def test_disclaimer_text_is_exact():
    result = assess(NORMAL_OBSERVATION, context={"observed_at": datetime(2026, 1, 1)})
    assert result["clinical_disclaimer"] == "AI screening alert - veterinarian assessment required."
    assert result["clinical_disclaimer"] == CLINICAL_DISCLAIMER


def test_normal_observation_is_low_band():
    result = assess(NORMAL_OBSERVATION, context={"observed_at": datetime(2026, 1, 1)})
    assert result["risk_band"] == "low"
    assert result["human_review_required"] is False


def test_severe_observation_is_high_band_and_requires_review():
    result = assess(SEVERE_OBSERVATION, context={"observed_at": datetime(2026, 1, 1)})
    assert result["risk_band"] == "high"
    assert result["human_review_required"] is True
    assert len(result["top_factors"]) >= 2
    assert len(result["top_factors"]) <= 4


def test_urgent_rule_forces_high_band_even_with_low_model_score():
    # appetite "none" alone is urgent per the rule engine regardless of
    # how the statistical model scores the rest of the observation.
    obs = {**NORMAL_OBSERVATION, "appetite": "none"}
    result = assess(obs, context={"observed_at": datetime(2026, 1, 1)})
    assert result["risk_band"] == "high"


def test_risk_score_is_bounded():
    result = assess(SEVERE_OBSERVATION, context={"observed_at": datetime(2026, 1, 1)})
    assert 0.0 <= result["risk_score"] <= 1.0


def test_missing_optional_fields_do_not_crash():
    minimal = {
        "appetite": "normal",
        "activity": "normal",
        "water_intake": "normal",
        "respiratory_sign": "none",
        "dung_sign": "normal",
        "temperature_c": None,
        "milk_yield_change_pct": None,
    }
    result = assess(minimal)
    assert result["risk_band"] in ("low", "medium", "high")
