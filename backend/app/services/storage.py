"""File storage abstraction.

Only a local-disk backend is implemented for this prototype, but every
caller goes through this interface (never touches the filesystem
directly) so swapping in an S3-compatible backend later is a matter of
adding one class here, not touching upload_service or the routes.
"""

from abc import ABC, abstractmethod
from pathlib import Path

from app.core.config import get_settings

settings = get_settings()


class StorageBackend(ABC):
    @abstractmethod
    def save(self, content: bytes, filename: str) -> str:
        """Persist `content` under `filename` and return a URL/path clients can fetch it from."""

    @abstractmethod
    def exists(self, filename: str) -> bool: ...


class LocalStorageBackend(StorageBackend):
    def __init__(self, base_dir: str):
        self._base_dir = Path(base_dir)
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, content: bytes, filename: str) -> str:
        target = self._base_dir / filename
        target.write_bytes(content)
        return f"/uploads/{filename}"

    def exists(self, filename: str) -> bool:
        return (self._base_dir / filename).is_file()

    @property
    def base_dir(self) -> Path:
        return self._base_dir


def get_storage_backend() -> StorageBackend:
    # UPLOAD_STORAGE_BACKEND is a single "local" | "s3" switch; only
    # "local" is implemented today. Anything else would raise here
    # rather than silently falling back, since silently writing to
    # local disk when the operator configured S3 would be a surprising
    # (and, in production, likely wrong) failure mode.
    if settings.UPLOAD_STORAGE_BACKEND != "local":
        raise NotImplementedError(
            f"Storage backend '{settings.UPLOAD_STORAGE_BACKEND}' is not implemented."
        )
    return LocalStorageBackend(settings.UPLOAD_DIR)
