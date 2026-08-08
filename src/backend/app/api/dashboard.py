"""Dashboard endpoints — list and retrieve past surveys for map/table views."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.analyze import SurveyResponse
from app.database import get_db
from app.models.survey import Survey
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


class DashboardStats(BaseModel):
    """Aggregate counts shown at the top of the dashboard."""

    total_surveys: int
    healthy: int
    partially_bleached: int
    severely_bleached: int
    dead_coral: int
    unknown: int


@router.get(
    "/surveys",
    response_model=list[SurveyResponse],
    summary="List past surveys, most recent first",
)
async def list_surveys(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> list[SurveyResponse]:
    surveys = (
        db.query(Survey)
        .order_by(Survey.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [SurveyResponse.model_validate(s) for s in surveys]


@router.get(
    "/surveys/{survey_id}",
    response_model=SurveyResponse,
    summary="Get a single survey by ID",
)
async def get_survey(survey_id: int, db: Session = Depends(get_db)) -> SurveyResponse:
    survey = db.get(Survey, survey_id)
    if survey is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Survey {survey_id} not found.")
    return SurveyResponse.model_validate(survey)


@router.get(
    "/stats",
    response_model=DashboardStats,
    summary="Get aggregate classification counts across all surveys",
)
async def get_stats(db: Session = Depends(get_db)) -> DashboardStats:
    rows = db.query(Survey.classification, func.count(Survey.id)).group_by(Survey.classification).all()
    counts = {classification: count for classification, count in rows}

    return DashboardStats(
        total_surveys=sum(counts.values()),
        healthy=counts.get("Healthy", 0),
        partially_bleached=counts.get("Partially Bleached", 0),
        severely_bleached=counts.get("Severely Bleached", 0),
        dead_coral=counts.get("Dead Coral", 0),
        unknown=counts.get("Unknown", 0),
    )
