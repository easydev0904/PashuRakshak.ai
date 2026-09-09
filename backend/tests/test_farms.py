from tests.conftest import auth_header


def test_create_farm_as_farmer(client, farmer_user):
    headers = auth_header(client, "farmer@example.com")
    resp = client.post(
        "/api/v1/farms",
        json={"name": "My Farm", "village": "Rampur", "district": "Meerut", "state": "UP"},
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json()["name"] == "My Farm"


def test_farmer_sees_only_own_farms(client, farmer_user, other_farm):
    headers = auth_header(client, "farmer@example.com")
    resp = client.post("/api/v1/farms", json={"name": "Mine"}, headers=headers)
    assert resp.status_code == 201

    resp = client.get("/api/v1/farms", headers=headers)
    assert resp.status_code == 200
    names = [f["name"] for f in resp.json()]
    assert "Mine" in names
    assert "Other Farm" not in names


def test_vet_sees_all_farms(client, vet_user, farm, other_farm):
    headers = auth_header(client, "vet@example.com")
    resp = client.get("/api/v1/farms", headers=headers)
    assert resp.status_code == 200
    names = [f["name"] for f in resp.json()]
    assert "Green Valley Farm" in names
    assert "Other Farm" in names


def test_farms_require_auth(client):
    resp = client.get("/api/v1/farms")
    assert resp.status_code == 401
