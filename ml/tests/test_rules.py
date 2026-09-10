from ml.src.rules import evaluate_rules

NORMAL_OBSERVATION = {
    "appetite": "normal",
    "activity": "normal",
    "water_intake": "normal",
    "respiratory_sign": "none",
    "dung_sign": "normal",
    "temperature_c": 38.3,
    "milk_yield_change_pct": 0.0,
}


def test_normal_observation_triggers_nothing():
    result = evaluate_rules(NORMAL_OBSERVATION)
    assert result.triggered == []
    assert result.minimum_risk_score == 0.0
    assert result.urgent is False


def test_appetite_loss_is_urgent_and_high():
    obs = {**NORMAL_OBSERVATION, "appetite": "none"}
    result = evaluate_rules(obs)
    assert result.urgent is True
    assert result.minimum_risk_score == 0.75
    assert any(t.rule == "appetite_loss" for t in result.triggered)


def test_appetite_reduced_is_medium_not_urgent():
    obs = {**NORMAL_OBSERVATION, "appetite": "reduced"}
    result = evaluate_rules(obs)
    assert result.urgent is False
    assert result.minimum_risk_score == 0.45


def test_bloody_dung_is_urgent():
    obs = {**NORMAL_OBSERVATION, "dung_sign": "bloody"}
    result = evaluate_rules(obs)
    assert result.urgent is True


def test_labored_breathing_is_urgent():
    obs = {**NORMAL_OBSERVATION, "respiratory_sign": "labored"}
    result = evaluate_rules(obs)
    assert result.urgent is True


def test_high_fever_is_urgent():
    obs = {**NORMAL_OBSERVATION, "temperature_c": 41.0}
    result = evaluate_rules(obs)
    assert result.urgent is True
    assert any(t.rule == "temperature_high_urgent" for t in result.triggered)


def test_elevated_temperature_below_urgent_threshold_is_medium_not_urgent():
    obs = {**NORMAL_OBSERVATION, "temperature_c": 39.8}
    result = evaluate_rules(obs)
    assert result.urgent is False
    assert any(t.rule == "temperature_elevated" for t in result.triggered)


def test_low_temperature_flagged():
    obs = {**NORMAL_OBSERVATION, "temperature_c": 36.0}
    result = evaluate_rules(obs)
    assert any(t.rule == "temperature_low" for t in result.triggered)


def test_missing_temperature_does_not_trigger_temperature_rules():
    obs = {**NORMAL_OBSERVATION, "temperature_c": None}
    result = evaluate_rules(obs)
    assert all("temperature" not in t.rule for t in result.triggered)


def test_sharp_milk_decline_triggers_high_not_urgent():
    obs = {**NORMAL_OBSERVATION, "milk_yield_change_pct": -45.0}
    result = evaluate_rules(obs)
    assert result.urgent is False
    assert result.minimum_risk_score == 0.75


def test_repeated_abnormal_observations_escalate():
    obs = {**NORMAL_OBSERVATION, "appetite": "reduced"}
    history = [
        {**NORMAL_OBSERVATION, "appetite": "reduced"},
        {**NORMAL_OBSERVATION, "activity": "reduced"},
        {**NORMAL_OBSERVATION},
    ]
    result = evaluate_rules(obs, history)
    assert any(t.rule == "repeated_abnormal_observations" for t in result.triggered)


def test_no_history_does_not_crash():
    result = evaluate_rules(NORMAL_OBSERVATION, history=None)
    assert result.triggered == []
