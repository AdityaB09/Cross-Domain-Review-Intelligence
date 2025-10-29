# backend/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    allowed_origins: str = "*"
    database_url: str | None = None
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
