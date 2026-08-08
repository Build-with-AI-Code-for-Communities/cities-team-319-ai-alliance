"""NOAA Coral Reef Watch integration (Tier 2 — optional, graceful fallback).

Uses NOAA's public ERDDAP server to fetch satellite-derived heat-stress
products (SST, HotSpot, Degree Heating Weeks, Bleaching Alert Area) for the
5km grid cell nearest a coordinate. No API key required. If the coordinate
is missing, the lookup fails, or the cell has no data (e.g. it's on land),
callers receive a clearly-flagged fallback rather than an exception.
"""
from __future__ import annotations

from typing import Any

import httpx

from app.utils.logger import get_logger

logger = get_logger(__name__)

_ERDDAP_URL = "https://coastwatch.pfeg.noaa.gov/erddap/griddap/NOAA_DHW.json"

_BAA_LABELS = {
    0: "No Stress",
    1: "Watch",
    2: "Warning",
    3: "Alert Level 1",
    4: "Alert Level 2",
}

_FALLBACK: dict[str, Any] = {
    "sst_c": None,
    "hotspot_c": None,
    "degree_heating_weeks": None,
    "bleaching_alert_level": None,
    "bleaching_alert_label": None,
    "source": "noaa_unavailable",
}


async def fetch_coral_reef_watch(latitude: float, longitude: float) -> dict[str, Any]:
    """Fetch NOAA Coral Reef Watch heat-stress data for the nearest reef grid cell.

    Args:
        latitude, longitude: survey location.

    Returns:
        A dict with sst_c, hotspot_c, degree_heating_weeks, bleaching_alert_level
        (0-4), bleaching_alert_label, and source. Never raises.
    """
    if latitude is None or longitude is None:
        return dict(_FALLBACK)

    query = (
        f"CRW_SST[(last)][({latitude})][({longitude})],"
        f"CRW_HOTSPOT[(last)][({latitude})][({longitude})],"
        f"CRW_DHW[(last)][({latitude})][({longitude})],"
        f"CRW_BAA[(last)][({latitude})][({longitude})]"
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

        dhw = values.get("CRW_DHW")
        baa = values.get("CRW_BAA")
        baa_int = int(baa) if baa is not None else None

        return {
            "sst_c": values.get("CRW_SST"),
            "hotspot_c": values.get("CRW_HOTSPOT"),
            "degree_heating_weeks": dhw,
            "bleaching_alert_level": baa_int,
            "bleaching_alert_label": _BAA_LABELS.get(baa_int) if baa_int is not None else None,
            "source": "noaa_coral_reef_watch",
        }

    except Exception as exc:  # noqa: BLE001 — Tier 2 must degrade gracefully
        logger.info("NOAA Coral Reef Watch lookup failed, falling back gracefully: %s", exc)
        return dict(_FALLBACK)
