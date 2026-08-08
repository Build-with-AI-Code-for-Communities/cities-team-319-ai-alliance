"""PDF report generation and download endpoints."""
from __future__ import annotations

import datetime as dt

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.report import Report
from app.models.survey import Survey
from app.services.report_service import generate_survey_report
from app.services.storage_service import S3Storage, get_storage
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/report", tags=["Report"])


class ReportResponse(BaseModel):
    """Metadata for a generated PDF report."""

    id: int
    survey_id: int
    pdf_path: str
    created_at: dt.datetime

    model_config = {"from_attributes": True}


def _get_survey_or_404(survey_id: int, db: Session) -> Survey:
    survey = db.get(Survey, survey_id)
    if survey is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Survey {survey_id} not found.")
    return survey


@router.post(
    "/{survey_id}",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a one-page PDF report for a survey",
)
async def create_report(survey_id: int, db: Session = Depends(get_db)) -> ReportResponse:
    survey = _get_survey_or_404(survey_id, db)

    pdf_path = generate_survey_report(survey)

    report = Report(survey_id=survey.id, pdf_path=str(pdf_path))
    db.add(report)
    db.commit()
    db.refresh(report)

    return ReportResponse.model_validate(report)


@router.get(
    "/{survey_id}/download",
    summary="Download the most recent PDF report for a survey",
    description=(
        "Serves the PDF directly when using local storage, or 307-redirects to a "
        "short-lived presigned URL when using S3-compatible object storage."
    ),
)
async def download_report(survey_id: int, db: Session = Depends(get_db)):
    survey = _get_survey_or_404(survey_id, db)

    report = (
        db.query(Report)
        .filter(Report.survey_id == survey.id)
        .order_by(Report.created_at.desc())
        .first()
    )
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No report generated yet for survey {survey_id}. POST /api/report/{survey_id} first.",
        )

    storage = get_storage()
    if isinstance(storage, S3Storage):
        return RedirectResponse(url=storage.presigned_url(report.pdf_path))

    return FileResponse(
        path=storage.local_path(report.pdf_path),
        media_type="application/pdf",
        filename=f"coral_survey_{survey_id}_report.pdf",
    )
