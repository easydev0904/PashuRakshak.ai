from datetime import date, datetime, timedelta

from ml.src.features import FEATURE_NAMES, build_feature_vector, feature_dict_to_vector

BASE_OBSERVATION = {
    "appetite": "normal",
    "activity": "normal",
    "water_intake": "normal",
    "respiratory_sign": "none",
    "dung_sign": "normal",
    "temperature_c": 38.3,
    "milk_yield_change_pct": 0.0,
}


def test_feature_vector_has_expected_keys():
    features = build_feature_vector(BASE_OBSERVATION, [], {"observed_at": datetime(2026, 1, 1)})
    assert set(features.keys()) == set(FEATURE_NAMES)


def test_feature_dict_to_vector_preserves_order():
    features = build_feature_vector(BASE_OBSERVATION, [], {"observed_at": datetime(2026, 1, 1)})
    vector = feature_dict_to_vector(features)
    assert vector == [features[name] for name in FEATURE_NAMES]


def test_missing_temperature_sets_missing_flag():
    obs = {**BASE_OBSERVATION, "temperature_c": None}
    features = build_feature_vector(obs, [], {"observed_at": datetime(2026, 1, 1)})
    assert features["temperature_missing"] == 1
    assert features["temperature_deviation"] == 0.0


def test_missing_milk_yield_sets_missing_flag():
    obs = {**BASE_OBSERVATION, "milk_yield_change_pct": None}
    features = build_feature_vector(obs, [], {"observed_at": datetime(2026, 1, 1)})
    assert features["milk_yield_missing"] == 1


def test_history_within_window_affects_baseline():
    observed_at = datetime(2026, 1, 15)
    history = [
        {**BASE_OBSERVATION, "appetite": "reduced", "observed_at": observed_at - timedelta(days=2)},
        {**BASE_OBSERVATION, "appetite": "reduced", "observed_at": observed_at - timedelta(days=4)},
    ]
    features = build_feature_vector(BASE_OBSERVATION, history, {"observed_at": observed_at})
    assert features["baseline_7d_concern_score"] > 0


def test_history_outside_window_excluded():
    observed_at = datetime(2026, 1, 15)
    history = [
        {**BASE_OBSERVATION, "appetite": "none", "observed_at": observed_at - timedelta(days=30)},
    ]
    features = build_feature_vector(BASE_OBSERVATION, history, {"observed_at": observed_at})
    assert features["baseline_14d_concern_score"] == 0.0


def test_species_one_hot():
    features = build_feature_vector(
        BASE_OBSERVATION, [], {"species": "buffalo", "observed_at": datetime(2026, 1, 1)}
    )
    assert features["species_buffalo"] == 1
    assert features["species_cattle"] == 0


def test_age_band_from_dob():
    observed_at = datetime(2026, 1, 1)
    calf = build_feature_vector(
        BASE_OBSERVATION, [], {"dob": date(2025, 8, 1), "observed_at": observed_at}
    )
    senior = build_feature_vector(
        BASE_OBSERVATION, [], {"dob": date(2010, 1, 1), "observed_at": observed_at}
    )
    assert calf["age_band"] == 0
    assert senior["age_band"] == 3


def test_unknown_dob_defaults_to_young_adult_band():
    features = build_feature_vector(BASE_OBSERVATION, [], {"observed_at": datetime(2026, 1, 1)})
    assert features["age_band"] == 1
