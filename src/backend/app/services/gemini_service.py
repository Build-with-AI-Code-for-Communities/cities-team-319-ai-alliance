"""Gemini Vision integration for coral health classification.

Tier 1 (required) service. Sends the uploaded coral image to Gemini with a
strict prompt that forces a pure-JSON response, then parses and validates it.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import google.generativeai as genai

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Exact prompt as specified by the CoralAI spec — do not reformat or alter.
GEMINI_PROMPT = """You are an expert marine biologist specializing in coral reef health.
Analyze the uploaded underwater coral image.
Respond ONLY in valid JSON.
{
"classification": "",
"severity": "",
"confidence": 0,
"possible_cause": "",
"recommendation": ""
}
Classification must be one of:
Healthy
Partially Bleached
Severely Bleached
Dead Coral
Unknown
Estimate confidence from 0-100.
Do not include markdown."""

VALID_CLASSIFICATIONS = {
    "Healthy",
    "Partially Bleached",
    "Severely Bleached",
    "Dead Coral",
    "Unknown",
}

_FALLBACK_RESULT: dict[str, Any] = {
    "classification": "Unknown",
    "severity": "Unknown",
    "confidence": 0,
    "possible_cause": "Analysis unavailable.",
    "recommendation": "Please retry the upload or consult a marine biologist.",
}


class GeminiServiceError(RuntimeError):
    """Raised when the Gemini API cannot be reached or returns an unusable response."""


def _get_mime_type(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    return {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }.get(suffix, "image/jpeg")


def _extract_json(raw_text: str) -> dict[str, Any]:
    """Strip markdown fences (if any) and parse the model's JSON response."""
    cleaned = raw_text.strip()
    cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()

    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        raise GeminiServiceError(f"No JSON object found in Gemini response: {raw_text!r}")

    return json.loads(match.group(0))


def _validate_result(data: dict[str, Any]) -> dict[str, Any]:
    """Coerce and validate the parsed Gemini JSON into the expected shape."""
    classification = str(data.get("classification", "Unknown")).strip()
    if classification not in VALID_CLASSIFICATIONS:
        logger.warning("Gemini returned unexpected classification %r, coercing to Unknown", classification)
        classification = "Unknown"

    try:
        confidence = float(data.get("confidence", 0))
    except (TypeError, ValueError):
        confidence = 0.0
    confidence = max(0.0, min(100.0, confidence))

    return {
        "classification": classification,
        "severity": str(data.get("severity", "Unknown")).strip() or "Unknown",
        "confidence": confidence,
        "possible_cause": str(data.get("possible_cause", "")).strip(),
        "recommendation": str(data.get("recommendation", "")).strip(),
    }


async def analyze_coral_image(image_bytes: bytes, filename: str) -> dict[str, Any]:
    """Classify coral health in an image using Gemini Vision.

    Falls back to a safe 'Unknown' result (rather than raising) if the API key
    is missing or the model call fails, so the rest of the pipeline can proceed.
    """
    if not settings.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not configured — returning fallback classification.")
        return dict(_FALLBACK_RESULT)

    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(settings.GEMINI_MODEL)

        image_part = {"mime_type": _get_mime_type(filename), "data": image_bytes}

        response = await model.generate_content_async([GEMINI_PROMPT, image_part])
        raw_text = response.text

        parsed = _extract_json(raw_text)
        result = _validate_result(parsed)
        logger.info("Gemini classification: %s (confidence=%.0f)", result["classification"], result["confidence"])
        return result

    except Exception as exc:  # noqa: BLE001 — never let a Gemini failure crash the upload flow
        logger.error("Gemini analysis failed: %s", exc)
        return dict(_FALLBACK_RESULT)
