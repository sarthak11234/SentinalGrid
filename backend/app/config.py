"""
Application configuration using Pydantic Settings.
Loads values from environment variables / .env file.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # ── Google OAuth ──
    google_client_id: str = ""
    google_client_secret: str = ""

    # ── Google Gemini ──
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"  # default model
    available_models: list[str] = [
        "gemini-3.1-pro",
        "gemini-3-flash",
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
    ]

    # ── Email / SMTP ──
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_pass: str = ""

    # ── WAHA WhatsApp ──
    waha_url: str = "http://localhost:3000"  # WAHA API base URL
    waha_api_key: str = ""  # WAHA API key (if configured)
    waha_session: str = "default"  # WAHA session name

    # ── Database ──
    database_url: str = "sqlite:///./data/sentinalgrid.db"

    # ── App ──
    secret_key: str = "change-me-to-a-random-string"
    frontend_url: str = "http://localhost:8501"
    confidence_threshold: float = 0.7

    model_config = {
        "env_file": (".env", "../.env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance — reads .env once."""
    return Settings()
