# Database Schema

CoralAI uses SQLAlchemy 2.0 with a SQLite database for local development (`src/backend/coral_ai.db`) and is Postgres-ready for production via `DATABASE_URL`.

## ER Diagram

```
┌────────────────────────────┐        ┌───────────────────────────┐
│           surveys           │        │           reports          │
├────────────────────────────┤        ├───────────────────────────┤
│ id               PK INTEGER │◀──┐    │ id              PK INTEGER │
│ image_name          STRING  │   │    │ survey_id  FK ──┘ INTEGER │
│ latitude            FLOAT   │   └────│ pdf_path            STRING │
│ longitude           FLOAT   │        │ created_at        DATETIME │
│ classification       STRING │        └───────────────────────────┘
│ severity             STRING │
│ confidence            FLOAT │        1 survey : N reports
│ possible_cause        STRING│        (a survey can be re-reported)
│ recommendation        STRING│
│ risk_level             STRING│
│ risk_score              FLOAT│
│ temperature              FLOAT│
│ weather                   JSON│
│ created_at            DATETIME│
└────────────────────────────┘
```

## `surveys`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `image_name` | STRING(255) | Storage key (e.g. `uploads/<uuid>.jpg`) — resolves to a local file or S3 object depending on `STORAGE_BACKEND` |
| `latitude` | FLOAT, nullable | From EXIF GPS or browser geolocation |
| `longitude` | FLOAT, nullable | |
| `classification` | STRING(64) | One of: `Healthy`, `Partially Bleached`, `Severely Bleached`, `Dead Coral`, `Unknown` |
| `severity` | STRING(64) | Free-text severity description from Gemini |
| `confidence` | FLOAT | 0–100, from Gemini |
| `possible_cause` | STRING(512), nullable | From Gemini |
| `recommendation` | STRING(512), nullable | From Gemini |
| `risk_level` | STRING(32), nullable | Low / Moderate / High / Critical, from Risk Engine |
| `risk_score` | FLOAT, nullable | 0–100, from Risk Engine |
| `temperature` | FLOAT, nullable | Sea surface temp if available, else air temp |
| `weather` | JSON, nullable | Full weather payload (temperature, wind, SST, source) |
| `created_at` | DATETIME (tz-aware) | UTC timestamp |

## `reports`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `survey_id` | INTEGER FK → `surveys.id` | Cascade-deletes with survey |
| `pdf_path` | STRING(512) | Storage key (e.g. `reports/survey_1_report.pdf`) — resolves to a local file or S3 object depending on `STORAGE_BACKEND` |
| `created_at` | DATETIME (tz-aware) | UTC timestamp |

## Migrations

The hackathon MVP creates tables via `Base.metadata.create_all()` on startup (see `app/database.py: init_db()`) rather than a migration tool, to keep setup to a single command. For a production deployment, introduce **Alembic** to manage schema changes safely against Postgres.
