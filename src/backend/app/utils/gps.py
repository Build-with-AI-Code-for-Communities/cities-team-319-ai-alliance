"""GPS coordinate extraction from image EXIF metadata."""
from __future__ import annotations

import io

from PIL import Image
from PIL.ExifTags import GPSTAGS, TAGS

from app.utils.logger import get_logger

logger = get_logger(__name__)


def _dms_to_decimal(dms: tuple, ref: str) -> float:
    """Convert EXIF degrees/minutes/seconds tuple to decimal degrees."""
    degrees, minutes, seconds = (float(v) for v in dms)
    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
    if ref in ("S", "W"):
        decimal = -decimal
    return decimal


def extract_gps(image_bytes: bytes) -> tuple[float | None, float | None]:
    """Extract (latitude, longitude) from an image's EXIF GPS tags.

    Returns (None, None) if no GPS metadata is present or the image has no EXIF data.
    """
    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            exif_raw = img.getexif()
            if not exif_raw:
                return None, None

            exif = {TAGS.get(tag_id, tag_id): value for tag_id, value in exif_raw.items()}
            gps_info = exif.get("GPSInfo")
            if not gps_info:
                return None, None

            gps_data = {GPSTAGS.get(tag_id, tag_id): value for tag_id, value in gps_info.items()}

            lat = gps_data.get("GPSLatitude")
            lat_ref = gps_data.get("GPSLatitudeRef")
            lon = gps_data.get("GPSLongitude")
            lon_ref = gps_data.get("GPSLongitudeRef")

            if not (lat and lat_ref and lon and lon_ref):
                return None, None

            latitude = _dms_to_decimal(lat, lat_ref)
            longitude = _dms_to_decimal(lon, lon_ref)
            return latitude, longitude

    except Exception as exc:  # noqa: BLE001 — GPS extraction must never break the upload flow
        logger.warning("Failed to extract GPS data from image: %s", exc)
        return None, None
