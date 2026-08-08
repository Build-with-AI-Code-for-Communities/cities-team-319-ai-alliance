"""NASA Ocean Color (chlorophyll-a / turbidity) integration — Tier 3 stub.

Not implemented for the hackathon build. Kept as a seam for a future
integration with NASA's Ocean Color Web (e.g. chlorophyll concentration as an
additional reef-stress signal). Always returns a clearly-flagged stub result.
"""
from __future__ import annotations

from typing import Any

from app.utils.logger import get_logger

logger = get_logger(__name__)


async def fetch_ocean_color(latitude: float, longitude: float) -> dict[str, Any]:
    """Stub for future NASA Ocean Color integration.

    TODO(Tier 3): integrate with https://oceancolor.gsfc.nasa.gov/ for
    chlorophyll-a concentration, which correlates with algal bloom stress
    on reefs. Not required for MVP scoring.
    """
    logger.debug("ocean_color_service is a Tier 3 stub — returning unimplemented status.")
    return {"chlorophyll_a": None, "source": "not_implemented"}
