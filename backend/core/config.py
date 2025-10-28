# backend/core/config.py
import os
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Neon Postgres URL that we inject from Render env
    # fallback is a local Postgres for docker-compose dev
    database_url: str = Field(
        default=os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:postgres@postgres:5432/postgres"
        )
    )

    # Comma-separated list of allowed origins for CORS.
    # Example in Render:
    #   ALLOWED_ORIGINS="https://your-frontend.vercel.app,https://localhost:3000"
    # For dev you can just "*"
    allowed_origins: str = Field(
        default=os.getenv("ALLOWED_ORIGINS", "*")
    )

    # just a flag if you care
    env: str = Field(
        default=os.getenv("ENV", "development")
    )

    class Config:
        # Pydantic Settings v2 still supports env loading automatically,
        # but we're also doing manual os.getenv defaults above so this is mostly FYI.
        env_file = ".env"
        extra = "ignore"

settings = Settings()
