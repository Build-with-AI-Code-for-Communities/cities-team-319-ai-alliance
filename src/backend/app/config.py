"""Application configuration, loaded from environment variables via pydantic-settings."""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Central application settings. Values are sourced from environment / .env file."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- App ---
    APP_NAME: str = "CoralAI"
    ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api"

    # --- CORS ---
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    # --- Database ---
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'coral_ai.db'}"

    # --- Local storage (used when STORAGE_BACKEND=local, and always for the SQLite default) ---
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    REPORT_DIR: Path = BASE_DIR / "reports"
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_IMAGE_TYPES: str = "image/jpeg,image/png,image/webp"
    IMAGE_MAX_DIMENSION: int = 1600

    # --- Object storage (Tier 1 for production; S3-compatible — AWS S3, Cloudflare R2, MinIO, etc.) ---
    STORAGE_BACKEND: str = "local"  # "local" or "s3"
    S3_ENDPOINT_URL: str = ""  # e.g. https://<account_id>.r2.cloudflarestorage.com for Cloudflare R2
    S3_REGION: str = "auto"  # R2 uses "auto"; AWS uses e.g. "us-east-1"
    S3_BUCKET_NAME: str = ""
    S3_ACCESS_KEY_ID: str = ""
    S3_SECRET_ACCESS_KEY: str = ""
    S3_UPLOAD_PREFIX: str = "uploads"
    S3_REPORT_PREFIX: str = "reports"
    S3_PRESIGNED_URL_EXPIRY_SECONDS: int = 3600

    # --- Gemini (Tier 1, required) ---
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # --- Open-Meteo (Tier 1, no key needed) ---
    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1/forecast"
    OPEN_METEO_MARINE_URL: str = "https://marine-api.open-meteo.com/v1/marine"

    # --- NASA (Tier 2, optional) ---
    NASA_API_KEY: str = ""
    NASA_SST_ENABLED: bool = False

    # --- Risk Engine thresholds ---
    RISK_TEMP_WARNING_C: float = 29.5
    RISK_TEMP_CRITICAL_C: float = 30.5

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def allowed_image_types_list(self) -> list[str]:
        return [t.strip() for t in self.ALLOWED_IMAGE_TYPES.split(",") if t.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (loaded once per process)."""
    return Settings()


settings = get_settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.REPORT_DIR.mkdir(parents=True, exist_ok=True)
