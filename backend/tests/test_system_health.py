from tests.conftest import auth_header


def test_admin_can_view_system_health(client, admin_user, farmer_user):
    headers = auth_header(client, "admin@example.com")
    resp = client.get("/api/v1/analytics/system-health", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["total_users"] >= 2


def test_non_admin_cannot_view_system_health(client, farmer_user):
    headers = auth_header(client, "farmer@example.com")
    resp = client.get("/api/v1/analytics/system-health", headers=headers)
    assert resp.status_code == 403
