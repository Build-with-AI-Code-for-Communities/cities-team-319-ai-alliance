"""One-page PDF report generation using ReportLab."""
from __future__ import annotations

import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.config import settings
from app.models.survey import Survey
from app.services.storage_service import get_storage
from app.utils.logger import get_logger

logger = get_logger(__name__)

_SEVERITY_COLORS = {
    "Healthy": colors.HexColor("#16a34a"),
    "Partially Bleached": colors.HexColor("#eab308"),
    "Severely Bleached": colors.HexColor("#f97316"),
    "Dead Coral": colors.HexColor("#dc2626"),
    "Unknown": colors.HexColor("#6b7280"),
}


def generate_survey_report(survey: Survey) -> str:
    """Render a one-page PDF summary of a coral survey and persist it via the storage backend.

    Returns:
        The storage key of the generated PDF (pass to storage_service.read()
        or, for the S3 backend, storage_service.presigned_url()).
    """
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        title=f"CoralAI Survey Report #{survey.id}",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CoralTitle", parent=styles["Title"], textColor=colors.HexColor("#0f766e")
    )
    heading_style = ParagraphStyle(
        "CoralHeading", parent=styles["Heading2"], textColor=colors.HexColor("#0f766e")
    )
    body_style = styles["BodyText"]

    accent = _SEVERITY_COLORS.get(survey.classification, _SEVERITY_COLORS["Unknown"])

    elements = [
        Paragraph("CoralAI — Coral Bleaching Survey Report", title_style),
        Paragraph(f"Survey #{survey.id} · {survey.created_at.strftime('%Y-%m-%d %H:%M UTC')}", body_style),
        Spacer(1, 0.6 * cm),
    ]

    classification_table = Table(
        [
            ["Classification", survey.classification],
            ["Severity", survey.severity],
            ["Confidence", f"{survey.confidence:.0f}%"],
            ["Risk Level", survey.risk_level or "N/A"],
        ],
        colWidths=[5 * cm, 10 * cm],
    )
    classification_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0fdfa")),
                ("TEXTCOLOR", (1, 0), (1, 0), accent),
                ("FONTNAME", (1, 0), (1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    elements.append(classification_table)
    elements.append(Spacer(1, 0.6 * cm))

    elements.append(Paragraph("Location & Environment", heading_style))
    lat = f"{survey.latitude:.5f}" if survey.latitude is not None else "N/A"
    lon = f"{survey.longitude:.5f}" if survey.longitude is not None else "N/A"
    temp = f"{survey.temperature:.1f} °C" if survey.temperature is not None else "N/A"
    env_table = Table(
        [
            ["Latitude", lat],
            ["Longitude", lon],
            ["Water/Air Temperature", temp],
        ],
        colWidths=[5 * cm, 10 * cm],
    )
    env_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f9fafb")),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    elements.append(env_table)
    elements.append(Spacer(1, 0.6 * cm))

    elements.append(Paragraph("Possible Cause", heading_style))
    elements.append(Paragraph(survey.possible_cause or "Not determined.", body_style))
    elements.append(Spacer(1, 0.4 * cm))

    elements.append(Paragraph("Recommendation", heading_style))
    elements.append(Paragraph(survey.recommendation or "No recommendation available.", body_style))
    elements.append(Spacer(1, 0.8 * cm))

    footer_style = ParagraphStyle("Footer", parent=body_style, fontSize=8, textColor=colors.grey)
    elements.append(
        Paragraph(
            "Generated automatically by CoralAI. Classification produced by an AI model and should "
            "be verified by a qualified marine biologist before use in formal reporting.",
            footer_style,
        )
    )

    doc.build(elements)

    storage_key = f"{settings.S3_REPORT_PREFIX}/survey_{survey.id}_report.pdf"
    get_storage().save(storage_key, buffer.getvalue())
    logger.info("Generated PDF report for survey %s at %s", survey.id, storage_key)
    return storage_key
