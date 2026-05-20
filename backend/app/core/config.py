"""
core/config.py – Application-wide constants.
"""

APP_NAME: str = "SmartLogi"
APP_VERSION: str = "1.0.0"
ENVIRONMENT: str = "development"          # "development" | "production"
API_PREFIX: str = "/api/v1"
DEBUG: bool = ENVIRONMENT == "development"
