from tests.conftest import auth_header


def test_admin_can_list_users(client, admin_user, farmer_user, vet_user):
    headers = auth_header(client, "admin@example.com")
    resp = client.get("/api/v1/users", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 3


def test_admin_can_filter_users_by_role(client, admin_user, farmer_user, vet_user):
    headers = auth_header(client, "admin@example.com")
    resp = client.get("/api/v1/users?role=farmer", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["role"] == "farmer"


def test_non_admin_cannot_list_users(client, farmer_user):
    headers = auth_header(client, "farmer@example.com")
    resp = client.get("/api/v1/users", headers=headers)
    assert resp.status_code == 403


def test_admin_can_create_user(client, admin_user):
    headers = auth_header(client, "admin@example.com")
    resp = client.post(
        "/api/v1/users",
        json={
            "name": "New Vet",
            "email": "newvet@example.com",
            "role": "veterinarian",
            "password": "SecurePass123",
        },
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json()["role"] == "veterinarian"


def test_admin_can_deactivate_user(client, admin_user, farmer_user):
    headers = auth_header(client, "admin@example.com")
    resp = client.patch(
        f"/api/v1/users/{farmer_user.id}",
        json={"is_active": False},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "farmer@example.com", "password": "testpass123"},
    )
    assert login_resp.status_code == 401


def test_duplicate_email_conflicts(client, admin_user, farmer_user):
    headers = auth_header(client, "admin@example.com")
    resp = client.post(
        "/api/v1/users",
        json={
            "name": "Duplicate",
            "email": "farmer@example.com",
            "role": "farmer",
            "password": "SecurePass123",
        },
        headers=headers,
    )
    assert resp.status_code == 409


def test_admin_can_view_audit_logs(client, admin_user, farmer_user):
    headers = auth_header(client, "admin@example.com")
    client.post(
        "/api/v1/farms",
        json={"name": "Audit Test Farm"},
        headers=auth_header(client, "farmer@example.com"),
    )
    resp = client.get("/api/v1/audit-logs", headers=headers)
    assert resp.status_code == 200
    assert any(log["entity_type"] == "farm" for log in resp.json())


def test_non_admin_cannot_view_audit_logs(client, farmer_user):
    headers = auth_header(client, "farmer@example.com")
    resp = client.get("/api/v1/audit-logs", headers=headers)
    assert resp.status_code == 403


def test_audit_logs_filter_by_entity_type(client, admin_user, farmer_user):
    auth_header(client, "farmer@example.com")
    headers = auth_header(client, "admin@example.com")
    resp = client.get("/api/v1/audit-logs?entity_type=user", headers=headers)
    assert resp.status_code == 200
    assert all(log["entity_type"] == "user" for log in resp.json())
