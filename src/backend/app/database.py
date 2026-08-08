"""SQLAlchemy engine, session factory, and declarative base."""
from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all ORM models."""


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session and closes it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _sync_missing_columns() -> None:
    """Add columns present on the ORM models but missing from already-existing tables.

    create_all() only creates tables that don't exist yet — it never alters
    existing ones. This keeps an already-deployed database (e.g. Neon) in sync
    with small, additive model changes without needing a full migration tool
    like Alembic for a hackathon-scale project. Only ever adds columns; never
    drops or alters existing ones, so it's safe to run on every startup.
    """
    inspector = inspect(engine)
    for table in Base.metadata.sorted_tables:
        if table.name not in inspector.get_table_names():
            continue  # brand new table, create_all() already built it in full
        existing_columns = {col["name"] for col in inspector.get_columns(table.name)}
        for column in table.columns:
            if column.name in existing_columns:
                continue
            ddl_type = column.type.compile(dialect=engine.dialect)
            logger.info("Migrating: adding column %s.%s (%s)", table.name, column.name, ddl_type)
            with engine.begin() as conn:
                conn.execute(text(f'ALTER TABLE "{table.name}" ADD COLUMN "{column.name}" {ddl_type}'))


def init_db() -> None:
    """Create all tables and sync any additive schema changes. Called on application startup."""
    from app.models import report, survey  # noqa: F401  (ensure models are registered)

    Base.metadata.create_all(bind=engine)
    _sync_missing_columns()
