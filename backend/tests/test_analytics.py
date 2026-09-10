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


def test_farm_trends_reflects_observations(client, farmer_user, farm, animal):
    headers = auth_header(client, "farmer@example.com")
    client.post(f"/api/v1/animals/{animal.id}/observations", json=NORMAL_PAYLOAD, headers=headers)

    resp = client.get(f"/api/v1/analytics/farm-trends?farm_id={farm.id}", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_animals"] == 1
    assert body["total_observations"] == 1
    assert "this village has an outbreak" not in body["note"].lower()
    assert "aggregated" in body["note"].lower() or "not a confirmed" in body["note"].lower()


def test_farmer_cannot_view_other_farms_trends(client, farmer_user, other_farm):
    headers = auth_header(client, "farmer@example.com")
    resp = client.get(f"/api/v1/analytics/farm-trends?farm_id={other_farm.id}", headers=headers)
    assert resp.status_code == 403


def test_analytics_requires_farm_id(client, farmer_user):
    headers = auth_header(client, "farmer@example.com")
    resp = client.get("/api/v1/analytics/farm-trends", headers=headers)
    assert resp.status_code == 422
