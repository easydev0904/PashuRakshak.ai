from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import get_settings
from tests.conftest import auth_header


def test_login_success(client, farmer_user):
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "farmer@example.com", "password": "testpass123"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["user"]["role"] == "farmer"
    assert body["access_token"]
    assert body["refresh_token"]


def test_login_wrong_password(client, farmer_user):
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "farmer@example.com", "password": "wrongpassword"},
    )
    assert resp.status_code == 401
    assert "detail" in resp.json()


def test_login_unknown_user(client):
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "whatever123"},
    )
    assert resp.status_code == 401


def test_login_requires_identifier(client):
    resp = client.post("/api/v1/auth/login", json={"password": "whatever123"})
    assert resp.status_code == 422


def test_me_requires_token(client):
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401


def test_me_returns_current_user(client, farmer_user):
    headers = auth_header(client, "farmer@example.com")
    resp = client.get("/api/v1/auth/me", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "farmer@example.com"


def test_me_rejects_garbage_token(client):
    resp = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert resp.status_code == 401


def test_inactive_user_cannot_login(client, db, farmer_user):
    farmer_user.is_active = False
    db.add(farmer_user)
    db.commit()
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "farmer@example.com", "password": "testpass123"},
    )
    assert resp.status_code == 401


def test_refresh_token_issues_new_access_token(client, farmer_user):
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "farmer@example.com", "password": "testpass123"},
    )
    refresh_token = login_resp.json()["refresh_token"]
    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    assert resp.json()["access_token"]


def _make_token(*, user_id: str, role: str, token_type: str, expires_delta: timedelta) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "role": role,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def test_expired_access_token_rejected(client, farmer_user):
    expired = _make_token(
        user_id=farmer_user.id,
        role="farmer",
        token_type="access",
        expires_delta=timedelta(minutes=-5),
    )
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired}"})
    assert resp.status_code == 401


def test_refresh_token_cannot_be_used_as_access_token(client, farmer_user):
    """A refresh token should not itself grant API access -- only /auth/refresh accepts it."""
    refresh_token = _make_token(
        user_id=farmer_user.id,
        role="farmer",
        token_type="refresh",
        expires_delta=timedelta(days=7),
    )
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {refresh_token}"})
    assert resp.status_code == 401


def test_expired_refresh_token_rejected(client, farmer_user):
    expired_refresh = _make_token(
        user_id=farmer_user.id,
        role="farmer",
        token_type="refresh",
        expires_delta=timedelta(minutes=-5),
    )
    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": expired_refresh})
    assert resp.status_code == 401
