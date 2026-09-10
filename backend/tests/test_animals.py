from tests.conftest import auth_header


def test_create_animal_on_own_farm(client, farmer_user, farm):
    headers = auth_header(client, "farmer@example.com")
    resp = client.post(
        "/api/v1/animals",
        json={"farm_id": farm.id, "tag_id": "COW-001", "species": "cattle", "sex": "female"},
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json()["tag_id"] == "COW-001"


def test_cannot_create_animal_on_other_farm(client, farmer_user, other_farm):
    headers = auth_header(client, "farmer@example.com")
    resp = client.post(
        "/api/v1/animals",
        json={"farm_id": other_farm.id, "tag_id": "COW-999", "species": "cattle", "sex": "male"},
        headers=headers,
    )
    assert resp.status_code == 403


def test_duplicate_tag_id_on_same_farm_conflicts(client, farmer_user, farm, animal):
    headers = auth_header(client, "farmer@example.com")
    resp = client.post(
        "/api/v1/animals",
        json={"farm_id": farm.id, "tag_id": animal.tag_id, "species": "cattle", "sex": "male"},
        headers=headers,
    )
    assert resp.status_code == 409


def test_farmer_cannot_read_other_farms_animal(client, farmer_user, other_farm, db):
    from app.models.animal import Animal
    from app.models.enums import Sex, Species

    other_animal = Animal(
        farm_id=other_farm.id, tag_id="X-1", species=Species.buffalo, sex=Sex.female
    )
    db.add(other_animal)
    db.commit()

    headers = auth_header(client, "farmer@example.com")
    resp = client.get(f"/api/v1/animals/{other_animal.id}", headers=headers)
    assert resp.status_code == 403


def test_nonexistent_animal_returns_404(client, farmer_user):
    headers = auth_header(client, "farmer@example.com")
    resp = client.get("/api/v1/animals/does-not-exist", headers=headers)
    assert resp.status_code == 404


def test_get_animal_includes_summary_fields(client, farmer_user, farm, animal):
    headers = auth_header(client, "farmer@example.com")
    resp = client.get(f"/api/v1/animals/{animal.id}", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "needs_checkin_today" in body
    assert body["needs_checkin_today"] is True
    assert body["last_observation_at"] is None
