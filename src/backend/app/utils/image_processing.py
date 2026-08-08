"""Image validation and resizing utilities backed by Pillow.

All processing happens in-memory (BytesIO) so the result can be handed to
either storage backend (local disk or S3-compatible object storage) without
this module needing to know which one is active.
"""
from __future__ import annotations

import io
import uuid
from pathlib import Path

from fastapi import UploadFile
from PIL import Image, ImageOps

from app.config import settings
from app.services.storage_service import get_storage
from app.utils.gps import extract_gps
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ImageValidationError(ValueError):
    """Raised when an uploaded file fails validation checks."""


def validate_upload(file: UploadFile, raw_bytes: bytes) -> None:
    """Validate content type and size of an uploaded image.

    Raises:
        ImageValidationError: if the file type is unsupported or too large.
    """
    if file.content_type not in settings.allowed_image_types_list:
        raise ImageValidationError(
            f"Unsupported file type '{file.content_type}'. "
            f"Allowed types: {', '.join(settings.allowed_image_types_list)}"
        )

    size_mb = len(raw_bytes) / (1024 * 1024)
    if size_mb > settings.MAX_UPLOAD_SIZE_MB:
        raise ImageValidationError(
            f"File too large ({size_mb:.1f} MB). Max allowed is {settings.MAX_UPLOAD_SIZE_MB} MB."
        )

    if len(raw_bytes) == 0:
        raise ImageValidationError("Uploaded file is empty.")


def save_and_resize_image(raw_bytes: bytes, original_filename: str) -> tuple[str, float | None, float | None]:
    """Auto-orient, downscale, and persist an uploaded image via the configured storage backend.

    GPS coordinates are extracted from EXIF *before* resizing, since re-saving
    with Pillow strips EXIF metadata. Processing happens entirely in memory.

    Returns:
        A tuple of (storage_key, latitude, longitude). storage_key is the
        identifier to pass to /api/analyze and to storage_service.read().
    """
    latitude, longitude = extract_gps(raw_bytes)

    suffix = Path(original_filename).suffix.lower() or ".jpg"
    unique_name = f"{uuid.uuid4().hex}{suffix}"
    storage_key = f"{settings.S3_UPLOAD_PREFIX}/{unique_name}"

    try:
        with Image.open(io.BytesIO(raw_bytes)) as img:
            img = ImageOps.exif_transpose(img)  # normalize rotation per EXIF orientation
            img.thumbnail(
                (settings.IMAGE_MAX_DIMENSION, settings.IMAGE_MAX_DIMENSION),
                Image.LANCZOS,
            )
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            save_format = {".png": "PNG", ".webp": "WEBP"}.get(suffix, "JPEG")
            buffer = io.BytesIO()
            img.save(buffer, format=save_format, quality=88, optimize=True)
            processed_bytes = buffer.getvalue()
    except Exception as exc:
        logger.error("Failed to process image %s: %s", original_filename, exc)
        raise ImageValidationError(f"Could not process image: {exc}") from exc

    get_storage().save(storage_key, processed_bytes)
    logger.info("Saved and resized image: %s (%d bytes)", storage_key, len(processed_bytes))

    return storage_key, latitude, longitude
