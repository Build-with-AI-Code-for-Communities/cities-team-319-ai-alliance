"""NOAA Coral Reef Watch integration (Tier 2 — optional, graceful fallback).

Uses NOAA's public ERDDAP server to fetch satellite-derived heat-stress
products (SST, HotSpot, Degree Heating Weeks) for the 5km grid cell nearest
a coordinate, then derives a Bleaching Alert Level (Watch / Warning /
Alert Level 1-5) using the Degree Heating Week thresholds NOAA CRW adopted
after the Fourth Global Coral Bleaching Event (2023-2025) — see
docs/reef-survey-methodology.md and the team's field methodology paper for
the source table. No API key required. If the coordinate is missing, the
lookup fails, or the cell has no data (e.g. it's on land), callers receive
a clearly-flagged fallback rather than an exception.
"""
from __future__ import annotations

from typing import Any

import httpx

from app.utils.logger import get_logger

logger = get_logger(__name__)

_ERDDAP_URL = "https://coastwatch.pfeg.noaa.gov/erddap/griddap/NOAA_DHW.json"

# (min_dhw, level, label) — checked from highest to lowest. Matches NOAA CRW's
# post-2023 seven-level scale: Watch/Warning precede numbered Alert Levels,
# which now extend to 5 (previously capped at 2) to capture the unprecedented
# heat stress of the Fourth Global Coral Bleaching Event.
_DHW_THRESHOLDS = [
    (20.0, 5, "Alert Level 5"),
    (16.0, 4, "Alert Level 4"),
    (12.0, 3, "Alert Level 3"),
    (8.0, 2, "Alert Level 2"),
    (4.0, 1, "Alert Level 1"),
]

_FALLBACK: dict[str, Any] = {
    "sst_c": None,
    "hotspot_c": None,
    "degree_heating_weeks": None,
    "bleaching_alert_level": None,
    "bleaching_alert_label": None,
    "source": "noaa_unavailable",
}


def _derive_alert(hotspot_c: float | None, dhw: float | None) -> tuple[int, str]:
    """Map HotSpot/DHW to NOAA CRW's Watch -> Warning -> Alert Level 1-5 scale."""
    if dhw is not None:
        for min_dhw, level, label in _DHW_THRESHOLDS:
            if dhw >= min_dhw:
                return level, label

    if hotspot_c is not None and hotspot_c > 1.0:
        return 0, "Warning"
    if hotspot_c is not None and hotspot_c > 0.0:
        return 0, "Watch"
    return 0, "No Stress"


async def fetch_coral_reef_watch(latitude: float, longitude: float) -> dict[str, Any]:
    """Fetch NOAA Coral Reef Watch heat-stress data for the nearest reef grid cell.

    Args:
        latitude, longitude: survey location.

    Returns:
        A dict with sst_c, hotspot_c, degree_heating_weeks, bleaching_alert_level
        (0-5), bleaching_alert_label (Watch/Warning/Alert Level 1-5), and source.
        Never raises.
    """
    if latitude is None or longitude is None:
        return dict(_FALLBACK)

    query = (
        f"CRW_SST[(last)][({latitude})][({longitude})],"
        f"CRW_HOTSPOT[(last)][({latitude})][({longitude})],"
        f"CRW_DHW[(last)][({latitude})][({longitude})]"
    )
    url = f"{_ERDDAP_URL}?{query}"

    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            payload = resp.json()

        row = payload["table"]["rows"][0]
        columns = payload["table"]["columnNames"]
        values = dict(zip(columns, row))

        hotspot = values.get("CRW_HOTSPOT")
        dhw = values.get("CRW_DHW")

        if dhw is None and hotspot is None:
            return dict(_FALLBACK)

        level, label = _derive_alert(hotspot, dhw)

        return {
            "sst_c": values.get("CRW_SST"),
            "hotspot_c": hotspot,
            "degree_heating_weeks": dhw,
            "bleaching_alert_level": level,
            "bleaching_alert_label": label,
            "source": "noaa_coral_reef_watch",
        }

    except Exception as exc:  # noqa: BLE001 — Tier 2 must degrade gracefully
        logger.info("NOAA Coral Reef Watch lookup failed, falling back gracefully: %s", exc)
        return dict(_FALLBACK)
