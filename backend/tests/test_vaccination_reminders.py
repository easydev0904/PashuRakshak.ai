from datetime import date, timedelta

from tests.conftest import auth_header


def test_vaccinations_due_soon_includes_upcoming_and_overdue(client, farmer_user, farm, animal):
    headers = auth_header(client, "farmer@example.com")

    client.post(
        f"/api/v1/animals/{animal.id}/vaccinations",
        json={
            "vaccine_name": "Overdue Shot",
            "due_date": (date.today() - timedelta(days=3)).isoformat(),
        },
        headers=headers,
    )
    client.post(
        f"/api/v1/animals/{animal.id}/vaccinations",
        json={
            "vaccine_name": "Upcoming Shot",
            "due_date": (date.today() + timedelta(days=5)).isoformat(),
        },
        headers=headers,
    )
    client.post(
        f"/api/v1/animals/{animal.id}/vaccinations",
        json={
            "vaccine_name": "Far Future Shot",
            "due_date": (date.today() + timedelta(days=60)).isoformat(),
        },
        headers=headers,
    )
    client.post(
        f"/api/v1/animals/{animal.id}/vaccinations",
        json={
            "vaccine_name": "Booster Due Soon",
            "dose_date": (date.today() - timedelta(days=120)).isoformat(),
            "due_date": (date.today() + timedelta(days=5)).isoformat(),
        },
        headers=headers,
    )
    client.post(
        f"/api/v1/animals/{animal.id}/vaccinations",
        json={"vaccine_name": "No Due Date Set"},
        headers=headers,
    )

    resp = client.get(f"/api/v1/farms/{farm.id}/vaccinations-due", headers=headers)
    assert resp.status_code == 200
    names = {v["vaccine_name"] for v in resp.json()}
    # A record with a past dose_date but an approaching due_date (a
    # booster) must still surface as a reminder -- dose_date only says
    # a dose happened once, not that nothing is due now.
    assert names == {"Overdue Shot", "Upcoming Shot", "Booster Due Soon"}
    assert all(v["animal_tag_id"] == animal.tag_id for v in resp.json())


def test_vaccinations_due_soon_requires_farm_access(client, farmer_user, other_farm):
    headers = auth_header(client, "farmer@example.com")
    resp = client.get(f"/api/v1/farms/{other_farm.id}/vaccinations-due", headers=headers)
    assert resp.status_code == 403
