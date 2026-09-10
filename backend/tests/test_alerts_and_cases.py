from tests.conftest import auth_header

SEVERE_PAYLOAD = {
    "appetite": "none",
    "activity": "lethargic",
    "water_intake": "reduced",
    "respiratory_sign": "labored",
    "dung_sign": "bloody",
    "temperature_c": 41.2,
    "milk_yield_change_pct": -50,
}


def _create_high_alert(client, farmer_headers, animal):
    resp = client.post(
        f"/api/v1/animals/{animal.id}/observations", json=SEVERE_PAYLOAD, headers=farmer_headers
    )
    assert resp.status_code == 201
    return resp


def test_vet_sees_alert_farmer_created(client, farmer_user, vet_user, farm, animal):
    farmer_headers = auth_header(client, "farmer@example.com")
    _create_high_alert(client, farmer_headers, animal)

    vet_headers = auth_header(client, "vet@example.com")
    resp = client.get("/api/v1/alerts", headers=vet_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_farmer_cannot_review_alert(client, farmer_user, farm, animal):
    farmer_headers = auth_header(client, "farmer@example.com")
    _create_high_alert(client, farmer_headers, animal)
    alert_id = client.get("/api/v1/alerts", headers=farmer_headers).json()[0]["id"]

    resp = client.post(
        f"/api/v1/alerts/{alert_id}/review",
        json={"action": "acknowledge"},
        headers=farmer_headers,
    )
    assert resp.status_code == 403


def test_vet_can_acknowledge_alert(client, farmer_user, vet_user, farm, animal):
    farmer_headers = auth_header(client, "farmer@example.com")
    _create_high_alert(client, farmer_headers, animal)
    vet_headers = auth_header(client, "vet@example.com")
    alert_id = client.get("/api/v1/alerts", headers=vet_headers).json()[0]["id"]

    resp = client.post(
        f"/api/v1/alerts/{alert_id}/review",
        json={"action": "acknowledge"},
        headers=vet_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "acknowledged"
    assert resp.json()["acknowledged_at"] is not None


def test_request_follow_up_creates_case(client, farmer_user, vet_user, farm, animal):
    farmer_headers = auth_header(client, "farmer@example.com")
    _create_high_alert(client, farmer_headers, animal)
    vet_headers = auth_header(client, "vet@example.com")
    alert_id = client.get("/api/v1/alerts", headers=vet_headers).json()[0]["id"]

    resp = client.post(
        f"/api/v1/alerts/{alert_id}/review",
        json={"action": "request_follow_up", "note": "Clinical review requested"},
        headers=vet_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "in_review"

    cases_resp = client.get(f"/api/v1/animals/{animal.id}/cases", headers=vet_headers)
    assert cases_resp.status_code == 200
    assert len(cases_resp.json()) == 1
    assert cases_resp.json()[0]["status"] == "follow_up"


def test_alert_detail_shows_full_context(client, farmer_user, vet_user, farm, animal):
    farmer_headers = auth_header(client, "farmer@example.com")
    _create_high_alert(client, farmer_headers, animal)
    vet_headers = auth_header(client, "vet@example.com")
    alert_id = client.get("/api/v1/alerts", headers=vet_headers).json()[0]["id"]

    resp = client.get(f"/api/v1/alerts/{alert_id}", headers=vet_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["animal"]["id"] == animal.id
    assert body["farm_name"] == "Green Valley Farm"
    assert "clinical_disclaimer" in body["risk_assessment"]


def test_vet_can_set_confirmed_condition_on_case(client, farmer_user, vet_user, farm, animal):
    farmer_headers = auth_header(client, "farmer@example.com")
    _create_high_alert(client, farmer_headers, animal)
    vet_headers = auth_header(client, "vet@example.com")
    alert_id = client.get("/api/v1/alerts", headers=vet_headers).json()[0]["id"]
    client.post(
        f"/api/v1/alerts/{alert_id}/review",
        json={"action": "request_follow_up"},
        headers=vet_headers,
    )
    case_id = client.get(f"/api/v1/animals/{animal.id}/cases", headers=vet_headers).json()[0]["id"]

    resp = client.patch(
        f"/api/v1/cases/{case_id}",
        json={
            "confirmed_condition": "Suspected FMD (veterinarian assessed)",
            "confirmation_basis": "Clinical exam on-farm",
            "status": "resolved",
        },
        headers=vet_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["confirmed_condition"] == "Suspected FMD (veterinarian assessed)"
    assert body["status"] == "resolved"
    assert body["closed_at"] is not None


def test_farmer_cannot_set_confirmed_condition(client, farmer_user, vet_user, farm, animal):
    farmer_headers = auth_header(client, "farmer@example.com")
    _create_high_alert(client, farmer_headers, animal)
    vet_headers = auth_header(client, "vet@example.com")
    alert_id = client.get("/api/v1/alerts", headers=vet_headers).json()[0]["id"]
    client.post(
        f"/api/v1/alerts/{alert_id}/review",
        json={"action": "request_follow_up"},
        headers=vet_headers,
    )
    case_id = client.get(f"/api/v1/animals/{animal.id}/cases", headers=vet_headers).json()[0]["id"]

    resp = client.patch(
        f"/api/v1/cases/{case_id}",
        json={"confirmed_condition": "Should not be allowed"},
        headers=farmer_headers,
    )
    assert resp.status_code == 403


def test_closed_alert_update_still_allowed_for_resolution_note(
    client, farmer_user, vet_user, farm, animal
):
    farmer_headers = auth_header(client, "farmer@example.com")
    _create_high_alert(client, farmer_headers, animal)
    vet_headers = auth_header(client, "vet@example.com")
    alert_id = client.get("/api/v1/alerts", headers=vet_headers).json()[0]["id"]

    resp = client.post(
        f"/api/v1/alerts/{alert_id}/review",
        json={"action": "resolve", "note": "No concern found on visit"},
        headers=vet_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "resolved"
    assert resp.json()["resolution"] == "No concern found on visit"


def test_reviewing_an_already_resolved_alert_does_not_error(
    client, farmer_user, vet_user, farm, animal
):
    farmer_headers = auth_header(client, "farmer@example.com")
    _create_high_alert(client, farmer_headers, animal)
    vet_headers = auth_header(client, "vet@example.com")
    alert_id = client.get("/api/v1/alerts", headers=vet_headers).json()[0]["id"]

    client.post(
        f"/api/v1/alerts/{alert_id}/review", json={"action": "resolve"}, headers=vet_headers
    )
    resp = client.post(
        f"/api/v1/alerts/{alert_id}/review",
        json={"action": "acknowledge"},
        headers=vet_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "acknowledged"


def test_review_action_rejects_unknown_action(client, farmer_user, vet_user, farm, animal):
    farmer_headers = auth_header(client, "farmer@example.com")
    _create_high_alert(client, farmer_headers, animal)
    vet_headers = auth_header(client, "vet@example.com")
    alert_id = client.get("/api/v1/alerts", headers=vet_headers).json()[0]["id"]

    resp = client.post(
        f"/api/v1/alerts/{alert_id}/review",
        json={"action": "delete_everything"},
        headers=vet_headers,
    )
    assert resp.status_code == 422


def test_nonexistent_alert_returns_404(client, vet_user):
    headers = auth_header(client, "vet@example.com")
    resp = client.get("/api/v1/alerts/does-not-exist", headers=headers)
    assert resp.status_code == 404
