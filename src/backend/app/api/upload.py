"""Image upload endpoint — validation, resizing, and GPS extraction."""
from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.utils.image_processing import ImageValidationError, save_and_resize_image, validate_upload
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/upload", tags=["Upload"])


class UploadResponse(BaseModel):
    """Response returned after an image has been validated, resized, and stored."""

    image_name: str
    latitude: float | None
    longitude: float | None
    message: str


@router.post(
    "",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and preprocess a coral image",
    description=(
        "Validates the uploaded image (type/size), auto-orients and resizes it, "
        "extracts GPS coordinates from EXIF if present, and stores it on disk. "
        "Returns the stored image name to be passed to /api/analyze."
    ),
)
async def upload_image(file: UploadFile = File(...)) -> UploadResponse:
    raw_bytes = await file.read()

    try:
        validate_upload(file, raw_bytes)
        storage_key, latitude, longitude = save_and_resize_image(raw_bytes, file.filename or "upload.jpg")
    except ImageValidationError as exc:
        logger.warning("Upload rejected: %s", exc)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return UploadResponse(
        image_name=storage_key,
        latitude=latitude,
        longitude=longitude,
        message="Image uploaded and processed successfully.",
    )
