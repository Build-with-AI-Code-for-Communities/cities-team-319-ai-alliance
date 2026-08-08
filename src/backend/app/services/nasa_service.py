"""NASA Sea Surface Temperature integration (Tier 2 — optional, graceful fallback).

Uses NASA's POWER API (https://power.larc.nasa.gov) for satellite-derived skin
temperature as a proxy for SST. Requires NASA_SST_ENABLED=true and, depending
on deployment, a NASA_API_KEY. If disabled or unreachable, callers receive a
clearly-flagged fallback rather than an exception.
"""
from __future__ import annotations

from typing import Any

import httpx

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

_POWER_API_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"

_FALLBACK: dict[str, Any] = {
    "sst_c": None,
    "source": "nasa_unavailable",
    "note": "NASA SST disabled or unreachable — using Open-Meteo marine data only.",
}


async def fetch_nasa_sst(latitude: float, longitude: float, date: str) -> dict[str, Any]:
    """Fetch satellite skin temperature for a coordinate/date. Best-effort, Tier 2.

    Args:
        latitude, longitude: survey location.
        date: ISO date string (YYYY-MM-DD) to query.

    Returns:
        A dict with 'sst_c' (float | None) and 'source'. Never raises.
    """
    if not settings.NASA_SST_ENABLED:
        logger.debug("NASA SST integration disabled via config — skipping.")
        return dict(_FALLBACK)

    if latitude is None or longitude is None:
        return dict(_FALLBACK)

    try:
        yyyymmdd = date.replace("-", "")
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                _POWER_API_URL,
                params={
                    "parameters": "T2M",
                    "community": "RE",
                    "longitude": longitude,
                    "latitude": latitude,
                    "start": yyyymmdd,
                    "end": yyyymmdd,
                    "format": "JSON",
                },
            )
            resp.raise_for_status()
            payload = resp.json()
            series = payload["properties"]["parameter"]["T2M"]
            value = next(iter(series.values()), None)

            if value is None or value == -999:
                return dict(_FALLBACK)

            return {"sst_c": float(value), "source": "nasa_power", "note": None}

    except Exception as exc:  # noqa: BLE001 — Tier 2 must degrade gracefully
        logger.info("NASA SST lookup failed, falling back gracefully: %s", exc)
        return dict(_FALLBACK)
