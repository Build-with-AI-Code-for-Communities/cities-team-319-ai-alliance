"""OBIS (Ocean Biodiversity Information System) integration — Tier 3 stub.

Not implemented for the hackathon build. Kept as a seam for cross-referencing
survey locations against known biodiversity records via the OBIS API
(https://api.obis.org). Always returns a clearly-flagged stub result.
"""
from __future__ import annotations

from typing import Any

from app.utils.logger import get_logger

logger = get_logger(__name__)


async def fetch_nearby_species(latitude: float, longitude: float) -> dict[str, Any]:
    """Stub for future OBIS biodiversity lookup.

    TODO(Tier 3): query https://api.obis.org/occurrence for coral species
    occurrence records near the survey coordinate to enrich reports with
    biodiversity context. Not required for MVP scoring.
    """
    logger.debug("obis_service is a Tier 3 stub — returning unimplemented status.")
    return {"species": [], "source": "not_implemented"}
