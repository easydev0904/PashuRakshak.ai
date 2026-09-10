def test_list_education_content_empty_state(client):
    resp = client.get("/api/v1/education")
    assert resp.status_code == 200
    assert resp.json() == []


def test_admin_can_create_content(client, admin_user):
    from tests.conftest import auth_header

    headers = auth_header(client, "admin@example.com")
    resp = client.post(
        "/api/v1/education",
        json={
            "category": "vaccination",
            "title": "Why vaccinate on schedule",
            "language": "en",
            "body": "Regular vaccination reduces the risk of common outbreaks.",
        },
        headers=headers,
    )
    assert resp.status_code == 201

    list_resp = client.get("/api/v1/education")
    assert len(list_resp.json()) == 1


def test_farmer_cannot_create_content(client, farmer_user):
    from tests.conftest import auth_header

    headers = auth_header(client, "farmer@example.com")
    resp = client.post(
        "/api/v1/education",
        json={
            "category": "hygiene",
            "title": "Keep water troughs clean",
            "language": "en",
            "body": "Clean water troughs regularly.",
        },
        headers=headers,
    )
    assert resp.status_code == 403


def test_unpublished_content_not_listed(client, admin_user):
    from tests.conftest import auth_header

    headers = auth_header(client, "admin@example.com")
    client.post(
        "/api/v1/education",
        json={
            "category": "nutrition",
            "title": "Draft article",
            "language": "en",
            "body": "Not ready yet.",
            "is_published": False,
        },
        headers=headers,
    )
    resp = client.get("/api/v1/education")
    assert resp.json() == []
