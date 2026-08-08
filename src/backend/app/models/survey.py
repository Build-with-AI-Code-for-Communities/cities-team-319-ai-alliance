"""Survey ORM model — one row per coral image submission."""
from __future__ import annotations

import datetime as dt

from sqlalchemy import JSON, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Survey(Base):
    """A single coral health survey derived from an uploaded image."""

    __tablename__ = "surveys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    image_name: Mapped[str] = mapped_column(String(255), nullable=False)

    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    classification: Mapped[str] = mapped_column(String(64), nullable=False, default="Unknown")
    severity: Mapped[str] = mapped_column(String(64), nullable=False, default="Unknown")
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    possible_cause: Mapped[str | None] = mapped_column(String(512), nullable=True)
    recommendation: Mapped[str | None] = mapped_column(String(512), nullable=True)

    risk_level: Mapped[str | None] = mapped_column(String(32), nullable=True)
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    weather: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: dt.datetime.now(dt.timezone.utc)
    )

    reports: Mapped[list["Report"]] = relationship(  # noqa: F821
        "Report", back_populates="survey", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Survey id={self.id} classification={self.classification!r}>"
