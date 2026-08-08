"""File storage abstraction — local disk (dev) or S3-compatible object storage (prod).

Set STORAGE_BACKEND=s3 with S3_* credentials to use any S3-compatible provider
(AWS S3, Cloudflare R2, Backblaze B2, MinIO, ...) instead of local disk. This
matters on hosts like Render's free tier, whose local filesystem is wiped on
every redeploy/restart — object storage is what keeps uploaded images and
generated PDF reports around.

Both backends are addressed by the same flat "key" string (e.g.
"uploads/<uuid>.jpg"), so callers never need to know which backend is active.
"""
from __future__ import annotations

from functools import lru_cache

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class StorageError(RuntimeError):
    """Raised when a storage backend cannot save, read, or locate an object."""


class LocalStorage:
    """Stores objects as files under the local BASE_DIR (uploads/reports)."""

    def __init__(self) -> None:
        settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        settings.REPORT_DIR.mkdir(parents=True, exist_ok=True)

    def _resolve(self, key: str):
        # Keys look like "uploads/<name>" or "reports/<name>" — map the first
        # segment to the matching local directory.
        prefix, _, filename = key.partition("/")
        if prefix == settings.S3_UPLOAD_PREFIX:
            return settings.UPLOAD_DIR / filename
        if prefix == settings.S3_REPORT_PREFIX:
            return settings.REPORT_DIR / filename
        raise StorageError(f"Unrecognized storage key: {key!r}")

    def save(self, key: str, data: bytes) -> str:
        path = self._resolve(key)
        path.write_bytes(data)
        logger.info("Saved %d bytes to local storage: %s", len(data), path)
        return key

    def read(self, key: str) -> bytes:
        path = self._resolve(key)
        if not path.exists():
            raise StorageError(f"Object not found: {key!r}")
        return path.read_bytes()

    def exists(self, key: str) -> bool:
        return self._resolve(key).exists()

    def local_path(self, key: str):
        """Return the local filesystem path for a key (local backend only)."""
        return self._resolve(key)

    def public_url(self, key: str) -> str | None:
        # Served by FastAPI's own StaticFiles mount in local dev — no separate URL scheme.
        return None


class S3Storage:
    """Stores objects in an S3-compatible bucket (AWS S3, Cloudflare R2, MinIO, ...)."""

    def __init__(self) -> None:
        import boto3  # imported lazily so local-only deployments don't need it installed

        if not settings.S3_BUCKET_NAME:
            raise StorageError("STORAGE_BACKEND=s3 requires S3_BUCKET_NAME to be set.")

        self._bucket = settings.S3_BUCKET_NAME
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL or None,
            region_name=settings.S3_REGION,
            aws_access_key_id=settings.S3_ACCESS_KEY_ID or None,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY or None,
        )

    def save(self, key: str, data: bytes) -> str:
        content_type = "application/pdf" if key.endswith(".pdf") else "application/octet-stream"
        if key.endswith((".jpg", ".jpeg")):
            content_type = "image/jpeg"
        elif key.endswith(".png"):
            content_type = "image/png"
        elif key.endswith(".webp"):
            content_type = "image/webp"

        try:
            self._client.put_object(Bucket=self._bucket, Key=key, Body=data, ContentType=content_type)
        except Exception as exc:  # noqa: BLE001
            raise StorageError(f"Failed to upload {key!r} to S3 bucket {self._bucket!r}: {exc}") from exc

        logger.info("Saved %d bytes to s3://%s/%s", len(data), self._bucket, key)
        return key

    def read(self, key: str) -> bytes:
        try:
            response = self._client.get_object(Bucket=self._bucket, Key=key)
            return response["Body"].read()
        except self._client.exceptions.NoSuchKey as exc:
            raise StorageError(f"Object not found: {key!r}") from exc
        except Exception as exc:  # noqa: BLE001
            raise StorageError(f"Failed to read {key!r} from S3 bucket {self._bucket!r}: {exc}") from exc

    def exists(self, key: str) -> bool:
        from botocore.exceptions import ClientError

        try:
            self._client.head_object(Bucket=self._bucket, Key=key)
            return True
        except ClientError:
            return False

    def presigned_url(self, key: str, expiry_seconds: int | None = None) -> str:
        try:
            return self._client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self._bucket, "Key": key},
                ExpiresIn=expiry_seconds or settings.S3_PRESIGNED_URL_EXPIRY_SECONDS,
            )
        except Exception as exc:  # noqa: BLE001
            raise StorageError(f"Failed to presign URL for {key!r}: {exc}") from exc


@lru_cache
def get_storage() -> LocalStorage | S3Storage:
    """Return the configured storage backend (cached — one instance per process)."""
    backend = settings.STORAGE_BACKEND.lower().strip()
    if backend == "s3":
        logger.info("Using S3-compatible object storage (bucket=%s)", settings.S3_BUCKET_NAME)
        return S3Storage()
    if backend == "local":
        logger.info("Using local disk storage (%s)", settings.UPLOAD_DIR.parent)
        return LocalStorage()
    raise StorageError(f"Unknown STORAGE_BACKEND: {backend!r} (expected 'local' or 's3')")
