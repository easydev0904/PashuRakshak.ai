import io

from tests.conftest import auth_header


def _png_bytes() -> bytes:
    # Minimal valid 1x1 PNG.
    return bytes.fromhex(
        "89504e470d0a1a0a0000000d49484452000000010000000108020000009077"
        "3de40000000c4944415408d763f8cfc0c00000030101006edd2f8f0000000049454e44ae426082"
    )


def test_upload_valid_image(client, farmer_user):
    headers = auth_header(client, "farmer@example.com")
    resp = client.post(
        "/api/v1/uploads",
        files={"file": ("photo.png", io.BytesIO(_png_bytes()), "image/png")},
        headers=headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["url"].startswith("/uploads/")
    assert body["url"].endswith(".png")


def test_upload_rejects_disallowed_content_type(client, farmer_user):
    headers = auth_header(client, "farmer@example.com")
    resp = client.post(
        "/api/v1/uploads",
        files={"file": ("script.js", io.BytesIO(b"alert(1)"), "application/javascript")},
        headers=headers,
    )
    assert resp.status_code == 422


def test_upload_rejects_oversized_file(client, farmer_user):
    headers = auth_header(client, "farmer@example.com")
    big_content = b"\x00" * (6 * 1024 * 1024)
    resp = client.post(
        "/api/v1/uploads",
        files={"file": ("big.png", io.BytesIO(big_content), "image/png")},
        headers=headers,
    )
    assert resp.status_code == 422


def test_upload_rejects_empty_file(client, farmer_user):
    headers = auth_header(client, "farmer@example.com")
    resp = client.post(
        "/api/v1/uploads",
        files={"file": ("empty.png", io.BytesIO(b""), "image/png")},
        headers=headers,
    )
    assert resp.status_code == 422


def test_upload_requires_auth(client):
    resp = client.post(
        "/api/v1/uploads",
        files={"file": ("photo.png", io.BytesIO(_png_bytes()), "image/png")},
    )
    assert resp.status_code == 401


def test_upload_filename_never_uses_client_supplied_name(client, farmer_user):
    headers = auth_header(client, "farmer@example.com")
    resp = client.post(
        "/api/v1/uploads",
        files={"file": ("../../etc/passwd.png", io.BytesIO(_png_bytes()), "image/png")},
        headers=headers,
    )
    assert resp.status_code == 201
    assert "etc" not in resp.json()["url"]
    assert ".." not in resp.json()["url"]
