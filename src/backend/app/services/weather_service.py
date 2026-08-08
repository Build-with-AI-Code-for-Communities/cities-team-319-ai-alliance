"""Open-Meteo weather integration (Tier 1 — no API key required)."""
from __future__ import annotations

from typing import Any

import httpx

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

_FALLBACK_WEATHER: dict[str, Any] = {
    "temperature_c": None,
    "wind_speed_kmh": None,
    "weather_code": None,
    "sea_surface_temperature_c": None,
    "source": "unavailable",
}


async def fetch_weather(latitude: float, longitude: float) -> dict[str, Any]:
    """Fetch current air temperature/wind for a coordinate, plus sea surface temp if available.

    Uses Open-Meteo's free forecast + marine APIs. Returns a fallback dict
    (all None values) if the coordinate is missing or the API call fails —
    this must never block the rest of the analysis pipeline.
    """
    if latitude is None or longitude is None:
        logger.info("No GPS coordinates supplied — skipping weather lookup.")
        return dict(_FALLBACK_WEATHER)

    result = dict(_FALLBACK_WEATHER)
    result["source"] = "open-meteo"

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            forecast_resp = await client.get(
                settings.OPEN_METEO_BASE_URL,
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "current": "temperature_2m,wind_speed_10m,weather_code",
                },
            )
            forecast_resp.raise_for_status()
            current = forecast_resp.json().get("current", {})
            result["temperature_c"] = current.get("temperature_2m")
            result["wind_speed_kmh"] = current.get("wind_speed_10m")
            result["weather_code"] = current.get("weather_code")
        except Exception as exc:  # noqa: BLE001
            logger.warning("Open-Meteo forecast lookup failed: %s", exc)

        try:
            marine_resp = await client.get(
                settings.OPEN_METEO_MARINE_URL,
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "hourly": "sea_surface_temperature",
                    "forecast_days": 1,
                },
            )
            marine_resp.raise_for_status()
            hourly = marine_resp.json().get("hourly", {})
            sst_series = hourly.get("sea_surface_temperature") or []
            if sst_series:
                result["sea_surface_temperature_c"] = sst_series[0]
        except Exception as exc:  # noqa: BLE001
            logger.info("Open-Meteo marine (SST) lookup unavailable: %s", exc)

    return result
