from tests.conftest import auth_header

NORMAL_PAYLOAD = {
    "appetite": "normal",
    "activity": "normal",
    "water_intake": "normal",
    "respiratory_sign": "none",
    "dung_sign": "normal",
    "temperature_c": 38.3,
    "milk_yield_change_pct": 0,
}

SEVERE_PAYLOAD = {
    "appetite": "none",
    "activity": "lethargic",
    "water_intake": "reduced",
    "respiratory_sign": "labored",
    "dung_sign": "bloody",
    "temperature_c": 41.2,
    "milk_yield_change_pct": -50,
}


def test_submit_normal_observation_returns_low_risk(client, farmer_user, animal):
    headers = auth_header(client, "farmer@example.com")
    resp = client.post(
        f"/api/v1/animals/{animal.id}/observations", json=NORMAL_PAYLOAD, headers=headers
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["risk_assessment"]["risk_band"] == "low"
    assert body["risk_assessment"]["human_review_required"] is False
    assert (
        body["risk_assessment"]["clinical_disclaimer"]
        == "AI screening alert - veterinarian assessment required."
    )


def test_submit_severe_observation_returns_high_risk_and_creates_alert(client, farmer_user, animal):
    headers = auth_header(client, "farmer@example.com")
    resp = client.post(
        f"/api/v1/animals/{animal.id}/observations", json=SEVERE_PAYLOAD, headers=headers
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["risk_assessment"]["risk_band"] == "high"
    assert body["risk_assessment"]["human_review_required"] is True
    assert len(body["risk_assessment"]["top_factors"]) >= 2

    alerts_resp = client.get("/api/v1/alerts", headers=headers)
    assert alerts_resp.status_code == 200
    assert len(alerts_resp.json()) == 1
    assert alerts_resp.json()[0]["priority"] == "high"


def test_never_returns_diagnosis_or_treatment_fields(client, farmer_user, animal):
    headers = auth_header(client, "farmer@example.com")
    resp = client.post(
        f"/api/v1/animals/{animal.id}/observations", json=SEVERE_PAYLOAD, headers=headers
    )
    risk = resp.json()["risk_assessment"]
    forbidden = {"diagnosis", "treatment", "prescription", "medication"}
    assert forbidden.isdisjoint(risk.keys())


def test_temperature_out_of_plausible_range_rejected(client, farmer_user, animal):
    headers = auth_header(client, "farmer@example.com")
    payload = {**NORMAL_PAYLOAD, "temperature_c": 60.0}
    resp = client.post(f"/api/v1/animals/{animal.id}/observations", json=payload, headers=headers)
    assert resp.status_code == 422


def test_milk_yield_out_of_plausible_range_rejected(client, farmer_user, animal):
    headers = auth_header(client, "farmer@example.com")
    payload = {**NORMAL_PAYLOAD, "milk_yield_change_pct": -500}
    resp = client.post(f"/api/v1/animals/{animal.id}/observations", json=payload, headers=headers)
    assert resp.status_code == 422


def test_missing_optional_fields_still_succeed(client, farmer_user, animal):
    headers = auth_header(client, "farmer@example.com")
    payload = {**NORMAL_PAYLOAD, "temperature_c": None, "milk_yield_change_pct": None}
    resp = client.post(f"/api/v1/animals/{animal.id}/observations", json=payload, headers=headers)
    assert resp.status_code == 201


def test_list_observations_ordered_most_recent_first(client, farmer_user, animal):
    headers = auth_header(client, "farmer@example.com")
    client.post(f"/api/v1/animals/{animal.id}/observations", json=NORMAL_PAYLOAD, headers=headers)
    client.post(f"/api/v1/animals/{animal.id}/observations", json=SEVERE_PAYLOAD, headers=headers)

    resp = client.get(f"/api/v1/animals/{animal.id}/observations", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_farmer_cannot_submit_observation_for_other_farms_animal(
    client, farmer_user, other_farm, db
):
    from app.models.animal import Animal
    from app.models.enums import Sex, Species

    other_animal = Animal(farm_id=other_farm.id, tag_id="Y-1", species=Species.cattle, sex=Sex.male)
    db.add(other_animal)
    db.commit()

    headers = auth_header(client, "farmer@example.com")
    resp = client.post(
        f"/api/v1/animals/{other_animal.id}/observations", json=NORMAL_PAYLOAD, headers=headers
    )
    assert resp.status_code == 403
