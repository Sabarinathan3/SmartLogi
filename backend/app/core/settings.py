"""
core/settings.py – Environment-variable driven settings via Pydantic BaseSettings.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    app_name: str = "SmartLogi"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True

    # Database
    database_url: str = "sqlite:///./smartlogi.db"

    # Security (placeholder – extend for JWT)
    secret_key: str = "changeme-super-secret-key"
    access_token_expire_minutes: int = 60

    # External APIs (placeholders)
    google_maps_api_key: str = ""
    openweather_api_key: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Singleton instance
settings = Settings()
