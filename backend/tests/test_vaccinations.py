from tests.conftest import auth_header


def test_create_and_list_vaccination_record(client, farmer_user, farm, animal):
    headers = auth_header(client, "farmer@example.com")
    resp = client.post(
        f"/api/v1/animals/{animal.id}/vaccinations",
        json={"vaccine_name": "FMD vaccine", "due_date": "2026-06-01"},
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json()["vaccine_name"] == "FMD vaccine"

    resp = client.get(f"/api/v1/animals/{animal.id}/vaccinations", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_cannot_add_vaccination_to_other_farms_animal(client, farmer_user, other_farm, db):
    from app.models.animal import Animal
    from app.models.enums import Sex, Species

    other_animal = Animal(
        farm_id=other_farm.id, tag_id="Z-1", species=Species.buffalo, sex=Sex.male
    )
    db.add(other_animal)
    db.commit()

    headers = auth_header(client, "farmer@example.com")
    resp = client.post(
        f"/api/v1/animals/{other_animal.id}/vaccinations",
        json={"vaccine_name": "FMD vaccine"},
        headers=headers,
    )
    assert resp.status_code == 403
