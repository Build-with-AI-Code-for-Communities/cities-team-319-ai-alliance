"""Coral analysis endpoint — orchestrates Gemini, weather, and the risk engine.

This is the core pipeline: it takes a previously uploaded image, runs it
through Gemini Vision for classification, enriches it with weather/SST data,
computes a simple coral risk score, and persists the result as a Survey row.
"""
from __future__ import annotations

import datetime as dt
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.survey import Survey
from app.services.gemini_service import analyze_coral_image
from app.services.nasa_service import fetch_nasa_sst
from app.services.noaa_service import fetch_coral_reef_watch
from app.services.storage_service import StorageError, get_storage
from app.services.weather_service import fetch_weather
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/analyze", tags=["Analyze"])

_CLASSIFICATION_BASE_SCORE = {
    "Healthy": 0,
    "Partially Bleached": 40,
    "Severely Bleached": 75,
    "Dead Coral": 100,
    "Unknown": 20,
}


class AnalyzeRequest(BaseModel):
    """Request body for triggering analysis on a previously uploaded image."""

    image_name: str
    latitude: float | None = None
    longitude: float | None = None
    submitted_by: str | None = None


class SurveyResponse(BaseModel):
    """Full survey result returned after analysis."""

    id: int
    image_name: str
    submitted_by: str | None
    latitude: float | None
    longitude: float | None
    classification: str
    severity: str
    confidence: float
    possible_cause: str | None
    recommendation: str | None
    risk_level: str | None
    risk_score: float | None
    temperature: float | None
    weather: dict[str, Any] | None
    created_at: dt.datetime

    model_config = {"from_attributes": True}


def _compute_risk(
    classification: str,
    temperature: float | None,
    bleaching_alert_level: int | None = None,
) -> tuple[str, float]:
    """Combine classification, temperature, and NOAA heat-stress data into a risk score/level.

    This is intentionally simple (per the hackathon spec): a base score from
    the classification, boosted if sea temperature crosses warning/critical
    thresholds, and boosted further by NOAA Coral Reef Watch's Bleaching
    Alert Level (0-5, derived from satellite Degree Heating Weeks using the
    same thresholds documented in the team's reef survey methodology paper —
    Alert Level 1 at DHW >= 4 up to Alert Level 5 at DHW >= 20).
    """
    score = float(_CLASSIFICATION_BASE_SCORE.get(classification, 20))

    if temperature is not None:
        if temperature >= settings.RISK_TEMP_CRITICAL_C:
            score += 20
        elif temperature >= settings.RISK_TEMP_WARNING_C:
            score += 10

    if bleaching_alert_level is not None:
        if bleaching_alert_level >= 4:
            score += 30
        elif bleaching_alert_level >= 2:
            score += 20
        elif bleaching_alert_level >= 1:
            score += 10

    score = max(0.0, min(100.0, score))

    if score < 25:
        level = "Low"
    elif score < 50:
        level = "Moderate"
    elif score < 75:
        level = "High"
    else:
        level = "Critical"

    return level, score


@router.post(
    "",
    response_model=SurveyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Run the full coral analysis pipeline on an uploaded image",
    description=(
        "Runs Gemini Vision classification, fetches weather/SST data for the "
        "given coordinates, computes a coral risk score, and stores the result."
    ),
)
async def analyze_image(payload: AnalyzeRequest, db: Session = Depends(get_db)) -> SurveyResponse:
    try:
        image_bytes = get_storage().read(payload.image_name)
    except StorageError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image '{payload.image_name}' not found. Upload it via /api/upload first.",
        ) from exc

    classification_result = await analyze_coral_image(image_bytes, payload.image_name)
    weather = await fetch_weather(payload.latitude, payload.longitude)

    if settings.NASA_SST_ENABLED and payload.latitude is not None and payload.longitude is not None:
        today = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
        nasa_result = await fetch_nasa_sst(payload.latitude, payload.longitude, today)
        if nasa_result.get("sst_c") is not None:
            weather["sea_surface_temperature_c"] = nasa_result["sst_c"]
            weather["source"] = "open-meteo+nasa"

    crw = await fetch_coral_reef_watch(payload.latitude, payload.longitude)
    weather["coral_reef_watch"] = crw

    temperature = (
        crw.get("sst_c")
        or weather.get("sea_surface_temperature_c")
        or weather.get("temperature_c")
    )
    risk_level, risk_score = _compute_risk(
        classification_result["classification"],
        temperature,
        crw.get("bleaching_alert_level"),
    )

    survey = Survey(
        image_name=payload.image_name,
        submitted_by=(payload.submitted_by or "").strip() or None,
        latitude=payload.latitude,
        longitude=payload.longitude,
        classification=classification_result["classification"],
        severity=classification_result["severity"],
        confidence=classification_result["confidence"],
        possible_cause=classification_result["possible_cause"],
        recommendation=classification_result["recommendation"],
        risk_level=risk_level,
        risk_score=risk_score,
        temperature=temperature,
        weather=weather,
    )

    db.add(survey)
    db.commit()
    db.refresh(survey)

    logger.info("Survey #%s created — classification=%s risk=%s", survey.id, survey.classification, risk_level)
    return SurveyResponse.model_validate(survey)
