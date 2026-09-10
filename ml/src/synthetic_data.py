"""Synthetic training-data generator.

IMPORTANT: This generates entirely synthetic, made-up records for
prototype/demo purposes. It is NOT derived from real animal health
data and must never be treated as a clinically meaningful dataset.
The generative process below encodes a caricature of "healthy" vs.
"at-risk" patterns purely so the baseline classifier has something
non-trivial to learn during the SIH demo.
"""

import random
from datetime import datetime, timedelta

from ml.src.features import FEATURE_NAMES, build_feature_vector

REFERENCE_DATE = datetime(2026, 1, 15)


def _sample_observation(rng: random.Random, at_risk: bool) -> dict:
    if at_risk:
        appetite = rng.choices(["normal", "reduced", "none"], weights=[0.25, 0.5, 0.25])[0]
        activity = rng.choices(["normal", "reduced", "lethargic"], weights=[0.3, 0.45, 0.25])[0]
        water_intake = rng.choices(["normal", "reduced", "increased"], weights=[0.5, 0.4, 0.1])[0]
        respiratory = rng.choices(
            ["none", "mild", "coughing", "labored"], weights=[0.35, 0.25, 0.25, 0.15]
        )[0]
        dung = rng.choices(
            ["normal", "loose", "diarrhea", "bloody"], weights=[0.35, 0.3, 0.25, 0.1]
        )[0]
        temp = None if rng.random() < 0.15 else round(rng.gauss(39.3, 1.0), 1)
        milk_change = None if rng.random() < 0.2 else round(rng.gauss(-15, 20), 1)
    else:
        appetite = rng.choices(["normal", "reduced", "none"], weights=[0.88, 0.11, 0.01])[0]
        activity = rng.choices(["normal", "reduced", "lethargic"], weights=[0.88, 0.11, 0.01])[0]
        water_intake = rng.choices(["normal", "reduced", "increased"], weights=[0.85, 0.1, 0.05])[0]
        respiratory = rng.choices(
            ["none", "mild", "coughing", "labored"], weights=[0.85, 0.1, 0.04, 0.01]
        )[0]
        dung = rng.choices(
            ["normal", "loose", "diarrhea", "bloody"], weights=[0.85, 0.1, 0.04, 0.01]
        )[0]
        temp = None if rng.random() < 0.15 else round(rng.gauss(38.3, 0.4), 1)
        milk_change = None if rng.random() < 0.2 else round(rng.gauss(0, 5), 1)

    if temp is not None:
        temp = max(35.0, min(42.0, temp))
    if milk_change is not None:
        milk_change = max(-80.0, min(40.0, milk_change))

    return {
        "appetite": appetite,
        "activity": activity,
        "water_intake": water_intake,
        "respiratory_sign": respiratory,
        "dung_sign": dung,
        "temperature_c": temp,
        "milk_yield_change_pct": milk_change,
    }


def _sample_history(rng: random.Random, at_risk: bool, observed_at: datetime) -> list:
    n_history = rng.choice([0, 1, 2, 3])
    history = []
    for _i in range(n_history):
        days_ago = rng.randint(1, 13)
        past_at_risk = at_risk if rng.random() < 0.6 else (not at_risk and rng.random() < 0.15)
        past_obs = _sample_observation(rng, bool(past_at_risk))
        past_obs["observed_at"] = observed_at - timedelta(days=days_ago)
        history.append(past_obs)
    history.sort(key=lambda h: h["observed_at"], reverse=True)
    return history


def generate_synthetic_dataset(n_samples: int = 4000, seed: int = 42):
    """Return (feature_rows, labels, group_ids) as parallel lists.

    group_ids simulate a synthetic farm/animal grouping so evaluation
    can do a group-aware (not just random) train/test split.
    """
    rng = random.Random(seed)
    feature_rows = []
    labels = []
    group_ids = []

    n_groups = max(20, n_samples // 15)

    for i in range(n_samples):
        group_id = f"synthetic-farm-{i % n_groups:03d}"
        at_risk = rng.random() < 0.28
        # 5% label noise: flip some labels so the classifier can't perfectly
        # separate on the generative rule alone (mirrors real-world noise).
        label = at_risk if rng.random() > 0.05 else (not at_risk)

        day_offset = rng.randint(0, 364)
        observed_at = REFERENCE_DATE - timedelta(days=day_offset)

        observation = _sample_observation(rng, at_risk)
        history = _sample_history(rng, at_risk, observed_at)

        species = rng.choices(["cattle", "buffalo"], weights=[0.6, 0.4])[0]
        age_years = rng.choices([0.5, 2, 5, 10], weights=[0.1, 0.35, 0.4, 0.15])[0]
        dob = (observed_at - timedelta(days=int(age_years * 365.25))).date()
        vaccination_overdue = rng.random() < 0.15

        context = {
            "species": species,
            "dob": dob,
            "observed_at": observed_at,
            "vaccination_overdue": vaccination_overdue,
        }

        feature_dict = build_feature_vector(observation, history, context)
        feature_rows.append([feature_dict[name] for name in FEATURE_NAMES])
        labels.append(int(label))
        group_ids.append(group_id)

    return feature_rows, labels, group_ids
