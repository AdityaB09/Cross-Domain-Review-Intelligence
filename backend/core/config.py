# backend/core/config.py
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    # DATABASE_URL will come from Render env -> Neon
    # fallback is the local docker-compose Postgres for dev
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@postgres:5432/postgres"
    )

    # allowed_origins controls CORS for the frontend.
    # Comma-separated list. Example:
    # "https://your-frontend.vercel.app,https://localhost:3000"
    allowed_origins: str = os.getenv(
        "ALLOWED_ORIGINS",
        "*"  # dev default, allow everything
    )

    env: str = os.getenv("ENV", "development")

settings = Settings()
