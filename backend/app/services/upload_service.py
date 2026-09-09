"""Validates and stores user-uploaded image files.

Security properties this module guarantees:
  - Only whitelisted image MIME types are accepted.
  - Size is enforced while reading (never buffers an unbounded body).
  - The stored filename is always server-generated (uuid4 + a fixed
    extension derived from the *validated* content type) -- the
    client-supplied filename is never used to build a filesystem path,
    which rules out path traversal and extension-spoofing tricks.
"""

from uuid import uuid4

from fastapi import UploadFile

from app.core.config import get_settings
from app.core.errors import ValidationAppError
from app.services.storage import get_storage_backend

settings = get_settings()

ALLOWED_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


async def save_image_upload(file: UploadFile) -> str:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise ValidationAppError("Only JPEG, PNG, or WEBP images are supported.")

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await file.read(1024 * 1024)
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise ValidationAppError(f"Images must be {settings.MAX_UPLOAD_SIZE_MB}MB or smaller.")
        chunks.append(chunk)

    if total == 0:
        raise ValidationAppError("The uploaded file is empty.")

    extension = ALLOWED_CONTENT_TYPES[file.content_type]
    filename = f"{uuid4().hex}{extension}"

    backend = get_storage_backend()
    return backend.save(b"".join(chunks), filename)
