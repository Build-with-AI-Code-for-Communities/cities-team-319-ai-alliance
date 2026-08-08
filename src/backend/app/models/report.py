"""Report ORM model — one row per generated PDF report."""
from __future__ import annotations

import datetime as dt

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Report(Base):
    """A generated PDF report tied to a survey."""

    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    survey_id: Mapped[int] = mapped_column(ForeignKey("surveys.id"), nullable=False)
    pdf_path: Mapped[str] = mapped_column(String(512), nullable=False)

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: dt.datetime.now(dt.timezone.utc)
    )

    survey: Mapped["Survey"] = relationship("Survey", back_populates="reports")  # noqa: F821

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Report id={self.id} survey_id={self.survey_id}>"
